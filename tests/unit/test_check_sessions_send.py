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


if __name__ == "__main__":
    unittest.main()
