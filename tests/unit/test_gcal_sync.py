"""Unit tests for scripts/gcal/gcal_sync.py (P-28, APR-0077, APR-0078). No network, no Google libraries, no OpenClaw.

Run from the repo root:
    python3 -B -m unittest discover -s tests/unit -p "test_gcal_sync.py"
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts", "gcal"))
sys.dont_write_bytecode = True

import gcal_common as gc  # noqa: E402
import gcal_sync as gs  # noqa: E402
from test_gcal_scripts import FakeHttpError, FakeService, CAL, TZ  # noqa: E402

HEADER = "name | start | end | status | run ID | event ID | requested by\n"
N1 = "CHO - Workout - 10282026-0001"
N2 = "CHO - Workout - 10282026-0002"


def jl(name, start, end, status, run="r1", event="r1-cho-01", by="CoS", detail=""):
    line = " | ".join([name, start, end, status, run, event, by])
    return line + (" | " + detail if detail else "") + "\n"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.journal = os.path.join(self.tmp, "calendar-journal.md")
        self.state = os.path.join(self.tmp, "state")
        self.alerts = []
        self.svc = FakeService()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, *lines):
        with open(self.journal, "w") as fh:
            fh.write(HEADER + "".join(lines))

    def text(self):
        with open(self.journal) as fh:
            return fh.read()

    def new_lines(self, before):
        return self.text()[len(before):].splitlines()

    def go(self, **kw):
        buf = io.StringIO()
        kw.setdefault("allow_deletes", False)
        code, counts = gs.sync(self.svc, CAL, self.journal, self.state, self.alerts.append, TZ,
                               out=lambda s: buf.write(s + "\n"), **kw)
        return code, counts, buf.getvalue()


class ParseTests(unittest.TestCase):
    def test_header_notes_and_junk_are_skipped(self):
        text = HEADER + "# a note\n\nnot a row | x\n" + jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written") + \
            jl("Bad title", "a", "b", "written") + jl(N1, "a", "b", "wat")
        got = gs.parse_journal(text)
        self.assertEqual([e.name for e in got], [N1])
        self.assertEqual(got[0].status, "written")

    def test_detail_column_and_pipe_cleaning(self):
        e = gs.parse_journal(jl(N1, "s", "e", "pushed", by="sync", detail="google=abc"))[0]
        self.assertEqual((e.by, e.detail), ("sync", "google=abc"))
        self.assertEqual(gs.clean("a | b\nc"), "a / b c")
        self.assertTrue(gs.clean("x" * 500).endswith("..."))


class PushTests(Base):
    def test_written_is_created_and_pushed_line_appended(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        before = self.text()
        code, counts, out = self.go()
        self.assertEqual((code, counts["pushed"]), (0, 1))
        inserts = [c for c in self.svc.calls if c[0] == "insert"]
        self.assertEqual(len(inserts), 1)
        body = inserts[0][1]["body"]
        self.assertEqual(sorted(body), ["end", "start", "summary"])
        self.assertEqual(body["end"]["dateTime"], "2026-10-28T08:00:00-04:00")
        (line,) = self.new_lines(before)
        self.assertEqual(line, " | ".join([N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", "r1", "r1-cho-01", "sync", "google=new1"]))
        self.assertTrue(self.text().startswith(before))  # nothing before was touched

    def test_second_run_does_nothing(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        self.go()
        text, n = self.text(), len(self.svc.calls)
        code, counts, _ = self.go()
        self.assertEqual((code, counts["pushed"]), (0, 0))
        self.assertEqual(self.text(), text)
        self.assertEqual(len(self.svc.calls), n)

    def test_already_in_google_is_pushed_without_a_write(self):
        self.svc.add("x1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        before = self.text()
        self.go()
        self.assertEqual(self.svc.writes(), [])
        self.assertIn("google=x1", self.new_lines(before)[0])

    def test_same_title_other_time_is_a_conflict_and_nothing_changes(self):
        self.svc.add("x1", N1, "2026-10-28T09:00:00-04:00", "2026-10-28T10:00:00-04:00")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        before = self.text()
        code, counts, _ = self.go()
        self.assertEqual(counts["conflict"], 1)
        self.assertEqual(self.svc.writes(), [])
        self.assertIn("| conflict |", self.new_lines(before)[0])
        self.assertIn("reason=", self.new_lines(before)[0])

    def test_two_events_with_the_title_is_a_conflict(self):
        for i in (1, 2):
            self.svc.add("x%d" % i, N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        _, counts, _ = self.go()
        self.assertEqual(counts["conflict"], 1)
        self.assertEqual(self.svc.writes(), [])

    def test_bad_entries_are_conflicts_without_a_google_call(self):
        self.write(
            jl(N1, "2026-10-29 07:00", "2026-10-29 08:00", "written", event="e1"),            # date differs from title
            jl(N2, "2026-10-28 08:00", "2026-10-28 07:00", "written", event="e2"),            # end before start
            jl("CHO - Y - 10282026-0003", "tomorrow", "later", "written", event="e3"))        # unreadable times
        _, counts, _ = self.go()
        self.assertEqual(counts["conflict"], 3)
        self.assertEqual(self.svc.calls, [])

    def test_move_pair_moves_the_old_event_with_the_new_title(self):
        self.svc.add("old1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", run="s", event="s-1", by="sync", detail="google=old1"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl(N2, "2026-10-28 09:00", "2026-10-28 10:00", "written", run="r2", event="r2-cho-02"))
        before = self.text()
        code, counts, _ = self.go()
        self.assertEqual(code, 0)
        self.assertEqual([c[0] for c in self.svc.writes()], ["patch"])
        self.assertEqual(self.svc.store["old1"]["summary"], N2)
        self.assertEqual(self.svc.store["old1"]["start"]["dateTime"], "2026-10-28T09:00:00-04:00")
        self.assertEqual(len(self.new_lines(before)), 1)
        self.assertIn("google=old1", self.new_lines(before)[0])

    def test_move_pair_without_old_event_creates(self):
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl(N2, "2026-10-28 09:00", "2026-10-28 10:00", "written", run="r2", event="r2-cho-02"))
        self.go()
        self.assertEqual([c[0] for c in self.svc.writes()], ["insert"])

    def test_move_pair_with_two_old_events_is_a_conflict(self):
        for i in (1, 2):
            self.svc.add("o%d" % i, N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl(N2, "2026-10-28 09:00", "2026-10-28 10:00", "written", run="r2", event="r2-cho-02"))
        _, counts, _ = self.go()
        self.assertEqual((counts["conflict"], self.svc.writes()), (1, []))

    def test_same_name_move_hint_moves_in_place(self):
        self.svc.add("x1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl(N1, "2026-10-28 11:00", "2026-10-28 12:00", "written", run="r2", event="r2-cho-02"))
        self.go()
        self.assertEqual(self.svc.store["x1"]["start"]["dateTime"], "2026-10-28T11:00:00-04:00")

    def test_requested_conflict_moved_and_pending_delete_are_ignored(self):
        self.write(jl(N1, "a", "b", "requested"), jl(N2, "a", "b", "conflict"),
                   jl("CHO - Z - 10282026-0003", "a", "b", "delete-pending-approval"))
        self.go()
        self.assertEqual(self.svc.calls, [])

    def test_personal_event_with_the_same_title_is_never_touched(self):
        self.svc.add("rec", N1, "2026-10-28T09:00:00-04:00", "2026-10-28T10:00:00-04:00", recurringEventId="s0")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        _, counts, _ = self.go()
        self.assertEqual(self.svc.writes(), [])
        self.assertEqual(counts["conflict"], 1)

    def test_no_final_newline_in_journal(self):
        with open(self.journal, "w") as fh:
            fh.write(HEADER + jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written").rstrip("\n"))
        self.go()
        lines = self.text().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[2].startswith(N1 + " | "))

    def test_max_per_run(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", event="e1"),
                   jl(N2, "2026-10-28 09:00", "2026-10-28 10:00", "written", event="e2"))
        _, counts, out = self.go(max_per_run=1)
        self.assertEqual(counts["pushed"], 1)
        self.assertIn("stop", out)
        self.go(max_per_run=1)
        self.assertEqual(len([c for c in self.svc.calls if c[0] == "insert"]), 2)


class DryRunTests(Base):
    def test_dry_run_writes_nothing_anywhere(self):
        self.svc.add("old1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl(N2, "2026-10-28 09:00", "2026-10-28 10:00", "written", run="r2", event="r2-cho-02"),
            jl("CHO - New - 10292026-0001", "2026-10-29 07:00", "2026-10-29 08:00", "written", event="e9"))
        before = self.text()
        code, counts, out = self.go(dry_run=True)
        self.assertEqual(code, 0)
        self.assertEqual(self.text(), before)
        self.assertEqual(self.svc.writes(), [])
        self.assertIn("would", out)
        self.assertEqual(self.alerts, [])
        self.assertFalse(os.path.exists(self.state))


class FailureTests(Base):
    def test_failure_appends_attempts_then_final_and_alerts_once(self):
        self.svc.fail_patch = False
        self.svc.add("x1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        orig = self.svc.events

        class Boom(Exception):
            pass

        def boom(*a, **k):
            raise Boom("backend unavailable")
        self.svc.events = lambda: types.SimpleNamespace(list=boom)
        self.write(jl("CHO - Y - 10282026-0009", "2026-10-28 07:00", "2026-10-28 08:00", "written", event="e9"))
        for n in range(1, 6):
            code, counts, out = self.go()
            self.assertEqual((code, counts["failed"]), (0, 1), out)
            last = self.text().splitlines()[-1]
            self.assertIn("| failed |", last)
            self.assertIn("attempt=%d;" % n, last)
            self.assertEqual(len(self.alerts), 1 if n == 5 else 0)
        self.assertIn("final", last)
        n_lines = len(self.text().splitlines())
        code, counts, _ = self.go()  # attempts used up: no sixth try
        self.assertEqual(counts["failed"], 0)
        self.assertEqual(len(self.text().splitlines()), n_lines)
        self.assertEqual(len(self.alerts), 1)
        self.svc.events = orig

    def test_recovery_after_a_failure_pushes(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "failed", by="sync", detail="attempt=1; error=x"))
        _, counts, _ = self.go()
        self.assertEqual(counts["pushed"], 1)
        self.assertIn("| pushed |", self.text().splitlines()[-1])

    def test_revoked_login_pauses_alerts_once_and_stops(self):
        def revoked(*a, **k):
            raise Exception("invalid_grant: Token has been expired or revoked.")
        self.svc.events = lambda: types.SimpleNamespace(list=revoked)
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", event="e1"),
                   jl(N2, "2026-10-28 09:00", "2026-10-28 10:00", "written", event="e2"))
        before = self.text()
        code, _, out = self.go()
        self.assertEqual(code, 3)
        self.assertEqual(self.text(), before)  # a revoked login is not the entry's fault: no failed line
        self.assertEqual(len(self.alerts), 1)
        self.assertTrue(os.path.exists(gs.pause_path(self.state)))
        code, _, out = self.go()  # paused: nothing, no second alert
        self.assertEqual(code, 3)
        self.assertEqual(len(self.alerts), 1)
        self.assertIn("paused", out)
        os.remove(gs.pause_path(self.state))
        self.assertTrue(gs.is_token_revoked(FakeHttpError(401)))
        self.assertFalse(gs.is_token_revoked(FakeHttpError(500)))

    def test_http_401_also_pauses(self):
        def unauth(*a, **k):
            raise FakeHttpError(401)
        self.svc.events = lambda: types.SimpleNamespace(list=unauth)
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        self.assertEqual(self.go()[0], 3)

    def test_missing_journal_is_exit_4(self):
        code, _, out = self.go()
        self.assertEqual(code, 4)
        self.assertIn("cannot read the journal", out)

    def test_refusal_from_the_scripts_is_a_conflict_not_a_retry(self):
        self.svc.add("p1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00", recurringEventId="s0")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl(N2, "2026-10-28 09:00", "2026-10-28 10:00", "written", run="r2", event="r2-cho-02"))
        _, counts, _ = self.go()
        self.assertEqual((counts["conflict"], counts["failed"]), (1, 0))
        self.assertEqual(self.svc.writes(), [])


class DeleteTests(Base):
    def lines(self, with_request=True):
        out = [jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", run="s", event="s-1", by="sync", detail="google=x1")]
        if with_request:
            out.append(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "delete-pending-approval", run="r3", event="r3-cho-01"))
        out.append(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "deleted", run="r3", event="r3-cho-01"))
        return out

    def setUp(self):
        super().setUp()
        self.svc.add("x1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")

    def test_off_by_default(self):
        self.write(*self.lines())
        _, counts, out = self.go()
        self.assertEqual((counts["skipped"], self.svc.writes()), (1, []))
        self.assertIn("--allow-deletes", out)

    def test_runs_with_the_flag_after_a_pending_line(self):
        self.write(*self.lines())
        before = self.text()
        _, counts, _ = self.go(allow_deletes=True)
        self.assertEqual(counts["deleted"], 1)
        self.assertNotIn("x1", self.svc.store)
        self.assertIn("deleted", self.new_lines(before)[0])
        self.assertIn("google=x1", self.new_lines(before)[0])
        self.go(allow_deletes=True)  # latest line is now pushed: nothing more
        self.assertEqual(len([c for c in self.svc.calls if c[0] == "delete"]), 1)

    def test_refused_without_a_pending_line(self):
        self.write(*self.lines(with_request=False))
        _, counts, out = self.go(allow_deletes=True)
        self.assertEqual((counts["skipped"], self.svc.writes()), (1, []))
        self.assertIn("no delete-pending-approval", out)
        self.assertIn("x1", self.svc.store)

    def test_dry_run_deletes_nothing(self):
        self.write(*self.lines())
        self.go(allow_deletes=True, dry_run=True)
        self.assertIn("x1", self.svc.store)

    def test_already_gone(self):
        del self.svc.store["x1"]
        self.write(*self.lines())
        before = self.text()
        self.go(allow_deletes=True)
        self.assertIn("already gone", self.new_lines(before)[0])


class CeoLedgerTests(DeleteTests):
    """APR-0100: --require-ceo-ledger. Off by default; the inherited DeleteTests run without the flag and must still pass."""
    NOW = None

    def ledger(self, *rows):
        import json
        self.lpath = os.path.join(self.tmp, "ceo-ledger.jsonl")
        with open(self.lpath, "w") as fh:
            for r in rows:
                fh.write((r if isinstance(r, str) else json.dumps(r)) + "\n")
        return self.lpath

    def row(self, **kw):
        r = {"time": "2020-01-01T00:00:00Z", "run": "r3", "event": "r3-cho-01", "channel": "slack", "sender": "CEO",
             "text_sha256": "0" * 64}
        r.update(kw)
        return r

    def gate(self, path):
        self.write(*self.lines())
        return self.go(allow_deletes=True, ceo_ledger=path)

    def test_no_entry_no_delete(self):
        _, counts, out = self.gate(self.ledger())
        self.assertEqual((counts["deleted"], counts["skipped"]), (0, 1))
        self.assertIn("no CEO approval record for event r3-cho-01", out)
        self.assertIn("x1", self.svc.store)

    def test_missing_ledger_no_delete(self):
        _, counts, _ = self.gate(os.path.join(self.tmp, "nope.jsonl"))
        self.assertEqual(counts["deleted"], 0)
        self.assertIn("x1", self.svc.store)

    def test_matching_entry_deletes(self):
        _, counts, _ = self.gate(self.ledger(self.row()))
        self.assertEqual(counts["deleted"], 1)
        self.assertNotIn("x1", self.svc.store)

    def test_other_run_or_event_no_delete(self):
        for kw in ({"run": "r9"}, {"event": "r9-cho-01"}):
            self.setUp()
            _, counts, _ = self.gate(self.ledger(self.row(**kw)))
            self.assertEqual(counts["deleted"], 0, kw)
            self.assertIn("x1", self.svc.store)

    def test_sender_not_ceo_or_future_time_or_bad_line_no_delete(self):
        for r in (self.row(sender="COO"), self.row(time="2999-01-01T00:00:00Z"), self.row(time="not a time"), "{broken", "[1]"):
            self.setUp()
            _, counts, _ = self.gate(self.ledger(r))
            self.assertEqual(counts["deleted"], 0, r)
            self.assertIn("x1", self.svc.store)

    def test_pending_line_is_still_required(self):
        self.write(*self.lines(with_request=False))
        _, counts, out = self.go(allow_deletes=True, ceo_ledger=self.ledger(self.row()))
        self.assertEqual(counts["deleted"], 0)
        self.assertIn("no delete-pending-approval", out)

    def test_main_accepts_the_flag(self):
        import inspect
        self.assertIn("--require-ceo-ledger", inspect.getsource(gs.main))


class HighPrivacyTests(Base):
    """High-privacy entries show in Google as busy, with a hidden key and never the mandated title (APR-0032, APR-0079)."""
    HP = "privacy=high"

    def busy_events(self):
        return [e for e in self.svc.store.values() if e.get("summary") == "busy"]

    def add_busy(self, eid, key, start="2026-10-28T07:00:00-04:00", end="2026-10-28T08:00:00-04:00"):
        self.svc.add(eid, "busy", start, end, extendedProperties={"private": {"lifeos_event": key}})

    def test_created_as_busy_with_a_hidden_key_and_no_name(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP))
        before = self.text()
        code, counts, _ = self.go()
        self.assertEqual((code, counts["pushed"]), (0, 1))
        (call,) = [c for c in self.svc.calls if c[0] == "insert"]
        body = call[1]["body"]
        self.assertEqual(body["summary"], "busy")
        self.assertEqual(body["transparency"], "opaque")
        self.assertEqual(body["extendedProperties"], {"private": {"lifeos_event": "r1-cho-01"}})
        self.assertEqual(sorted(body), ["end", "extendedProperties", "start", "summary", "transparency"])
        self.assertNotIn("Workout", repr(self.svc.calls))  # the mandated title never goes to Google
        (line,) = self.new_lines(before)
        self.assertTrue(line.endswith("| sync | google=new1; privacy=high"), line)

    def test_second_run_does_nothing(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP))
        self.go()
        text, writes = self.text(), len(self.svc.writes())
        self.go()
        self.assertEqual(self.text(), text)
        self.assertEqual(len(self.svc.writes()), writes)

    def test_marker_is_remembered_from_the_pushed_line(self):
        # the CoS writes the marker once; later lines of the same name (a job line, a CoS line without it) still count
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP),
                   jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=b1; privacy=high"),
                   jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "failed", by="sync", detail="attempt=1; error=x"))
        self.assertTrue(gs.is_high_privacy(gs.parse_journal(self.text()), N1))
        self.assertFalse(gs.is_high_privacy(gs.parse_journal(self.text()), N2))

    def test_crash_recovery_finds_the_busy_event_by_key(self):
        self.add_busy("b1", "r1-cho-01")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP))
        before = self.text()
        self.go()
        self.assertEqual(self.svc.writes(), [])
        self.assertIn("google=b1", self.new_lines(before)[0])

    def test_same_key_at_another_time_or_twice_is_a_conflict(self):
        self.add_busy("b1", "r1-cho-01", "2026-10-28T09:00:00-04:00", "2026-10-28T10:00:00-04:00")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP))
        self.assertEqual(self.go()[1]["conflict"], 1)
        self.assertEqual(self.svc.writes(), [])
        self.svc.store.clear()
        self.add_busy("b1", "r1-cho-01")
        self.add_busy("b2", "r1-cho-01")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP))
        self.assertEqual(self.go()[1]["conflict"], 1)
        self.assertEqual(self.svc.writes(), [])

    def test_other_busy_events_are_not_taken(self):
        self.add_busy("b9", "someone-else")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP))
        self.go()
        self.assertEqual([c[0] for c in self.svc.writes()], ["insert"])

    def test_move_pair_moves_the_busy_event_and_updates_the_key(self):
        self.add_busy("b1", "r1-cho-01")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=b1; privacy=high"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl("CHO - Workout - 10292026-0001", "2026-10-29 07:00", "2026-10-29 08:00", "written", run="r2", event="r2-cho-02", detail=self.HP))
        before = self.text()
        code, counts, _ = self.go()
        self.assertEqual(code, 0, counts)
        self.assertEqual([c[0] for c in self.svc.writes()], ["patch"])
        ev = self.svc.store["b1"]
        self.assertEqual(ev["summary"], "busy")
        self.assertEqual(ev["start"]["dateTime"], "2026-10-29T07:00:00-04:00")
        self.assertEqual(ev["extendedProperties"]["private"]["lifeos_event"], "r2-cho-02")
        self.assertNotIn("Workout", repr(self.svc.calls))
        self.assertIn("google=b1; privacy=high", self.new_lines(before)[0])
        self.go()  # a second run finds it by the new key and does nothing
        self.assertEqual(len(self.svc.writes()), 1)

    def test_move_pair_with_the_old_event_gone_creates(self):
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=gone; privacy=high"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl("CHO - Workout - 10292026-0001", "2026-10-29 07:00", "2026-10-29 08:00", "written", run="r2", event="r2-cho-02", detail=self.HP))
        self.go()
        self.assertEqual([c[0] for c in self.svc.writes()], ["insert"])

    def test_a_normal_event_becomes_busy_when_a_move_raises_privacy(self):
        # APR-0086: the seed workout is a normal event; the CHO's move is high privacy; Google must end with a busy event
        self.svc.add("p1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00", description="secret plan", location="home")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=p1"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02", detail=self.HP),
            jl("CHO - Workout - 10292026-0001", "2026-10-29 07:00", "2026-10-29 08:00", "written", run="r2", event="r2-cho-02", detail=self.HP))
        before = self.text()
        code, counts, _ = self.go()
        self.assertEqual((counts["conflict"], counts["pushed"]), (0, 1))
        ev = self.svc.store["p1"]
        self.assertEqual(ev["summary"], "busy")
        self.assertEqual(ev["transparency"], "opaque")
        self.assertEqual(ev["extendedProperties"], {"private": {"lifeos_event": "r2-cho-02"}})
        self.assertTrue(ev["start"]["dateTime"].startswith("2026-10-29T07:00"), ev["start"])
        self.assertEqual((ev["description"], ev["location"]), ("", ""))
        self.assertEqual([c[0] for c in self.svc.writes()], ["patch"])
        self.assertNotIn("Workout", repr(ev))
        (line,) = self.new_lines(before)
        self.assertTrue(line.endswith("| sync | google=p1; privacy=high"), line)

    def test_a_normal_event_becomes_busy_when_the_same_name_is_marked_high_later(self):
        self.svc.add("p1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=p1"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", run="r2", event="r2-cho-03", detail=self.HP))
        self.assertEqual(self.go()[1]["conflict"], 0)
        self.assertEqual(self.svc.store["p1"]["summary"], "busy")
        self.assertEqual([c[0] for c in self.svc.writes()], ["patch"])  # no second event, no duplicate with the mandated title
        self.assertEqual(len([e for e in self.svc.store.values() if "Workout" in e.get("summary", "")]), 0)

    def test_dry_run_of_raising_privacy_changes_nothing(self):
        self.svc.add("p1", N1, "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=p1"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02", detail=self.HP),
            jl("CHO - Workout - 10292026-0001", "2026-10-29 07:00", "2026-10-29 08:00", "written", run="r2", event="r2-cho-02", detail=self.HP))
        before = self.text()
        self.go(dry_run=True)
        self.assertEqual((self.text(), self.svc.writes()), (before, []))
        self.assertEqual(self.svc.store["p1"]["summary"], N1)

    def test_make_busy_refuses_other_events(self):
        import gcal_busy
        self.svc.add("p3", "Dentist", "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.add_busy("b1", "k")
        for eid in ("p3", "b1", "series1", "gym1"):  # a personal event, a busy event, a recurring one, an all-day one
            with self.assertRaises(gc.CalendarError):
                gcal_busy.make_busy(self.svc, CAL, eid, "k2", "2026-10-28T09:00", 60, TZ)
        self.assertEqual(self.svc.writes(), [])

    def test_privacy_follows_a_move_even_if_the_new_line_has_no_marker(self):
        # a forgotten marker must never put a mandated title into Google; the old event here is a personal one: conflict
        self.svc.add("p2", "Dentist", "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=p2; privacy=high"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl("CHO - Workout - 10292026-0001", "2026-10-29 07:00", "2026-10-29 08:00", "written", run="r2", event="r2-cho-02"))
        self.assertEqual(self.go()[1]["conflict"], 1)
        self.assertEqual(self.svc.writes(), [])
        self.assertEqual(self.svc.store["p2"]["summary"], "Dentist")

    def test_privacy_follows_a_move_into_a_new_busy_event(self):
        self.write(
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=gone; privacy=high"),
            jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "moved", run="r2", event="r2-cho-02"),
            jl("CHO - Workout - 10292026-0001", "2026-10-29 07:00", "2026-10-29 08:00", "written", run="r2", event="r2-cho-02"))
        self.go()
        self.assertEqual([self.svc.store[k]["summary"] for k in self.svc.store if k.startswith("new")], ["busy"])
        self.assertNotIn("Workout", repr(self.svc.calls))

    def test_dry_run_changes_nothing(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written", detail=self.HP))
        before = self.text()
        self.go(dry_run=True)
        self.assertEqual((self.text(), self.svc.writes()), (before, []))

    def test_delete_gate_for_a_busy_event(self):
        self.add_busy("b1", "r1-cho-01")
        lines = [jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=b1; privacy=high", event="r1-cho-01"),
                 jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "deleted", run="r3", event="r3-cho-01")]
        self.write(*lines)
        self.go(allow_deletes=True)  # no pending line: refused
        self.assertIn("b1", self.svc.store)
        self.write(lines[0], jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "delete-pending-approval", run="r3", event="r3-cho-01"), lines[1])
        self.go()  # flag off: refused
        self.assertIn("b1", self.svc.store)
        before = self.text()
        _, counts, _ = self.go(allow_deletes=True)
        self.assertEqual(counts["deleted"], 1)
        self.assertNotIn("b1", self.svc.store)
        self.assertIn("deleted", self.new_lines(before)[0])

    def test_delete_refuses_a_busy_event_with_another_key(self):
        self.add_busy("b1", "someone-else")
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "pushed", by="sync", detail="google=b1; privacy=high", event="r1-cho-01"),
                   jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "delete-pending-approval", run="r3", event="r3-cho-01"),
                   jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "deleted", run="r3", event="r3-cho-01"))
        self.go(allow_deletes=True)
        self.assertIn("b1", self.svc.store)

    def test_busy_helpers_refuse_other_events(self):
        import gcal_busy
        self.svc.add("p3", "Dentist", "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")
        self.svc.add("p4", "busy", "2026-10-28T07:00:00-04:00", "2026-10-28T08:00:00-04:00")  # a plain busy event without our key
        for eid in ("p3", "p4"):
            with self.assertRaises(gc.CalendarError):
                gcal_busy.move_busy(self.svc, CAL, eid, "k", "2026-10-28T09:00", 60, TZ)
            with self.assertRaises(gc.CalendarError):
                gcal_busy.delete_busy(self.svc, CAL, eid, "k", True, "x")
        self.assertEqual(self.svc.writes(), [])


class AlertAndMainTests(Base):
    def test_alert_logs_and_posts_with_openclaw(self):
        calls = []

        def runner(cmd, **kw):
            calls.append(cmd)
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")
        alert = gs.make_alerter(self.state, "channel:C0TEST", "main", runner)
        self.assertEqual(alert("hello | world"), "sent")
        self.assertEqual(calls[0][:6], ["openclaw", "message", "send", "--channel", "slack", "--account"])
        self.assertIn("channel:C0TEST", calls[0])
        with open(os.path.join(self.state, "alerts.log")) as fh:
            self.assertIn("hello / world", fh.read())

    def test_alert_failure_is_logged_not_raised(self):
        def runner(cmd, **kw):
            return types.SimpleNamespace(returncode=1, stdout="", stderr="no System Agent owner")
        res = gs.make_alerter(self.state, "channel:C0TEST", "", runner)("x")
        self.assertIn("send failed", res)
        self.assertIn("System Agent", res)

        def raises(cmd, **kw):
            raise FileNotFoundError("openclaw")
        self.assertIn("FileNotFoundError", gs.make_alerter(self.state, "channel:C0TEST", "", raises)("x"))

    def test_alert_without_target_is_logged_only(self):
        res = gs.make_alerter(self.state, "", "", None)("x")
        self.assertIn("logged only", res)

    def main(self, argv, env=None):
        out = io.StringIO()
        old = dict(os.environ)
        os.environ.pop("LIFEOS_ALERT_TARGET", None)
        os.environ.pop("GCAL_CALENDAR", None)
        os.environ.update(env or {})
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                code = gs.main(argv, service=self.svc)
        finally:
            os.environ.clear()
            os.environ.update(old)
        return code, out.getvalue()

    def test_main_runs_end_to_end(self):
        self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
        code, out = self.main(["--calendar", CAL, "--journal", self.journal, "--state-dir", self.state])
        self.assertEqual(code, 0, out)
        self.assertIn("pushed 1", out)

    def test_main_needs_a_calendar(self):
        self.assertEqual(self.main(["--journal", self.journal, "--state-dir", self.state])[0], 2)

    def test_main_test_alert(self):
        code, out = self.main(["--test-alert", "--state-dir", self.state])
        self.assertEqual(code, 0)
        self.assertIn("logged only", out)

    def test_main_paused_exits_3_without_a_login(self):
        os.makedirs(self.state)
        open(gs.pause_path(self.state), "w").close()
        code, out = self.main(["--calendar", CAL, "--journal", self.journal, "--state-dir", self.state])
        self.assertEqual(code, 3)

    def test_main_second_run_while_locked_exits_quietly(self):
        import fcntl
        os.makedirs(self.state)
        fh = open(os.path.join(self.state, "run.lock"), "a")
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            self.write(jl(N1, "2026-10-28 07:00", "2026-10-28 08:00", "written"))
            code, out = self.main(["--calendar", CAL, "--journal", self.journal, "--state-dir", self.state])
        finally:
            fh.close()
        self.assertEqual(code, 0)
        self.assertIn("another run is active", out)
        self.assertEqual(self.svc.calls, [])

    def test_main_login_problem_is_exit_4_and_revoked_is_exit_3(self):
        def bad(msg):
            def f(token):
                raise gc.CalendarError(msg)
            return f
        old = gc.build_service
        try:
            for msg, want in (("no login file at x", 4), ("could not be refreshed (RefreshError: invalid_grant: Token has been expired or revoked.)", 3)):
                gc.build_service = bad(msg)
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    code = gs.main(["--calendar", CAL, "--journal", self.journal, "--state-dir", self.state])
                self.assertEqual(code, want, msg)
                if want == 3:
                    os.remove(gs.pause_path(self.state))
        finally:
            gc.build_service = old


if __name__ == "__main__":
    unittest.main()
