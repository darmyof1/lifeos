"""Tests for scripts/ops/agent-compact.sh (Loop 7, APR-0126): the COO rules for the CHO, CoS and CFO too. Reuses the fake openclaw command
of test_coo_compact.py. The COO behaviour itself is covered by test_coo_compact.py, which runs through the thin coo-compact.sh wrapper."""
import json, os, shutil, stat, subprocess, tempfile, unittest

import test_coo_compact as base

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "..", "scripts", "ops", "agent-compact.sh")
NOW_MS, MIN = base.NOW_MS, base.MIN


def key(agent):
    return "agent:%s:slack:channel:fake0id" % agent


def sessions(agent, last_ms, tokens, others=()):
    rows = [{"key": key(agent), "updatedAt": last_ms, "lastInteractionAt": last_ms, "totalTokens": tokens},
            {"key": "agent:%s:main" % agent, "updatedAt": NOW_MS, "lastInteractionAt": NOW_MS, "totalTokens": 5}]
    for o in others:
        rows.append({"key": key(o), "updatedAt": NOW_MS, "lastInteractionAt": NOW_MS, "totalTokens": 7})
    return json.dumps({"sessions": rows})


class AgentCompact(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="agent-compact-", dir="/tmp")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin = os.path.join(self.tmp, "fake-openclaw")
        with open(self.bin, "w") as fh:
            fh.write(base.FAKE)
        os.chmod(self.bin, os.stat(self.bin).st_mode | stat.S_IXUSR)
        self.dir = os.path.join(self.tmp, "fake")
        os.mkdir(self.dir)
        self.journal = os.path.join(self.tmp, "journal.md")
        self.token = os.path.join(self.tmp, "token")
        with open(self.token, "w") as fh:
            fh.write("fake-token-value\n")
        self.set_journal([("written", "e1", "seed"), ("pushed", "e1", "sync")])

    def set_sessions(self, agent, last_ms, tokens, others=()):
        with open(os.path.join(self.dir, "sessions.json"), "w") as fh:
            fh.write(sessions(agent, last_ms, tokens, others))
        with open(os.path.join(self.dir, "sessions-after.json"), "w") as fh:
            fh.write(sessions(agent, last_ms, 2100, others))

    def set_journal(self, rows):
        with open(self.journal, "w") as fh:
            fh.write(base.JOURNAL_HEAD + "".join(base.LINE % r for r in rows))

    def run_script(self, *args, now="12:00", log=None, env_extra=None):
        self.log = log or os.path.join(self.tmp, "state", "agent.log")
        env = dict(os.environ, FAKE_DIR=self.dir, AGENT_COMPACT_BIN=self.bin, AGENT_COMPACT_NOW=now, AGENT_COMPACT_NOWMS=str(NOW_MS),
                   AGENT_COMPACT_JOURNAL=self.journal, AGENT_COMPACT_LOG=self.log, AGENT_COMPACT_TOKEN_FILE=self.token, AGENT_COMPACT_ENV="0")
        env.update(env_extra or {})
        r = subprocess.run(["bash", SCRIPT, *args], env=env, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout + r.stderr

    def lines(self):
        return open(self.log).read().splitlines() if os.path.exists(self.log) else []

    def calls(self):
        p = os.path.join(self.dir, "compact-calls.txt")
        return open(p).read().splitlines() if os.path.exists(p) else []

    def test_each_agent_compacts_its_own_channel_session(self):
        for agent in ("cho", "cos", "cfo"):
            shutil.rmtree(self.dir); os.mkdir(self.dir)
            self.set_sessions(agent, NOW_MS - 120 * MIN, 15000, others=[a for a in ("coo", "cho", "cos", "cfo") if a != agent])
            rc, out = self.run_script(agent, "--execute", log=os.path.join(self.tmp, agent + ".log"))
            self.assertEqual(rc, 0, out)
            self.assertEqual(len(self.calls()), 1)
            self.assertTrue(self.calls()[0].startswith("sessions compact %s --agent %s --max-lines 1 --token " % (key(agent), agent)), self.calls()[0])
            self.assertIn("mode=execute result=compacted size_before=15000 size_after=2100 kept_lines=1 agent=%s" % agent, self.lines()[0])

    def test_log_line_names_the_agent_and_has_no_secret_or_text(self):
        self.set_sessions("cho", NOW_MS - 120 * MIN, 15000)
        self.run_script("cho", "--execute")
        text = open(self.log).read()
        self.assertTrue(text.rstrip().endswith("agent=cho"))
        self.assertNotIn("fake0id", text)
        self.assertNotIn("fake-token-value", text)

    def test_default_log_file_is_per_agent(self):
        home = os.path.join(self.tmp, "home")
        self.set_sessions("cfo", NOW_MS - 120 * MIN, 15000)
        rc, out = self.run_script("cfo", "--execute", log="", env_extra={"HOME": home, "AGENT_COMPACT_LOG": ""})
        self.assertEqual(rc, 0, out)
        self.assertTrue(os.path.exists(os.path.join(home, "loop1", "state", "cfo-compact.log")))

    def test_other_agents_channel_session_is_not_used(self):
        self.set_sessions("cos", NOW_MS - 120 * MIN, 15000)       # only a cos channel session exists
        rc, out = self.run_script("cho", "--execute")
        self.assertEqual(rc, 3, out)
        self.assertEqual(self.calls(), [])
        self.assertIn("result=error", self.lines()[0])
        self.assertIn("agent=cho", self.lines()[0])

    def test_window_recent_message_and_waiting_request_rules_apply_to_every_agent(self):
        for agent in ("cho", "cos", "cfo"):
            self.set_sessions(agent, NOW_MS - 120 * MIN, 15000)
            for hm in ("03:30", "05:09"):
                self.assertEqual(self.run_script(agent, "--execute", now=hm)[0], 2, agent + hm)
            self.set_sessions(agent, NOW_MS - 9 * MIN, 15000)
            self.assertEqual(self.run_script(agent, "--execute")[0], 0)
            self.assertIn("result=skipped", self.lines()[-1])
            self.set_sessions(agent, NOW_MS - 120 * MIN, 15000)
            for status in ("requested", "delete-pending-approval"):
                self.set_journal([(status, "e2", "CHO")])
                self.assertEqual(self.run_script(agent, "--execute")[0], 0)
                self.assertIn("CEO request(s) waiting", self.lines()[-1])
            self.set_journal([("written", "e1", "seed")])
        self.assertEqual(self.calls(), [])

    def test_dry_run_default_changes_nothing(self):
        self.set_sessions("cos", NOW_MS - 120 * MIN, 15000)
        rc, out = self.run_script("cos")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.calls(), [])
        self.assertIn("mode=dry-run result=would-compact size=15000", self.lines()[0])

    def test_bad_agent_or_option_exits_64_and_logs_nothing(self):
        for args in ((), ("main",), ("coo2",), ("cho", "--force"), ("--execute",)):
            rc, out = self.run_script(*args)
            self.assertEqual(rc, 64, str(args) + out)
        self.assertEqual(self.lines(), [])


if __name__ == "__main__":
    unittest.main()
