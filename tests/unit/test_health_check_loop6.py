"""Tests for the health-check line added in Loop 6 (APR-0121): the COO morning compaction log.
The function is extracted with ast because health-check.py runs on import."""
import ast
import calendar
import os
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HC = os.path.join(ROOT, "deploy", "loop1", "health-check.py")


def extract(path, names):
    with open(path) as fh:
        tree = ast.parse(fh.read())
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {"calendar": calendar, "time": time}
    exec(compile(ast.Module(body=body, type_ignores=[]), path, "exec"), ns)
    return ns


status = extract(HC, {"compact_log_status"})["compact_log_status"]
NOW = calendar.timegm((2026, 11, 10, 9, 25, 0))   # 05:25 AST on 2026-11-10 is 09:25 UTC


def line(day_hms, result, mode="execute"):
    return "%s AST mode=%s result=%s size_before=15289 size_after=unknown kept_lines=1" % (day_hms, mode, result)


class CompactLine(unittest.TestCase):
    def test_no_log_is_info(self):
        self.assertEqual(status([], NOW)[0], "INFO")

    def test_dry_run_lines_do_not_count(self):
        self.assertEqual(status([line("2026-11-10 05:00:00", "would-compact", "dry-run")], NOW)[0], "INFO")

    def test_young_compaction_passes(self):
        st, det = status([line("2026-11-10 05:25:01", "compacted")], NOW + 60)
        self.assertEqual(st, "PASS")
        self.assertIn("compacted", det)

    def test_a_skip_by_the_rule_still_counts_as_a_run(self):
        self.assertEqual(status([line("2026-11-10 05:25:01", "skipped")], NOW + 60)[0], "PASS")
        self.assertEqual(status([line("2026-11-10 05:25:01", "no-compaction-needed")], NOW + 60)[0], "PASS")

    def test_old_run_warns(self):
        st, det = status([line("2026-11-08 05:25:01", "compacted")], NOW)
        self.assertEqual(st, "WARN")
        self.assertIn("limit 36", det)

    def test_36_hour_edge(self):
        t = calendar.timegm((2026, 11, 9, 1, 0, 0))                       # 2026-11-08 21:00 AST
        self.assertEqual(status([line("2026-11-08 21:00:00", "compacted")], t + 36 * 3600 - 1)[0], "PASS")
        self.assertEqual(status([line("2026-11-08 21:00:00", "compacted")], t + 36 * 3600 + 1)[0], "WARN")

    def test_newest_line_decides(self):
        lines = [line("2026-11-10 05:25:01", "compacted"), line("2026-11-08 05:25:01", "error")]
        self.assertEqual(status(lines, NOW + 60)[0], "PASS")
        lines = [line("2026-11-09 05:25:01", "compacted"), line("2026-11-10 05:25:01", "error")]
        self.assertEqual(status(lines, NOW + 60)[0], "WARN")

    def test_error_and_refusal_warn(self):
        for r in ("error", "refused"):
            self.assertEqual(status([line("2026-11-10 05:25:01", r)], NOW + 60)[0], "WARN")

    def test_garbage_lines_are_ignored(self):
        self.assertEqual(status(["", "junk", "2026-13-45 99:99:99 AST mode=execute result=compacted"], NOW)[0], "INFO")

    def test_future_date_warns(self):
        self.assertEqual(status([line("2026-11-12 05:25:01", "compacted")], NOW)[0], "WARN")


class FileHasTheLines(unittest.TestCase):
    def test_cfo_send_list_still_expects_coo_and_cos(self):
        # Loop 6 Item 1 was skipped (APR-0092: the CFO sends calendar entries to the CoS); the existing line must keep that list
        with open(HC) as fh:
            text = fh.read()
        self.assertIn('"cfo": ["coo", "cos"]', text)
        self.assertIn("COO morning compaction ran in the last 36 hours", text)


if __name__ == "__main__":
    unittest.main()
