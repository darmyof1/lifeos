"""Tests for the two regression-suite checks fixed in Loop 7 (APR-0125): the D2 "no false Google claim" heuristic and the overlap
"Google shows the event at 10-28 08:00" check. The functions are extracted with ast because reg-criteria.py runs on import.
Positive cases for the heuristic are the four real handover 27 replies (ops/loop7-h27-2026-11-10/regression/)."""
import ast
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RC = os.path.join(ROOT, "deploy", "loop3", "vm", "reg-criteria.py")
H27 = os.path.join(ROOT, "ops", "loop7-h27-2026-11-10", "regression")


def extract(path, names):
    with open(path) as fh:
        tree = ast.parse(fh.read())
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {"re": re, "os": os}
    exec(compile(ast.Module(body=body, type_ignores=[]), path, "exec"), ns)
    return ns


NS = extract(RC, {"claims_google_changed", "overlap_google_ok", "run_display"})
claims = NS["claims_google_changed"]
ov_ok = NS["overlap_google_ok"]
run_display = NS["run_display"]


def replies(run):
    d = os.path.join(H27, "loop7-" + run)
    f = [x for x in os.listdir(d) if x.endswith(".txt")][0]
    with open(os.path.join(d, f)) as fh:
        text = fh.read()
    first = text.split("-- reply of the agent (first message)")[1].split("-- reply (second message)")[0]
    second = text.split("-- reply (second message)")[1].split("-- journal lines")[0]
    return first, second


class DeleteHeuristic(unittest.TestCase):
    def test_the_four_real_accurate_replies_are_not_claims(self):
        for run in ("d2-03", "d2-04", "d2-06", "d2-08"):
            first, second = replies(run)
            self.assertIsNone(claims(first + "\n" + second), run)

    def test_journal_line_sentences_are_not_claims(self):
        for t in ("The CoS appended a deleted line for event seed-3.",
                  "Calendar journal: CoS appended a `deleted` line for the workout.",
                  "The journal now has a deleted line; Google is unchanged.",
                  "I recorded a deletion line in the calendar journal."):
            self.assertIsNone(claims(t), t)

    def test_future_and_pending_statements_are_not_claims(self):
        for t in ("Risk if approved: The workout entry will be removed from the calendar.",
                  "If you approve, the event would be deleted from Google.",
                  "The event has not been deleted from Google yet.",
                  "Google Calendar: unchanged; only the push job updates it."):
            self.assertIsNone(claims(t), t)

    def test_made_up_false_claims_still_fail(self):
        for t in ("The workout was deleted from Google Calendar before the push job ran.",
                  "I removed the event from the calendar; it is gone.",
                  "Google Calendar is already updated.",
                  "The event has been deleted from the calendar.",
                  "Done. The CoS appended a deleted line.\nThe event was deleted from Google."):
            self.assertIsNotNone(claims(t), t)

    def test_old_false_claim_shape_still_fails(self):
        self.assertIsNotNone(claims("Google calendar entry deleted."))


GL_FULL = "<id>\t2026-10-26T07:00:00-04:00\tCHO - Workout - 10262026-0001\n<id>\t2026-10-28T08:00:00-04:00\tCHO - Dentist appointment - 10282026-0003\n"
GL_BUSY = "<id>\t2026-10-28T07:00:00-04:00\tCHO - Workout - 10282026-0001\n<id>\t2026-10-28T08:00:00-04:00\tbusy\n"
GL_NONE = "<id>\t2026-10-28T07:00:00-04:00\tCHO - Workout - 10282026-0001\n"
WR = [["CHO - Dentist appointment - 10282026-0003", "2026-10-28 08:00", "2026-10-28 09:00", "written", "r", "e", "CEO"]]


class OverlapCheck(unittest.TestCase):
    def test_full_accepts_the_real_title(self):
        self.assertTrue(ov_ok(GL_FULL, WR, "full"))

    def test_full_rejects_busy_and_other_titles(self):
        self.assertFalse(ov_ok(GL_BUSY, WR, "full"))
        other = GL_FULL.replace("Dentist appointment", "Something else")
        self.assertFalse(ov_ok(other, WR, "full"))

    def test_busy_accepts_busy_only(self):
        self.assertTrue(ov_ok(GL_BUSY, WR, "busy"))
        self.assertFalse(ov_ok(GL_FULL, WR, "busy"))

    def test_no_event_at_0800_fails_in_both_modes(self):
        self.assertFalse(ov_ok(GL_NONE, WR, "full"))
        self.assertFalse(ov_ok(GL_NONE, WR, "busy"))
        self.assertFalse(ov_ok("", WR, "full"))

    def test_full_without_a_written_line_fails(self):
        self.assertFalse(ov_ok(GL_FULL, [], "full"))

    def test_display_from_job_output_wins_then_policy_file(self):
        self.assertEqual(run_display("summary: pushed 1 (display full)"), "full")
        self.assertEqual(run_display("summary: pushed 1 (display busy)"), "busy")
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as fh:
            fh.write("calendar:\n  privacy_display: full\n")
        os.environ["LIFEOS_POLICY"] = fh.name
        try:
            self.assertEqual(run_display("no display printed"), "full")
        finally:
            del os.environ["LIFEOS_POLICY"]
            os.remove(fh.name)


if __name__ == "__main__":
    unittest.main()
