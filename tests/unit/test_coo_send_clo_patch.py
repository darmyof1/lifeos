"""Tests for deploy/loop7/coo-send-clo-patch.py (APR-0128): one key, backup, idempotent."""
import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("coo_patch", os.path.join(ROOT, "deploy", "loop7", "coo-send-clo-patch.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def base():
    return {"agents": {"entries": {"coo": {"tools": {"agentToAgent": {"send": ["cho", "cos", "cfo"]}}},
                                   "cho": {"tools": {"agentToAgent": {"send": ["coo", "cos"]}}}}},
            "tools": {"agentToAgent": {"allow": ["coo", "cho", "cos", "cfo", "clo"]}}, "session": {"reset": {"atHour": 4}}}


class Patch(unittest.TestCase):
    def test_one_key_changes(self):
        old = base()
        new = mod.apply(old)
        self.assertEqual(new["agents"]["entries"]["coo"]["tools"]["agentToAgent"]["send"], ["cho", "cos", "cfo", "clo"])
        self.assertTrue(mod.only_that_key(old, new))
        self.assertEqual(new["agents"]["entries"]["cho"], old["agents"]["entries"]["cho"])

    def test_second_apply_is_a_no_op(self):
        self.assertIsNone(mod.apply(mod.apply(base())))

    def test_a_second_changed_key_is_caught(self):
        old = base()
        new = mod.apply(old)
        new["session"]["reset"]["atHour"] = 5
        self.assertFalse(mod.only_that_key(old, new))

    def test_run_writes_a_backup_and_second_run_says_so(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.json")
            with open(p, "w") as fh:
                json.dump(base(), fh)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mod.main([p]), 0)
            with open(p + ".pre-coo-clo") as fh:
                self.assertEqual(json.load(fh), base())
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(mod.main([p]), 0)
            self.assertIn("already", buf.getvalue())

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.json")
            with open(p, "w") as fh:
                json.dump(base(), fh)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mod.main([p, "--dry-run"]), 0)
            self.assertFalse(os.path.exists(p + ".pre-coo-clo"))
            with open(p) as fh:
                self.assertEqual(json.load(fh), base())


if __name__ == "__main__":
    unittest.main()
