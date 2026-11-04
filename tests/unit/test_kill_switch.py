"""Unit tests for scripts/ops/kill-switch.sh (APR-0112) with a fake systemctl and a fake crontab in a temp HOME."""
import os, stat, subprocess, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "scripts", "ops", "kill-switch.sh")
CAL = '*/5 * * * * LIFEOS_SYNC_ARGS="--require-ceo-ledger $HOME/a --require-ceo-ledger $HOME/b" bash $HOME/lifeos-ro/scripts/gcal/gcal_sync_cron.sh'
STRESS = "0 */6 * * * /usr/bin/stress-ng --cpu 1 --timeout 30m > /dev/null 2>&1"
RESET = "0 5 * * * bash $HOME/loop1/daily-reset-report.sh >> $HOME/loop1/reset-check/cron.out 2>&1"
FAKE_CRONTAB = """#!/bin/bash
F="$HOME/fake.crontab"
if [ "$1" = "-l" ]; then [ -f "$F" ] && cat "$F" || { echo "no crontab for x" >&2; exit 1; }; exit 0; fi
if [ "$1" = "-" ]; then cat > "$F.tmp" && mv "$F.tmp" "$F"; exit 0; fi
exit 2
"""
FAKE_SYSTEMCTL = """#!/bin/bash
S="$HOME/gw.state"; echo "$@" >> "$HOME/systemctl.calls"
case "$*" in
  "--user is-active "*) cat "$S" 2>/dev/null || echo inactive; [ "$(cat "$S" 2>/dev/null)" = active ];;
  "--user stop "*) echo inactive > "$S";;
  "--user start "*) echo active > "$S";;
  *) exit 2;;
esac
"""


class KillSwitchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = os.path.join(self.tmp.name, "home")
        self.bin = os.path.join(self.tmp.name, "bin")
        os.makedirs(os.path.join(self.home, "loop1"))
        os.makedirs(self.bin)
        for name, body in (("crontab", FAKE_CRONTAB), ("systemctl", FAKE_SYSTEMCTL)):
            p = os.path.join(self.bin, name)
            with open(p, "w") as fh:
                fh.write(body)
            os.chmod(p, 0o755)
        self.crontab(["# header", STRESS, CAL, RESET])
        self.gateway("active")

    def crontab(self, lines):
        with open(os.path.join(self.home, "fake.crontab"), "w") as fh:
            fh.write("\n".join(lines) + "\n")

    def cron_text(self):
        with open(os.path.join(self.home, "fake.crontab")) as fh:
            return fh.read()

    def gateway(self, state):
        with open(os.path.join(self.home, "gw.state"), "w") as fh:
            fh.write(state + "\n")

    def gw(self):
        with open(os.path.join(self.home, "gw.state")) as fh:
            return fh.read().strip()

    def calls(self):
        p = os.path.join(self.home, "systemctl.calls")
        if not os.path.exists(p):
            return ""
        with open(p) as fh:
            return fh.read()

    def run_ks(self, *args):
        env = {"HOME": self.home, "PATH": self.bin + ":/usr/bin:/bin", "KS_SERVICE": "fake-gateway"}
        r = subprocess.run(["bash", SCRIPT, *args], env=env, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout + r.stderr

    marker = property(lambda self: os.path.join(self.home, "loop1", "kill-switch.marker"))

    def test_default_is_a_dry_run_and_changes_nothing(self):
        before = self.cron_text()
        for args in ((), ("--restore",)):
            rc, out = self.run_ks(*args)
            self.assertIn("dry run", out)
        rc, out = self.run_ks()
        self.assertEqual(rc, 0)
        self.assertIn("would run: pause_cron", out)
        self.assertIn("would run: systemctl --user stop fake-gateway", out)
        self.assertEqual(self.cron_text(), before)
        self.assertEqual(self.gw(), "active")
        self.assertFalse(os.path.exists(self.marker))
        self.assertNotIn("stop", self.calls())

    def test_execute_pauses_only_the_calendar_line_and_stops_the_gateway(self):
        before = self.cron_text()
        rc, out = self.run_ks("--execute")
        self.assertEqual(rc, 0, out)
        after = self.cron_text()
        self.assertEqual(self.gw(), "inactive")
        b, a = before.splitlines(), after.splitlines()
        self.assertEqual(len(a), len(b))
        changed = [i for i, (x, y) in enumerate(zip(b, a)) if x != y]
        self.assertEqual(len(changed), 1)
        self.assertEqual(a[changed[0]], "#" + b[changed[0]])
        self.assertIn(STRESS, a)
        self.assertIn(RESET, a)
        self.assertIn("check: calendar cron line paused", out)
        self.assertIn("check: gateway stopped", out)

    def test_marker_and_crontab_copy_are_mode_600(self):
        self.run_ks("--execute")
        self.assertEqual(stat.S_IMODE(os.stat(self.marker).st_mode), 0o600)
        copies = [f for f in os.listdir(os.path.join(self.home, "loop1")) if f.startswith("kill-switch-crontab.")]
        self.assertEqual(len(copies), 1)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.join(self.home, "loop1", copies[0])).st_mode), 0o600)

    def test_restore_gives_back_the_same_crontab_byte_for_byte_and_starts_the_gateway(self):
        before = self.cron_text()
        self.run_ks("--execute")
        rc, out = self.run_ks("--restore", "--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.cron_text(), before)
        self.assertEqual(self.gw(), "active")
        self.assertIn("crontab identical", out)
        self.assertFalse(os.path.exists(self.marker))

    def test_execute_twice_is_refused_while_engaged(self):
        self.run_ks("--execute")
        rc, out = self.run_ks("--execute")
        self.assertEqual(rc, 1)
        self.assertIn("already engaged", out)

    def test_restore_without_a_marker_does_nothing(self):
        before = self.cron_text()
        rc, out = self.run_ks("--restore", "--execute")
        self.assertEqual(rc, 1)
        self.assertIn("nothing to restore", out)
        self.assertEqual(self.cron_text(), before)
        self.assertEqual(self.gw(), "active")

    def test_restore_dry_run_changes_nothing(self):
        self.run_ks("--execute")
        paused = self.cron_text()
        rc, out = self.run_ks("--restore")
        self.assertEqual(rc, 0)
        self.assertIn("dry run", out)
        self.assertEqual(self.cron_text(), paused)
        self.assertEqual(self.gw(), "inactive")
        self.assertTrue(os.path.exists(self.marker))

    def test_a_cron_line_the_suites_already_paused_stays_paused_after_restore(self):
        self.crontab(["# header", STRESS, "#" + CAL, RESET])
        before = self.cron_text()
        rc, out = self.run_ks("--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.cron_text(), before)
        self.assertIn("already paused", out)
        rc, out = self.run_ks("--restore", "--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.cron_text(), before)
        self.assertEqual(self.gw(), "active")

    def test_gateway_already_stopped_is_not_started_by_the_restore(self):
        self.gateway("inactive")
        self.run_ks("--execute")
        self.run_ks("--restore", "--execute")
        self.assertEqual(self.gw(), "inactive")
        self.assertNotIn("start", self.calls())

    def test_no_calendar_line_or_two_lines_stop_before_any_change(self):
        for lines in (["# header", STRESS], ["# header", CAL, CAL], ["# header", CAL, "#" + CAL]):
            self.crontab(lines)
            before = self.cron_text()
            rc, out = self.run_ks("--execute")
            self.assertEqual(rc, 1, lines)
            self.assertEqual(self.cron_text(), before)
            self.assertEqual(self.gw(), "active")
            self.assertFalse(os.path.exists(self.marker))

    def test_no_crontab_at_all_stops(self):
        os.unlink(os.path.join(self.home, "fake.crontab"))
        rc, out = self.run_ks("--execute")
        self.assertEqual(rc, 1)
        self.assertEqual(self.gw(), "active")

    def test_nothing_is_deleted_and_no_secrets_are_printed(self):
        os.makedirs(os.path.join(self.home, "loop1", "ceo-ledger"))
        with open(os.path.join(self.home, "loop1", "ceo-slack-id"), "w") as fh:
            fh.write("fake-ceo-id-123\n")
        with open(os.path.join(self.home, "loop1", "gateway-token"), "w") as fh:
            fh.write("tok-secret-123\n")
        rc, out1 = self.run_ks("--execute")
        rc, out2 = self.run_ks("--restore", "--execute")
        for secret in ("fake-ceo-id-123", "tok-secret-123"):
            self.assertNotIn(secret, out1 + out2)
        left = sorted(os.listdir(os.path.join(self.home, "loop1")))
        for keep in ("ceo-ledger", "ceo-slack-id", "gateway-token"):
            self.assertIn(keep, left)

    def test_unknown_option_is_refused(self):
        rc, out = self.run_ks("--force")
        self.assertEqual(rc, 2)
        self.assertEqual(self.gw(), "active")


if __name__ == "__main__":
    unittest.main()
