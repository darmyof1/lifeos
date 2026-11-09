"""Tests for scripts/ops/gate-shadow-report.py (APR-0119)."""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location("gsr", os.path.join(HERE, "..", "..", "scripts", "ops", "gate-shadow-report.py"))
gsr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gsr)


def line(day="2026-11-09", hour="10", agent="coo", ck="slack", tk="human", label="high", wb=True, reason="privacy_high_cloud_denied", h="0123456789abcdef"):
    return json.dumps({"time": "%sT%s:00:00.000Z" % (day, hour), "mode": "shadow", "agent": agent, "channel_kind": ck, "trigger_kind": tk,
                       "label": label, "would_block": wb, "reason": reason, "text_hash": h, "ms": 2})


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "gate-log.jsonl")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_main(self, lines):
        with open(self.path, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = gsr.main([self.path])
        return code, out.getvalue()

    def test_counts_by_label_agent_channel_trigger_and_day(self):
        lines = [line(), line(agent="cho", ck="main", label="high"),
                 line(agent="coo", label="low", wb=False, reason="privacy_low"),
                 line(day="2026-11-10", agent="cfo", ck="cron", tk="internal", label="medium", reason="medium_not_low_sensitivity"),
                 json.dumps({"time": "2026-11-10T11:00:00.000Z", "mode": "shadow", "error": "hook_error_failed_open"})]
        code, out = self.run_main(lines)
        self.assertEqual(code, 0)
        s = gsr.summarize(lines)
        self.assertEqual((s["turns"], s["wb_total"], s["errors"]), (4, 3, 1))
        self.assertEqual(dict(s["label"]), {"high": 2, "low": 1, "medium": 1})
        self.assertEqual(dict(s["wb_agent"]), {"coo": 1, "cho": 1, "cfo": 1})
        self.assertEqual(dict(s["wb_channel_kind"]), {"slack": 1, "main": 1, "cron": 1})
        self.assertEqual(dict(s["wb_trigger_kind"]), {"human": 2, "internal": 1})
        self.assertEqual(s["day"], {"2026-11-09": [3, 2], "2026-11-10": [1, 1]})
        self.assertEqual(s["first"], "2026-11-09T10:00:00.000Z")
        self.assertEqual(s["last"], "2026-11-10T11:00:00.000Z")
        self.assertIn("turns logged: 4   would block: 3   error lines: 1", out)
        self.assertIn("2026-11-09     3     2", out)

    def test_never_prints_a_hash_or_a_text(self):
        bad = json.loads(line())
        bad["text"] = "my private diary entry zx81"
        bad["agent"] = "my private diary entry zx81"
        code, out = self.run_main([json.dumps(bad), line(h="deadbeefdeadbeef")])
        self.assertEqual(code, 0)
        for secret in ("zx81", "diary", "deadbeefdeadbeef", "0123456789abcdef"):
            self.assertNotIn(secret, out)
        self.assertIn("other", out)  # the odd agent field is shown as "other"

    def test_damaged_lines_are_counted_and_skipped(self):
        code, out = self.run_main([line(), "not json", "{}", "[1]", line()])
        self.assertEqual(code, 0)
        self.assertIn("turns logged: 2", out)
        self.assertIn("damaged lines: 3", out)

    def test_empty_and_missing_log(self):
        code, out = self.run_main([""])
        self.assertEqual(code, 0)
        self.assertIn("turns logged: 0", out)
        self.assertIn("(none)", out)
        self.assertEqual(gsr.main([os.path.join(self.tmp, "nope.jsonl")]), 1)

    def test_the_script_only_reads(self):
        with open(os.path.join(HERE, "..", "..", "scripts", "ops", "gate-shadow-report.py")) as fh:
            text = fh.read()
        self.assertNotIn('"w"', text)
        self.assertNotIn("'w'", text)
        self.assertNotIn("subprocess", text)


if __name__ == "__main__":
    unittest.main()
