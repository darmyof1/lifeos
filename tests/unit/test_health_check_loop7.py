"""Tests for the health-check line added in Loop 7 (APR-0125): file tools confined to the workspace.
The function is extracted with ast because health-check.py runs on import."""
import ast
import os
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


status = extract(HC, {"workspace_confined_status"})["workspace_confined_status"]


def tools(only="absent"):
    t = {"alsoAllow": ["read", "write", "edit"]}
    if only != "absent":
        t["fs"] = {"workspaceOnly": only}
    return t


def good():
    return {"cho": tools(True), "cos": tools(True), "cfo": tools(True)}


class ConfinedLine(unittest.TestCase):
    def test_all_confined_passes(self):
        self.assertEqual(status(good())[0], "PASS")

    def test_each_agent_false_fails(self):
        for a in ("cho", "cos", "cfo"):
            d = good()
            d[a] = tools(False)
            st, det = status(d)
            self.assertEqual(st, "FAIL", a)
            self.assertIn(a + ": workspaceOnly = False", det)

    def test_each_agent_missing_key_fails(self):
        for a in ("cho", "cos", "cfo"):
            d = good()
            d[a] = tools()
            self.assertEqual(status(d)[0], "FAIL", a)
            d[a] = {"alsoAllow": ["read"], "fs": {}}
            self.assertEqual(status(d)[0], "FAIL", a)

    def test_missing_tools_block_fails(self):
        d = good()
        d["cfo"] = None
        self.assertEqual(status(d)[0], "FAIL")

    def test_agent_without_file_tools_passes(self):
        d = good()
        d["cfo"] = {"alsoAllow": []}
        self.assertEqual(status(d)[0], "PASS")
        d["cfo"] = {}
        self.assertEqual(status(d)[0], "PASS")

    def test_coo_style_agent_without_tools_passes_even_when_false(self):
        self.assertEqual(status({"coo": {"fs": {"workspaceOnly": False}}})[0], "PASS")
        self.assertEqual(status({"coo": {}})[0], "PASS")

    def test_non_file_tool_in_also_allow_is_not_file_tools(self):
        d = good()
        d["cho"] = {"alsoAllow": ["sessions_send"], "fs": {"workspaceOnly": False}}
        self.assertEqual(status(d)[0], "PASS")


class CloKnown(unittest.TestCase):
    """Part 3 (APR-0127): the health check knows the CLO. Source-level checks, because the file runs on import."""
    with open(HC) as fh:
        src = fh.read()

    def test_clo_false_or_missing_fails(self):
        for bad in (tools(False), tools(), None):
            d = dict(good(), clo=bad)
            self.assertEqual(status(d)[0], "FAIL", bad)
        self.assertEqual(status(dict(good(), clo=tools(True)))[0], "PASS")

    def test_clo_is_in_every_list(self):
        for needle in ('AGENTS = ["coo", "cho", "cos", "cfo", "clo"]',
                       '"clo": ["coo", "cos"]}',
                       'for a in ("cho", "cos", "cfo", "clo")})',
                       'expected_slack = ["default", "cho", "cos", "cfo", "clo"]',
                       '("cfo", "v1.11"), ("clo", "v1.0")',
                       '"clo": "department/clo"',
                       '"CLO": "lifestyle-clo"'):
            self.assertIn(needle, self.src)

    def test_cfo_is_expected_on_v111_not_v110(self):
        self.assertNotIn('("cfo", "v1.10")', self.src)


if __name__ == "__main__":
    unittest.main()
