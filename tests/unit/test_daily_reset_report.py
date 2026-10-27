"""Tests for deploy/loop2/vm/daily-reset-report.py (P-36, APR-0090). Runs it with --dry-run against fake agent databases in a temporary HOME.
No OpenClaw, no Slack; the script is read-only and a dry run saves and posts nothing."""
import datetime
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "deploy", "loop2", "vm", "daily-reset-report.py")
AST = datetime.timezone(datetime.timedelta(hours=-4))


def cut_ms():
    now = datetime.datetime.now(AST)
    return int(now.replace(hour=4, minute=0, second=0, microsecond=0).timestamp() * 1000)


class ResetReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.agents = {}
        for a in ("coo", "cho", "cos", "cfo"):
            d = os.path.join(self.tmp, "loop1", "state", "agents", a, "agent")
            os.makedirs(d)
            c = sqlite3.connect(os.path.join(d, "openclaw-agent.sqlite"))
            c.execute("create table session_nodes (session_key text, current_session_id text, entry_json text)")
            c.execute("create table transcript_events (session_id text, created_at integer, event_json text)")
            c.execute("insert into session_nodes values (?,?,?)", ("agent:%s:main" % a, a + "-main-0001", "{}"))
            c.execute("insert into session_nodes values (?,?,?)", ("agent:%s:slack:channel:c1" % a, a + "-slack-0001", "{}"))
            c.commit()
            self.agents[a] = c

    def tearDown(self):
        for c in self.agents.values():
            c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_report(self):
        env = dict(os.environ, HOME=self.tmp)
        env.pop("LIFEOS_ALERT_TARGET", None)
        return subprocess.run([sys.executable, "-I", SCRIPT, "--dry-run"], capture_output=True, text=True, env=env)

    def add_event(self, agent, sid, when_ms, event):
        c = self.agents[agent]
        c.execute("insert into transcript_events values (?,?,?)", (sid, when_ms, json.dumps(event)))
        c.commit()

    def test_no_message_means_reset_pending(self):
        r = self.run_report()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("coo main: coo-main", r.stdout)
        self.assertIn("no message since 04:00, reset pending (normal)", r.stdout)
        self.assertIn("(dry run: nothing saved, nothing posted)", r.stdout)

    def test_first_message_after_04_is_reported(self):
        self.add_event("cho", "cho-slack-0001", cut_ms() + 60000, {"type": "message"})
        out = self.run_report().stdout
        line = [l for l in out.splitlines() if l.startswith("cho slack")][0]
        self.assertIn("first message after 04:00 at", line)

    def test_reset_marker_with_its_reason_is_reported(self):
        self.add_event("coo", "coo-slack-0001", cut_ms() + 60000, {"type": "reset", "reason": "daily"})
        line = [l for l in self.run_report().stdout.splitlines() if l.startswith("coo slack")][0]
        self.assertIn("reset applied", line)
        self.assertIn("(daily)", line)

    def test_dry_run_saves_nothing_and_never_writes_the_databases(self):
        before = {a: c.execute("select count(*) from transcript_events").fetchone()[0] for a, c in self.agents.items()}
        self.run_report()
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "loop1", "reset-check")))
        after = {a: c.execute("select count(*) from transcript_events").fetchone()[0] for a, c in self.agents.items()}
        self.assertEqual(before, after)

    def test_an_unreadable_agent_database_is_reported_not_fatal(self):
        os.remove(os.path.join(self.tmp, "loop1", "state", "agents", "cfo", "agent", "openclaw-agent.sqlite"))
        r = self.run_report()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("cfo: could not read", r.stdout)
        self.assertIn("coo main:", r.stdout)


if __name__ == "__main__":
    unittest.main()
