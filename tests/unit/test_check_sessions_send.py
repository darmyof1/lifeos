"""Unit tests for scripts/verify/check_sessions_send.py (APR-0075, P-38). No network, no OpenClaw needed."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts", "verify"))
import check_sessions_send as cs  # noqa: E402


def call(ts, sender, args, cid):
    return {"type": "tool.call", "ts": ts, "sessionKey": "agent:%s:main" % sender,
            "data": {"name": "sessions_send", "args": args, "toolCallId": cid}}


def result(ts, sender, body, cid, success=True):
    text = body if isinstance(body, str) else json.dumps(body)
    return {"type": "tool.result", "ts": ts, "sessionKey": "agent:%s:main" % sender,
            "data": {"name": "sessions_send", "toolCallId": cid, "success": success,
                     "result": {"content": [{"type": "text", "text": text}]}}}


def write_run(root, run_id, cho_events, cos_events):
    for agent, events in (("cho", cho_events), ("cos", cos_events)):
        d = os.path.join(root, "%s-%s" % (run_id, agent))
        os.makedirs(d)
        with open(os.path.join(d, "events.jsonl"), "w") as fh:
            for e in events:
                fh.write(json.dumps(e) + "\n")
            fh.write("not json\n")  # the reader must skip junk lines
            fh.write(json.dumps({"type": "tool.call", "ts": "2026-10-26T04:00:00.000Z",
                                 "data": {"name": "exec", "args": {"code": "***"}}}) + "\n")


def check(root, run_id, since=""):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cs.run(root, run_id, since)
    return rc, buf.getvalue()


MSG = {"message": "x", "timeoutSeconds": 120, "mode": "followup"}


def good_cho():
    a = dict(MSG, sessionKey="agent:cos:main")
    return [call("2026-10-26T04:07:44.100Z", "cho", a, "c1"),
            result("2026-10-26T04:08:20.000Z", "cho", {"status": "ok", "reply": "Moved"}, "c1")]


class CheckSessionsSend(unittest.TestCase):
    def test_v17_run_passes(self):
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "r1", good_cho(), [])
            rc, out = check(t, "r1")
            self.assertEqual(rc, 0, out)
            self.assertIn("all checks passed", out)

    def test_old_behaviour_fails_on_mode_and_watch(self):
        # The run 002 pattern: notify + watch, forbidden; then notify queued; then followup works.
        cho = [
            call("2026-10-26T04:07:44.000Z", "cho", dict(MSG, agentId="cos", mode="notify", watch=True), "a"),
            result("2026-10-26T04:07:44.100Z", "cho", {"status": "forbidden", "error": "watch:true requires session status visibility"}, "a"),
            call("2026-10-26T04:07:49.000Z", "cho", dict(MSG, agentId="cos", mode="notify"), "b"),
            result("2026-10-26T04:07:49.100Z", "cho", {"status": "queued", "runStarted": False}, "b"),
            call("2026-10-26T04:08:46.000Z", "cho", dict(MSG, agentId="cos"), "c"),
            result("2026-10-26T04:09:23.000Z", "cho", {"status": "ok", "reply": "Moved"}, "c"),
        ]
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "r2", cho, [])
            rc, out = check(t, "r2")
            self.assertEqual(rc, 1, out)
            self.assertIn("FAIL  first CHO call uses mode followup", out)
            self.assertIn("FAIL  first CHO call does not set watch", out)
            self.assertIn("FAIL  first CHO call returned ok", out)
            self.assertIn("WARN  CHO sent 3 calls", out)

    def test_cos_send_to_cho_and_marker_fail(self):
        err = "Session \"agent:cho:main\" changed while starting work. Retry. | SESSION_WORK_START_CHANGED"
        cos = [call("2026-10-26T04:08:20.000Z", "cos", {"sessionKey": "agent:cho:main", "message": "y"}, "z"),
               result("2026-10-26T04:08:20.100Z", "cos", {"status": "error", "error": err, "sentBeforeError": True}, "z", success=False)]
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "r3", good_cho(), cos)
            rc, out = check(t, "r3")
            self.assertEqual(rc, 1, out)
            self.assertIn("FAIL  CoS sent nothing to the CHO", out)
            self.assertIn("FAIL  no SESSION_WORK_START_CHANGED", out)
            self.assertIn("PASS  first CHO call uses mode followup", out)

    def test_since_cuts_off_the_earlier_run(self):
        old = [call("2026-10-26T03:58:44.000Z", "cho", dict(MSG, agentId="cos", mode="notify", watch=True), "o"),
               result("2026-10-26T03:58:44.100Z", "cho", {"status": "forbidden"}, "o")]
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "r4", old + good_cho(), [])
            rc_all, _ = check(t, "r4")
            rc_cut, out = check(t, "r4", "2026-10-26T04:00:00Z")
            self.assertEqual(rc_all, 1)
            self.assertEqual(rc_cut, 0, out)

    def test_pairs_by_order_when_ids_are_missing(self):
        a = dict(MSG, sessionKey="agent:cos:main")
        c = call("2026-10-26T04:07:44.100Z", "cho", a, None)
        r = result("2026-10-26T04:08:20.000Z", "cho", {"status": "ok"}, None)
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "r5", [c, r], [])
            rc, out = check(t, "r5")
            self.assertEqual(rc, 0, out)

    def test_plain_text_error_result_is_an_error(self):
        a = dict(MSG, sessionKey="agent:cos:main", mode="resume")
        cho = [call("2026-10-26T04:07:44.100Z", "cho", a, "p"),
               result("2026-10-26T04:07:45.000Z", "cho", "mode=resume returns admission only", "p", success=False)]
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "r6", cho, [])
            rc, out = check(t, "r6")
            self.assertEqual(rc, 1, out)
            self.assertIn("status=error", out)

    def test_missing_export_is_reported(self):
        with tempfile.TemporaryDirectory() as t:
            rc, out = check(t, "nope")
            self.assertEqual(rc, 2)
            self.assertIn("MISSING", out)

    def test_target_can_come_from_agent_id(self):
        self.assertEqual(cs.target_of({"agentId": "cos"}), "cos")
        self.assertEqual(cs.target_of({"sessionKey": "agent:cho:main"}), "cho")
        self.assertEqual(cs.target_of({"sessionKey": "agent:coo:slack:channel:c0x"}), "coo")
        self.assertEqual(cs.target_of({}), "")


def cho_call(ts_call, ts_res, run, cid, **over):
    a = {"sessionKey": "agent:cos:main", "message": "Loop 1 run ID %s; event ID %s-cho-02; move it" % (run, run),
         "timeoutSeconds": 120, "mode": "followup"}
    a.update(over)
    return [call(ts_call, "cho", a, cid), result(ts_res, "cho", {"status": "ok", "reply": "Moved"}, cid)]


class CheckByRunId(unittest.TestCase):
    """One export holds several runs; the checker finds the run by its run ID (no --since needed)."""

    def two_runs(self, second_over=None):
        cho = cho_call("2026-10-26T05:56:29.000Z", "2026-10-26T05:56:59.000Z", "loop2-scn-003", "a")
        cho += cho_call("2026-10-26T06:01:27.000Z", "2026-10-26T06:01:57.000Z", "loop2-scn-004", "b", **(second_over or {}))
        return cho

    def test_second_run_is_not_blamed_for_the_first_runs_call(self):
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "loop2-scn-004", self.two_runs(), [])
            rc, out = check(t, "loop2-scn-004")
            self.assertEqual(rc, 0, out)
            self.assertIn("window: starts at 06:01:27", out)
            self.assertIn("1 call(s)", out)
            self.assertNotIn("WARN  CHO sent", out)
            self.assertNotIn("05:56:29", out)

    def test_first_run_stops_before_the_next_runs_call(self):
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "loop2-scn-003", self.two_runs(second_over={"mode": "notify", "watch": True}), [])
            rc, out = check(t, "loop2-scn-003")
            self.assertEqual(rc, 0, out)  # the bad call belongs to run 004
            self.assertIn("1 call(s)", out)

    def test_bad_call_in_this_run_still_fails(self):
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "loop2-scn-004", self.two_runs(second_over={"mode": "notify", "watch": True}), [])
            rc, out = check(t, "loop2-scn-004")
            self.assertEqual(rc, 1, out)
            self.assertIn("FAIL  first CHO call uses mode followup", out)

    def test_cos_send_in_this_run_is_counted_but_not_the_next_runs(self):
        err = {"status": "error", "error": "SESSION_WORK_START_CHANGED", "sentBeforeError": True}
        cos_here = [call("2026-10-26T06:01:40.000Z", "cos", {"sessionKey": "agent:cho:main", "message": "done loop2-scn-004"}, "z"),
                    result("2026-10-26T06:01:41.000Z", "cos", err, "z", success=False)]
        cos_next = [call("2026-10-26T06:10:40.000Z", "cos", {"sessionKey": "agent:cho:main", "message": "done loop2-scn-005"}, "y"),
                    result("2026-10-26T06:10:41.000Z", "cos", err, "y", success=False)]
        cho = self.two_runs() + cho_call("2026-10-26T06:10:00.000Z", "2026-10-26T06:10:30.000Z", "loop2-scn-005", "c")
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "loop2-scn-004", cho, cos_here + cos_next)
            rc, out = check(t, "loop2-scn-004")
            self.assertEqual(rc, 1, out)
            self.assertIn("FAIL  CoS sent nothing to the CHO  (1 call(s))", out)

    def test_unknown_run_id_checks_everything_and_warns(self):
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "zzz", good_cho(), [])
            rc, out = check(t, "zzz")
            self.assertEqual(rc, 0, out)
            self.assertIn("WARN  run ID zzz not found", out)

    def test_since_overrides_the_run_id_window(self):
        with tempfile.TemporaryDirectory() as t:
            write_run(t, "loop2-scn-004", self.two_runs(), [])
            rc, out = check(t, "loop2-scn-004", "2026-10-26T05:00:00Z")
            self.assertEqual(rc, 0, out)
            self.assertIn("2 call(s)", out)
            self.assertNotIn("window: starts", out)


if __name__ == "__main__":
    unittest.main()
