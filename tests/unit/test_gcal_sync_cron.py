"""Tests for scripts/gcal/gcal_sync_cron.sh (APR-0078). A stub Python stands in for the job."""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "scripts", "gcal", "gcal_sync_cron.sh")


@unittest.skipUnless(shutil.which("bash"), "needs bash")
class Cron(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.state = os.path.join(self.home, "loop1", "gcal-sync")
        os.makedirs(self.state)
        self.py = os.path.join(self.tmp, "fakepy")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def stub(self, code, text="summary: pushed 0"):
        with open(self.py, "w") as fh:
            fh.write('#!/bin/sh\necho "%s"\necho "args: $@"\necho "cal=$GCAL_CALENDAR"\nexit %d\n' % (text, code))
        os.chmod(self.py, 0o755)

    def run_cron(self, **extra):
        env = dict(os.environ, HOME=self.home, LIFEOS_SYNC_PY=self.py, **extra)
        return subprocess.run(["bash", SCRIPT], capture_output=True, text=True, env=env)

    def log(self):
        with open(os.path.join(self.state, "sync.log")) as fh:
            return fh.read()

    def test_logs_one_block_and_passes_the_exit_code(self):
        self.stub(3, "paused")
        with open(os.path.join(self.state, "env"), "w") as fh:
            fh.write("GCAL_CALENDAR=cal-from-env\n")
        r = self.run_cron()
        self.assertEqual(r.returncode, 3)
        log = self.log()
        self.assertIn("exit 3", log)
        self.assertIn("paused", log)
        self.assertIn("--state-dir " + self.state, log)
        self.assertIn("cal=cal-from-env", log)

    def test_loads_the_openclaw_environment_first(self):
        self.stub(0)
        with open(self.py, "w") as fh:
            fh.write('#!/bin/sh\necho "oc=$OPENCLAW_TEST_VAR"\nexit 0\n')
        with open(os.path.join(self.home, "loop1", "env.sh"), "w") as fh:
            fh.write("OPENCLAW_TEST_VAR=from-env-sh\n")
        self.assertEqual(self.run_cron().returncode, 0)
        self.assertIn("oc=from-env-sh", self.log())

    def test_works_without_env_sh(self):
        self.stub(0)
        self.assertEqual(self.run_cron().returncode, 0)

    def test_extra_args_and_second_run_appends(self):
        self.stub(0)
        self.run_cron(LIFEOS_SYNC_ARGS="--dry-run")
        self.run_cron()
        log = self.log()
        self.assertEqual(log.count("=== "), 2)
        self.assertIn("--dry-run", log)

    def test_deletes_are_off_by_default(self):
        self.stub(0)
        self.run_cron()
        self.assertNotIn("--allow-deletes", self.log())

    def test_deletes_only_with_the_exact_setting_1(self):
        self.stub(0)
        with open(os.path.join(self.state, "env"), "w") as fh:
            fh.write("GCAL_ALLOW_DELETES=yes\n")
        self.run_cron()
        self.assertNotIn("--allow-deletes", self.log())
        with open(os.path.join(self.state, "env"), "w") as fh:
            fh.write("GCAL_ALLOW_DELETES=1\n")
        self.run_cron()
        self.assertEqual(self.log().count("--allow-deletes"), 1)

    def test_log_is_trimmed(self):
        self.stub(0)
        with open(os.path.join(self.state, "sync.log"), "w") as fh:
            fh.write("old\n" * 2100)
        self.run_cron()
        n = len(self.log().splitlines())
        self.assertLessEqual(n, 1510)
        self.assertIn("exit 0", self.log())


@unittest.skipUnless(shutil.which("bash"), "needs bash")
class Notify(unittest.TestCase):
    """The optional WirePusher notification: counts only, only when Google changed, never breaks the job."""
    SUMMARY = "summary: pushed %d, conflict 0, failed 0 (final 0), deleted %d, skipped 0, reconciled 0 (display full)"

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.state = os.path.join(self.home, "loop1", "gcal-sync")
        os.makedirs(self.state)
        self.py = os.path.join(self.tmp, "fakepy")
        self.curl = os.path.join(self.tmp, "fakecurl")
        self.calls = os.path.join(self.tmp, "curl-calls.txt")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def stub(self, pushed, deleted=0, code=0):
        with open(self.py, "w") as fh:
            fh.write('#!/bin/sh\necho "%s"\nexit %d\n' % (self.SUMMARY % (pushed, deleted), code))
        os.chmod(self.py, 0o755)

    def fake_curl(self, http="200", code=0):
        with open(self.curl, "w") as fh:
            fh.write('#!/bin/sh\necho "$@" >>"%s"\nprintf "%s"\nexit %d\n' % (self.calls, http, code))
        os.chmod(self.curl, 0o755)

    def settings(self, with_id=True):
        with open(os.path.join(self.state, "env"), "w") as fh:
            fh.write("GCAL_CALENDAR=cal-from-env\n")
            if with_id:
                fh.write("WIREPUSHER_ID=secret-id-123\n")

    def run_cron(self):
        env = dict(os.environ, HOME=self.home, LIFEOS_SYNC_PY=self.py, LIFEOS_CURL=self.curl)
        return subprocess.run(["bash", SCRIPT], capture_output=True, text=True, env=env)

    def log(self):
        with open(os.path.join(self.state, "sync.log")) as fh:
            return fh.read()

    def sent(self):
        if not os.path.exists(self.calls):
            return []
        with open(self.calls) as fh:
            return fh.read().splitlines()

    def test_no_id_no_notification(self):
        self.stub(2)
        self.fake_curl()
        self.settings(with_id=False)
        self.assertEqual(self.run_cron().returncode, 0)
        self.assertEqual(self.sent(), [])

    def test_nothing_changed_no_notification(self):
        self.stub(0, 0)
        self.fake_curl()
        self.settings()
        self.assertEqual(self.run_cron().returncode, 0)
        self.assertEqual(self.sent(), [])

    def test_pushed_events_send_one_notification_with_counts_only(self):
        self.stub(2, 1)
        self.fake_curl()
        self.settings()
        self.assertEqual(self.run_cron().returncode, 0)
        sent = self.sent()
        self.assertEqual(len(sent), 1)
        self.assertIn("https://wirepusher.com/send", sent[0])
        self.assertIn("message=Calendar pushed to Google: 2 pushed, 1 deleted.", sent[0])
        self.assertIn("id=secret-id-123", sent[0])
        self.assertIn("notify: WirePusher HTTP 200", self.log())

    def test_the_id_never_reaches_the_log(self):
        self.stub(1)
        self.fake_curl()
        self.settings()
        self.run_cron()
        self.assertNotIn("secret-id-123", self.log())

    def test_a_failed_notification_does_not_change_the_exit_code(self):
        self.stub(1, 0, code=0)
        self.fake_curl(http="000", code=7)
        self.settings()
        self.assertEqual(self.run_cron().returncode, 0)
        self.assertIn("notify: WirePusher HTTP 000", self.log())

    def test_the_job_exit_code_is_kept_when_it_notifies(self):
        self.stub(1, 0, code=3)
        self.fake_curl()
        self.settings()
        self.assertEqual(self.run_cron().returncode, 3)


if __name__ == "__main__":
    unittest.main()
