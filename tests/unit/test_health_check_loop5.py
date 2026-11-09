"""Tests for the health-check lines added in Loop 5 (APR-0119): the gate plugin in shadow mode, and the calendar policy values.
The functions are extracted with ast because health-check.py runs on import."""
import ast
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HC = os.path.join(ROOT, "deploy", "loop1", "health-check.py")


def extract(path, names):
    with open(path) as fh:
        tree = ast.parse(fh.read())
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), path, "exec"), ns)
    return ns


NS = extract(HC, {"gate_plugin_status", "policy_value_status", "policy_line"})
gate, pvs, pline = NS["gate_plugin_status"], NS["policy_value_status"], NS["policy_line"]
ENABLED = "Gate plugin\nid: gate-plugin\nStatus: enabled\nCapability mode: none\n"


class GatePlugin(unittest.TestCase):
    def test_shadow_passes(self):
        self.assertEqual(gate(ENABLED, "shadow")[0], "PASS")
        self.assertEqual(gate(ENABLED, None)[0], "PASS")      # no config key: the plugin default is shadow
        self.assertEqual(gate(ENABLED, "")[0], "PASS")

    def test_enforce_warns(self):
        st, det = gate(ENABLED, "enforce")
        self.assertEqual(st, "WARN")
        self.assertIn("ENFORCE", det)

    def test_unknown_mode_warns(self):
        self.assertEqual(gate(ENABLED, "loud")[0], "WARN")

    def test_missing_fails(self):
        self.assertEqual(gate("", "shadow")[0], "FAIL")
        self.assertEqual(gate("Plugin not found: gate-plugin", "shadow")[0], "FAIL")
        self.assertEqual(gate(None, "shadow")[0], "FAIL")

    def test_not_enabled_fails(self):
        self.assertEqual(gate("id: gate-plugin\nStatus: disabled\n", "shadow")[0], "FAIL")


class PolicyLines(unittest.TestCase):
    def test_allowed_values_are_info(self):
        self.assertEqual(pvs("busy", ("busy", "full")), ("INFO", "busy"))
        self.assertEqual(pvs("full", ("busy", "full")), ("INFO", "full"))
        self.assertEqual(pvs("test", ("test", "real")), ("INFO", "test"))
        self.assertEqual(pvs("real", ("test", "real")), ("INFO", "real"))

    def test_other_values_warn(self):
        for v in (None, "", "loud", "BUSY"):
            self.assertEqual(pvs(v, ("busy", "full"))[0], "WARN", v)

    def test_policy_line_reader(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "calendar.yaml")
            with open(p, "w") as fh:
                fh.write('x:\n  privacy_display: nested\nprivacy_display: "full"   # comment\ncalendar_target: test\n')
            self.assertEqual(pline(p, "privacy_display"), "full")
            self.assertEqual(pline(p, "calendar_target"), "test")
            self.assertIsNone(pline(p, "missing_key"))
            self.assertIsNone(pline(os.path.join(d, "none.yaml"), "privacy_display"))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_the_repo_policy_values_are_allowed(self):
        p = os.path.join(ROOT, "contracts", "policy", "calendar.yaml")
        self.assertEqual(pvs(pline(p, "privacy_display"), ("busy", "full"))[0], "INFO")
        self.assertEqual(pvs(pline(p, "calendar_target"), ("test", "real"))[0], "INFO")

    def test_lines_are_wired_into_the_script(self):
        with open(HC) as fh:
            text = fh.read()
        for needle in ("privacy gate plugin loaded in shadow mode", "calendar policy: ", "gate_plugin_status(", "policy_value_status("):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
