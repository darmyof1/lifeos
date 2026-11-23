"""APR-0143: requireMentionInBotThreads false on the five Slack accounts: the patch script, the clo patch, the health line, the guide."""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATCH = os.path.join(ROOT, "deploy", "after-loop7", "bot-thread-mention-patch.py")
HC = os.path.join(ROOT, "deploy", "loop1", "health-check.py")
GUIDE = os.path.join(ROOT, "guides", "slack-new-agent-app.md")
CLO = os.path.join(ROOT, "deploy", "loop7", "clo-config-patch.py")
KEY = "requireMentionInBotThreads"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cfg():
    acc = {a: {"enabled": True, "mode": "socket", "botToken": {"source": "env", "id": "DUMMY"},
               "channels": {"C0DUMMY": {"enabled": True, "users": ["U0DUMMY"]}}} for a in ("default", "cho", "cos", "cfo", "clo")}
    return {"channels": {"slack": {"enabled": True, "accounts": acc}}, "agents": {"entries": {"coo": {}}}}


class Patch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load(PATCH, "btm")

    def test_sets_exactly_five_keys_to_false(self):
        c = cfg()
        new, changed = self.m.apply(c)
        self.assertEqual(sorted(changed), sorted(["default", "cho", "cos", "cfo", "clo"]))
        for a in changed:
            self.assertIs(new["channels"]["slack"]["accounts"][a][KEY], False)
        added, removed, other = self.m.diff_paths(c, new)
        self.assertEqual(len(added), 5)
        self.assertEqual((removed, other), ([], []))
        self.assertIn("/channels/slack/accounts/coo/" + KEY, added)

    def test_missing_account_refused(self):
        c = cfg()
        del c["channels"]["slack"]["accounts"]["cho"]
        with self.assertRaises(ValueError):
            self.m.apply(c)

    def test_script_backup_second_run_and_output_has_no_ids(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "openclaw.json")
            c = cfg()
            with open(p, "w") as fh:
                json.dump(c, fh)
            r = subprocess.run([sys.executable, PATCH, p, "--dry-run"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            self.assertIn("Dry run only", r.stdout)
            self.assertFalse(os.path.exists(p + ".pre-mentionthreads"))
            r = subprocess.run([sys.executable, PATCH, p], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(r.stdout.count("= false"), 5)
            for bad in ("DUMMY", "C0DUMMY", "U0DUMMY"):
                self.assertNotIn(bad, r.stdout)
            with open(p + ".pre-mentionthreads") as fh:
                self.assertEqual(json.load(fh), c)
            with open(p) as fh:
                new = json.load(fh)
            before = copy.deepcopy(c)
            for a in new["channels"]["slack"]["accounts"].values():
                del a[KEY]
            self.assertEqual(new, before)
            r = subprocess.run([sys.executable, PATCH, p], capture_output=True, text=True)
            self.assertIn("already set", r.stdout)


class CloPatch(unittest.TestCase):
    def test_new_account_carries_the_key(self):
        with open(CLO) as fh:
            self.assertIn('"requireMentionInBotThreads": False', fh.read())


class HealthLine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ast
        with open(HC) as fh:
            tree = ast.parse(fh.read())
        body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "bot_thread_mention_status"]
        ns = {}
        exec(compile(ast.Module(body=body, type_ignores=[]), HC, "exec"), ns)
        cls.f = staticmethod(ns["bot_thread_mention_status"])

    EXP = ["default", "cho", "cos", "cfo", "clo"]

    def test_pass_when_all_five_false(self):
        accs = {a: {KEY: False} for a in self.EXP}
        self.assertEqual(self.f(accs, self.EXP)[0], "PASS")

    def test_warn_when_unset_or_true(self):
        accs = {a: {KEY: False} for a in self.EXP}
        accs["cfo"] = {}
        accs["clo"] = {KEY: True}
        st, det = self.f(accs, self.EXP)
        self.assertEqual(st, "WARN")
        self.assertIn("cfo", det)
        self.assertIn("clo", det)
        self.assertIn("3 of 5", det)

    def test_warn_when_an_account_is_missing(self):
        self.assertEqual(self.f({}, self.EXP)[0], "WARN")

    def test_the_line_is_in_the_health_check_and_prints_no_other_value(self):
        with open(HC) as fh:
            src = fh.read()
        self.assertIn("slack bot-thread mention: requireMentionInBotThreads false for 5 of 5 accounts", src)


class Guide(unittest.TestCase):
    def test_guide_section(self):
        with open(GUIDE) as fh:
            t = fh.read()
        for needle in ("message.channels", "message.groups", "channels:history", "groups:history", "app_mention",
                       "requireMentionInBotThreads", "APR-0143", "APR-0063", "top-level message still needs the mention"):
            self.assertIn(needle, t)
        self.assertEqual(t.count("## 8. Thread replies without a mention"), 1)


if __name__ == "__main__":
    unittest.main()
