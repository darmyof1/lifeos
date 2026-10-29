"""Unit tests for ceo-ledger.py. Run with the unit tests (tests/unit)"""
import datetime, hashlib, importlib.util, json, os, stat, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.join(ROOT, "deploy", "loop3", "vm")
spec = importlib.util.spec_from_file_location("ceo_ledger", os.path.join(HERE, "ceo-ledger.py"))
cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
T = datetime.datetime(2026, 10, 28, 1, 2, 3, tzinfo=datetime.timezone.utc)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.path = os.path.join(self.tmp, "led", "scenario-ledger.jsonl")

    def test_line_format_and_hash(self):
        o = json.loads(cl.make_line("r1", "seed-3", "Yes, I approve", T))
        self.assertEqual(list(o), ["time", "run", "event", "channel", "sender", "text_sha256"])
        self.assertEqual((o["time"], o["run"], o["event"], o["channel"], o["sender"]), ("2026-10-28T01:02:03Z", "r1", "seed-3", "cli", "CEO"))
        self.assertEqual(o["text_sha256"], hashlib.sha256(b"Yes, I approve").hexdigest())

    def test_append_only_and_modes(self):
        cl.append(self.path, "r1", "seed-3", "a", T); cl.append(self.path, "r2", "seed-3", "b", T)
        lines = open(self.path).read().splitlines()
        self.assertEqual([json.loads(l)["run"] for l in lines], ["r1", "r2"])
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(self.path)).st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o600)

    def test_requires_run_and_event(self):
        for a in (("", "e"), ("r", "")):
            with self.assertRaises(ValueError): cl.append(self.path, a[0], a[1], "t", T)

    def test_command_line(self):
        env = dict(os.environ, CEO_LEDGER=self.path)
        r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "ceo-ledger.py"), "append", "r9", "seed-3", "text"], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0); self.assertEqual(json.loads(open(self.path).read())["run"], "r9")
        self.assertNotEqual(subprocess.run([sys.executable, "-B", os.path.join(HERE, "ceo-ledger.py")], env=env, capture_output=True).returncode, 0)

    def test_line_is_accepted_by_the_push_job_check(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts", "gcal"))
        import gcal_sync as gs
        cl.append(self.path, "r3", "seed-3", "t", T)
        e = gs.Entry(3, "n", "s", "e", "deleted", "r3", "seed-3", "CEO")
        self.assertTrue(gs.ceo_approval_recorded(self.path, e))
        self.assertFalse(gs.ceo_approval_recorded(self.path, gs.Entry(3, "n", "s", "e", "deleted", "r4", "seed-3", "CEO")))


if __name__ == "__main__":
    unittest.main()
