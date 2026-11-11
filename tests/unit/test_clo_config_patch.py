"""Tests for deploy/loop7/clo-config-patch.py (Loop 7 part 3): only new keys are added, a second run changes nothing, secrets never print."""
import copy
import importlib.util
import io
import json
import os
import contextlib
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("clo_patch", os.path.join(ROOT, "deploy", "loop7", "clo-config-patch.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CID, UID = "C0AAAAAAAAA", "U0BBBBBBBBB"


def base():
    return {
        "agents": {"defaults": {"model": {"primary": "m/x"}}, "entries": {"coo": {"tools": {"agentToAgent": {"send": ["cho"]}}}, "cfo": {}}},
        "tools": {"profile": "messaging", "agentToAgent": {"enabled": True, "allow": ["coo", "cho", "cos", "cfo"]}},
        "channels": {"slack": {"enabled": True, "accounts": {"cfo": {"channels": {"C0CFOCFOCFO": {"enabled": True, "users": [UID]}}}}}},
        "bindings": [{"match": {"channel": "slack", "peer": {"kind": "channel", "id": "C0CFOCFOCFO"}}, "agentId": "cfo"},
                     {"type": "route", "agentId": "cfo", "match": {"channel": "slack", "accountId": "cfo"}}],
        "session": {"reset": {"mode": "daily", "atHour": 4}},
    }


class Patch(unittest.TestCase):
    def test_only_additions_with_slack(self):
        old = base()
        new = mod.apply(old, "/w/clo", "/a/clo", (CID, [UID]))
        self.assertEqual(mod.check_only_additions(old, new), [])
        e = new["agents"]["entries"]["clo"]
        self.assertIs(e["tools"]["fs"]["workspaceOnly"], True)
        self.assertEqual(e["tools"]["agentToAgent"]["send"], ["coo", "cos"])
        self.assertEqual(new["tools"]["agentToAgent"]["allow"][-1], "clo")
        self.assertEqual(new["channels"]["slack"]["accounts"]["clo"]["botToken"]["source"], "env")
        self.assertEqual(new["agents"]["entries"]["coo"], old["agents"]["entries"]["coo"])
        self.assertEqual(len(new["bindings"]), 4)

    def test_no_slack_adds_no_account_or_binding(self):
        new = mod.apply(base(), "/w", "/a")
        self.assertNotIn("clo", new["channels"]["slack"]["accounts"])
        self.assertEqual(len(new["bindings"]), 2)

    def test_second_apply_is_a_no_op(self):
        once = mod.apply(base(), "/w", "/a")
        self.assertIsNone(mod.apply(once, "/w", "/a"))

    def test_a_stray_change_is_caught(self):
        old = base()
        new = mod.apply(old, "/w", "/a", (CID, [UID]))
        new["session"]["reset"]["atHour"] = 5
        self.assertTrue(mod.check_only_additions(old, new))
        new = mod.apply(old, "/w", "/a")
        new["agents"]["entries"]["coo"]["tools"]["agentToAgent"]["send"].append("clo")
        self.assertTrue(mod.check_only_additions(old, new))

    def test_run_writes_backup_masks_ids_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            cfgp, envp = os.path.join(d, "c.json"), os.path.join(d, "ch.env")
            json.dump(base(), open(cfgp, "w"))
            open(envp, "w").write("lifestyle-clo=" + CID + "\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mod.main([cfgp, "--slack", "--channels-env", envp, "--workspace", "/w/clo", "--agent-dir", "/a/clo"])
            self.assertEqual(rc, 0)
            self.assertNotIn(CID, buf.getvalue())
            self.assertNotIn(UID, buf.getvalue())
            self.assertEqual(json.load(open(cfgp + ".pre-clo")), base())
            self.assertIn("clo", json.load(open(cfgp))["agents"]["entries"])
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(mod.main([cfgp, "--slack", "--channels-env", envp]), 0)
            self.assertIn("already", buf.getvalue())

    def test_missing_channel_line_stops(self):
        with tempfile.TemporaryDirectory() as d:
            cfgp, envp = os.path.join(d, "c.json"), os.path.join(d, "ch.env")
            json.dump(base(), open(cfgp, "w"))
            open(envp, "w").write("finance-cfo=C0CFOCFOCFO\n")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mod.main([cfgp, "--slack", "--channels-env", envp]), 1)
            self.assertFalse(os.path.exists(cfgp + ".pre-clo"))


if __name__ == "__main__":
    unittest.main()
