"""Test for the health-check line added in Loop 4 (APR-0117): the newest backup is younger than 8 days. The function is extracted with ast because health-check.py runs on import."""
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


F = extract(HC, {"backup_age_status"})["backup_age_status"]
NOW = 1_800_000_000
DAY = 86400


class BackupAge(unittest.TestCase):
    def test_none_is_info(self):
        self.assertEqual(F(None, NOW)[0], "INFO")

    def test_fresh_is_pass(self):
        self.assertEqual(F(NOW - 3600, NOW)[0], "PASS")
        self.assertEqual(F(NOW - 7 * DAY, NOW)[0], "PASS")

    def test_exactly_eight_days_is_warn(self):
        self.assertEqual(F(NOW - 8 * DAY, NOW)[0], "WARN")

    def test_old_is_warn(self):
        st, det = F(NOW - 30 * DAY, NOW)
        self.assertEqual(st, "WARN")
        self.assertIn("30.0 days", det)

    def test_future_date_is_warn(self):
        self.assertEqual(F(NOW + 3600, NOW)[0], "WARN")

    def test_the_line_is_wired_into_the_script(self):
        with open(HC) as fh:
            text = fh.read()
        self.assertIn("newest backup is younger than 8 days", text)
        self.assertIn("import glob", text)
        self.assertIn("import time", text)


if __name__ == "__main__":
    unittest.main()
