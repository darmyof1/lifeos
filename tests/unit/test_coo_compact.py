"""Tests for scripts/ops/coo-compact.sh (Loop 6, APR-0121): a fake openclaw command, a throwaway journal and log. No real session, no real data."""
import json, os, shutil, stat, subprocess, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "..", "scripts", "ops", "coo-compact.sh")

KEY = "agent:coo:slack:channel:fake0id"
NOW_MS = 1_800_000_000_000
MIN = 60_000

FAKE = r"""#!/usr/bin/env bash
# fake openclaw: "sessions --all-agents --json" lists sessions from $FAKE_DIR/sessions.json (tokens drop after a compact);
# "sessions compact KEY ..." records the call and answers like the real command.
D="$FAKE_DIR"
if [ "$1" = sessions ] && [ "$2" = compact ]; then
  echo "$@" >>"$D/compact-calls.txt"
  if [ -f "$D/compact-output.txt" ]; then cat "$D/compact-output.txt"; exit "$(cat "$D/compact-exit.txt" 2>/dev/null || echo 0)"; fi
  touch "$D/compacted"
  echo "Compacted session $3 (kept 1 lines)."
  exit 0
fi
if [ "$1" = sessions ]; then
  if [ -f "$D/compacted" ]; then cat "$D/sessions-after.json"; else cat "$D/sessions.json"; fi
  exit 0
fi
exit 1
"""

JOURNAL_HEAD = ("# Calendar journal - SYNTHETIC\nOnly the CoS writes here.\n\n"
                "name | start | end | status | run ID | event ID | requested by\n")
LINE = "CHO - Workout - 10262026-0001 | 2026-10-26 07:00 | 2026-10-26 08:00 | %s | r1 | %s | %s\n"


def sessions_json(last_ms, tokens, extra=()):
    rows = [{"key": KEY, "updatedAt": last_ms, "lastInteractionAt": last_ms, "totalTokens": tokens},
            {"key": "agent:coo:explicit:some-run", "updatedAt": NOW_MS, "lastInteractionAt": NOW_MS, "totalTokens": 5},
            {"key": "agent:cfo:main", "updatedAt": NOW_MS, "lastInteractionAt": NOW_MS, "totalTokens": 7}]
    rows.extend(extra)
    return json.dumps({"count": len(rows), "sessions": rows})


class CompactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="coo-compact-", dir="/tmp")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin = os.path.join(self.tmp, "fake-openclaw")
        with open(self.bin, "w") as fh:
            fh.write(FAKE)
        os.chmod(self.bin, os.stat(self.bin).st_mode | stat.S_IXUSR)
        self.dir = os.path.join(self.tmp, "fake")
        os.mkdir(self.dir)
        self.log = os.path.join(self.tmp, "state", "coo-compact.log")
        self.journal = os.path.join(self.tmp, "journal.md")
        self.token = os.path.join(self.tmp, "token")
        with open(self.token, "w") as fh:
            fh.write("fake-token-value\n")
        self.set_sessions(NOW_MS - 120 * MIN, 15000)
        self.set_journal([("written", "e1", "seed"), ("pushed", "e1", "sync")])

    def set_sessions(self, last_ms, tokens, extra=()):
        with open(os.path.join(self.dir, "sessions.json"), "w") as fh:
            fh.write(sessions_json(last_ms, tokens, extra))
        with open(os.path.join(self.dir, "sessions-after.json"), "w") as fh:
            fh.write(sessions_json(last_ms, 2100, extra))

    def set_journal(self, rows):
        with open(self.journal, "w") as fh:
            fh.write(JOURNAL_HEAD + "".join(LINE % r for r in rows))

    def run_script(self, *args, now="12:00"):
        env = dict(os.environ, FAKE_DIR=self.dir, COO_COMPACT_BIN=self.bin, COO_COMPACT_NOW=now, COO_COMPACT_NOWMS=str(NOW_MS),
                   COO_COMPACT_JOURNAL=self.journal, COO_COMPACT_LOG=self.log, COO_COMPACT_TOKEN_FILE=self.token,
                   COO_COMPACT_ENV="0")
        r = subprocess.run(["bash", SCRIPT, *args], env=env, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout + r.stderr

    def log_lines(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log) as fh:
            return fh.read().splitlines()

    def calls(self):
        p = os.path.join(self.dir, "compact-calls.txt")
        if not os.path.exists(p):
            return []
        with open(p) as fh:
            return fh.read().splitlines()

    # --- the rules
    def test_window_refused_with_exit_2(self):
        for hm in ("03:30", "04:00", "05:09"):
            rc, out = self.run_script("--execute", now=hm)
            self.assertEqual(rc, 2, hm + out)
        self.assertEqual(self.calls(), [])
        self.assertTrue(all("result=refused" in x for x in self.log_lines()))
        self.assertEqual(len(self.log_lines()), 3)

    def test_window_edges_are_open(self):
        for hm in ("03:29", "05:10", "05:25"):
            rc, out = self.run_script("--execute", now=hm)
            self.assertEqual(rc, 0, hm + out)
        self.assertEqual(len(self.calls()), 3)

    def test_recent_message_skipped(self):
        self.set_sessions(NOW_MS - 9 * MIN, 15000)
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.calls(), [])
        self.assertIn("result=skipped", self.log_lines()[0])
        self.assertIn("message 9 min ago", self.log_lines()[0])

    def test_message_exactly_ten_minutes_old_is_compacted(self):
        self.set_sessions(NOW_MS - 10 * MIN, 15000)
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.calls()), 1)

    def test_waiting_request_skipped(self):
        for status in ("requested", "delete-pending-approval"):
            self.set_journal([("written", "e1", "seed"), (status, "e2", "CHO")])
            rc, out = self.run_script("--execute")
            self.assertEqual(rc, 0, out)
            self.assertIn("1 CEO request(s) waiting", self.log_lines()[-1])
        self.assertEqual(self.calls(), [])

    def test_answered_request_does_not_block(self):
        self.set_journal([("delete-pending-approval", "e2", "CHO"), ("deleted", "e2", "sync")])
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.calls()), 1)

    def test_unreadable_journal_skips(self):
        os.remove(self.journal)
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.calls(), [])
        self.assertIn("journal unreadable", self.log_lines()[0])

    # --- normal run and dry run
    def test_normal_run_logs_sizes_and_uses_the_h23_command(self):
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.calls()), 1)
        call = self.calls()[0]
        self.assertTrue(call.startswith("sessions compact %s --agent coo --max-lines 1 --token " % KEY), call)
        lines = self.log_lines()
        self.assertEqual(len(lines), 1)
        self.assertIn("mode=execute result=compacted size_before=15000 size_after=2100 kept_lines=1", lines[0])
        self.assertRegex(lines[0], r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d AST ")

    def test_log_has_no_secret_session_id_or_text(self):
        self.run_script("--execute")
        with open(self.log) as fh:
            text = fh.read()
        self.assertNotIn("fake0id", text)
        self.assertNotIn("fake-token-value", text)

    def test_dry_run_is_the_default_and_changes_nothing(self):
        rc, out = self.run_script()
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.calls(), [])
        self.assertFalse(os.path.exists(os.path.join(self.dir, "compacted")))
        self.assertEqual(len(self.log_lines()), 1)
        self.assertIn("mode=dry-run result=would-compact size=15000", self.log_lines()[0])

    # --- errors
    def test_no_channel_session_is_an_error(self):
        with open(os.path.join(self.dir, "sessions.json"), "w") as fh:
            fh.write(json.dumps({"sessions": [{"key": "agent:coo:main"}]}))
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 3, out)
        self.assertIn("result=error", self.log_lines()[0])

    def test_two_channel_sessions_is_an_error(self):
        self.set_sessions(NOW_MS - 120 * MIN, 15000, extra=[{"key": "agent:coo:slack:channel:other", "updatedAt": 1, "totalTokens": 1}])
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 3, out)
        self.assertEqual(self.calls(), [])

    def test_failed_compact_is_an_error_and_is_logged(self):
        with open(os.path.join(self.dir, "compact-output.txt"), "w") as fh:
            fh.write("Error: gateway not reachable for channel:ABC123\n")
        with open(os.path.join(self.dir, "compact-exit.txt"), "w") as fh:
            fh.write("1")
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 3, out)
        self.assertIn("result=error", self.log_lines()[0])
        self.assertNotIn("ABC123", self.log_lines()[0])

    def test_no_compaction_needed_is_logged_as_such(self):
        with open(os.path.join(self.dir, "compact-output.txt"), "w") as fh:
            fh.write("No compaction needed for session x.\n")
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 0, out)
        self.assertIn("result=no-compaction-needed", self.log_lines()[0])

    def test_size_after_unknown_when_the_token_count_is_not_fresh(self):
        rows = json.loads(sessions_json(NOW_MS - 120 * MIN, 15000))
        rows["sessions"][0]["totalTokens"] = None
        rows["sessions"][0]["totalTokensFresh"] = False
        with open(os.path.join(self.dir, "sessions-after.json"), "w") as fh:
            fh.write(json.dumps(rows))
        rc, out = self.run_script("--execute")
        self.assertEqual(rc, 0, out)
        self.assertIn("size_before=15000 size_after=unknown kept_lines=1", self.log_lines()[0])

    def test_bad_option_exits_64(self):
        rc, out = self.run_script("--force")
        self.assertEqual(rc, 64)
        self.assertEqual(self.log_lines(), [])


if __name__ == "__main__":
    unittest.main()
