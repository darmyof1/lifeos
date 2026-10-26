"""Unit tests for scripts/gcal (APR-0074). No network and no Google libraries needed.

Run from the repo root:
    python3 -B -m unittest discover -s tests/unit -p "test_gcal*.py"
"""
import contextlib
import datetime
import importlib.util
import io
import os
import pickle
import stat
import sys
import tempfile
import types
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts", "gcal"))
sys.dont_write_bytecode = True

import gcal_common as gc  # noqa: E402
import gcal_create  # noqa: E402
import gcal_delete  # noqa: E402
import gcal_find  # noqa: E402
import gcal_get  # noqa: E402
import gcal_list  # noqa: E402
import gcal_move  # noqa: E402
import gcal_roundtrip_test  # noqa: E402

CAL = "calendar-under-test"
TZ = "America/Santo_Domingo"
TITLE = "CHO - Doctor Appointment - 10262026-0001"


class FakeHttpError(Exception):
    def __init__(self, status):
        super().__init__("HTTP " + str(status))
        self.resp = types.SimpleNamespace(status=status)


class Req:
    def __init__(self, fn):
        self.fn = fn

    def execute(self):
        return self.fn()


class FakeEvents:
    def __init__(self, svc):
        self.svc = svc

    def _log(self, name, **kw):
        self.svc.calls.append((name, kw))

    def list(self, **kw):
        self._log("list", **kw)

        def run():
            t0 = datetime.datetime.fromisoformat(kw["timeMin"])
            t1 = datetime.datetime.fromisoformat(kw["timeMax"])
            hits = []
            for e in self.svc.store.values():
                s = e["start"]
                when = (datetime.datetime.fromisoformat(s["dateTime"]) if "dateTime" in s
                        else datetime.datetime.fromisoformat(s["date"]).replace(tzinfo=t0.tzinfo))
                if t0 <= when < t1:
                    hits.append(e)
            hits.sort(key=lambda e: e["start"].get("dateTime", e["start"].get("date")))
            size = self.svc.page_size
            start = int(kw.get("pageToken") or 0)
            page = hits[start:start + size] if size else hits
            out = {"items": page}
            if size and start + size < len(hits):
                out["nextPageToken"] = str(start + size)
            return out
        return Req(run)

    def get(self, calendarId, eventId):
        self._log("get", eventId=eventId)

        def run():
            if eventId not in self.svc.store:
                raise FakeHttpError(410 if eventId in self.svc.deleted else 404)
            return dict(self.svc.store[eventId])
        return Req(run)

    def insert(self, calendarId, body):
        self._log("insert", body=body)

        def run():
            self.svc.counter += 1
            eid = "new" + str(self.svc.counter)
            self.svc.store[eid] = dict(body, id=eid)
            return {"id": eid}
        return Req(run)

    def patch(self, calendarId, eventId, body):
        self._log("patch", eventId=eventId, body=body)

        def run():
            if self.svc.fail_patch:
                raise FakeHttpError(500)
            self.svc.store[eventId].update(body)
            return dict(self.svc.store[eventId])
        return Req(run)

    def delete(self, calendarId, eventId):
        self._log("delete", eventId=eventId)

        def run():
            if self.svc.keep_on_delete:
                return ""
            self.svc.deleted.add(eventId)
            del self.svc.store[eventId]
            return ""
        return Req(run)


class FakeService:
    def __init__(self, page_size=0):
        self.store, self.calls, self.deleted = {}, [], set()
        self.counter, self.page_size = 0, page_size
        self.fail_patch, self.keep_on_delete = False, False
        self.add("doc1", TITLE, "2026-10-26T07:00:00-04:00", "2026-10-26T07:30:00-04:00")
        self.add("gym1", "Health | Gym Fiscal Bill", None, None, all_day=("2026-10-25", "2026-10-31"))
        self.add("series1", "CHO - Weekly Run - 10262026-0002", "2026-10-26T18:00:00-04:00",
                 "2026-10-26T19:00:00-04:00", recurringEventId="series0")

    def add(self, eid, title, start, end, all_day=None, **extra):
        if all_day:
            ev = {"id": eid, "summary": title, "start": {"date": all_day[0]}, "end": {"date": all_day[1]}}
        else:
            ev = {"id": eid, "summary": title, "start": {"dateTime": start}, "end": {"dateTime": end}}
        ev.update(extra)
        self.store[eid] = ev

    def events(self):
        return FakeEvents(self)

    def writes(self):
        return [c for c in self.calls if c[0] in ("insert", "patch", "delete")]


def run_main(module, argv, svc):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = module.main(argv, service=svc)
    return code, out.getvalue(), err.getvalue()


class TitleAndTimeTests(unittest.TestCase):
    def test_good_titles(self):
        self.assertEqual(gc.validate_title(TITLE), datetime.date(2026, 10, 26))
        for dom in gc.DOMAINS:
            self.assertIsNotNone(gc.title_date(dom + " - X - 01022026-0001"))

    def test_bad_titles(self):
        bad = ["", None, "Doctor", "XXX - Doctor - 10262026-0001", "CHO - Doctor - 13262026-0001",
               "CHO - Doctor - 10262026-001", "CHO - Doctor - 2026-10-26-0001", "CHO -  - 10262026-0001",
               "CHO - Doctor  - 10262026-0001", "cho - Doctor - 10262026-0001", "CHO - Doctor - 10262026-0001 "]
        for t in bad:
            self.assertIsNone(gc.title_date(t), t)
        with self.assertRaises(gc.CalendarError):
            gc.validate_title("Doctor")

    def test_title_may_contain_dashes(self):
        self.assertIsNotNone(gc.title_date("CHO - Follow - up visit - 10262026-0001"))

    def test_parse_local(self):
        dt = gc.parse_local("2026-10-26T07:00", TZ)
        self.assertEqual(gc.iso(dt), "2026-10-26T07:00:00-04:00")
        for bad in ["tomorrow", "2026-10-26T07:00-04:00", "2026-10-26T07:00Z", None]:
            with self.assertRaises(gc.CalendarError):
                gc.parse_local(bad, TZ)

    def test_google_time_with_z_or_offset(self):
        self.assertEqual(gc.parse_google_time("2026-10-26T11:00:00Z"), datetime.datetime(2026, 10, 26, 11, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(gc.iso(gc.parse_google_time("2026-10-26T07:00:00-04:00")), "2026-10-26T07:00:00-04:00")

    def test_move_works_when_google_returns_z_times(self):
        svc = FakeService()
        svc.store["doc1"]["start"]["dateTime"] = "2026-10-26T11:00:00Z"
        svc.store["doc1"]["end"]["dateTime"] = "2026-10-26T11:30:00Z"
        gc.move_event(svc, CAL, "doc1", "2026-10-26T08:00", tz=TZ)
        patch = [c for c in svc.calls if c[0] == "patch"][0][1]["body"]
        self.assertEqual(patch["end"]["dateTime"], "2026-10-26T08:30:00-04:00")

    def test_minutes(self):
        for bad in [0, -5, 1441, "30", None]:
            with self.assertRaises(gc.CalendarError):
                gc.check_minutes(bad)
        self.assertEqual(gc.check_minutes(30), 30)

    def test_event_body_has_title_start_end_only(self):
        body = gc.event_body(TITLE, gc.parse_local("2026-10-26T07:00", TZ), 30, TZ)
        self.assertEqual(sorted(body), ["end", "start", "summary"])
        self.assertEqual(body["end"]["dateTime"], "2026-10-26T07:30:00-04:00")

    def test_event_line_is_one_tab_line(self):
        line = gc.event_line({"id": "a", "summary": "x\ty\nz", "start": {"date": "2026-10-25"}, "end": {"date": "2026-10-26"}})
        self.assertEqual(line, "a\t2026-10-25\t2026-10-26\tx y z")


class ReadTests(unittest.TestCase):
    def test_list_range_and_order(self):
        svc = FakeService()
        events = gc.list_events(svc, CAL, datetime.date(2026, 10, 25), datetime.date(2026, 10, 27), TZ)
        self.assertEqual([e["id"] for e in events], ["gym1", "doc1", "series1"])

    def test_list_end_not_included(self):
        svc = FakeService()
        events = gc.list_events(svc, CAL, datetime.date(2026, 10, 26), datetime.date(2026, 10, 27), TZ)
        self.assertNotIn("gym1", [e["id"] for e in events])

    def test_list_bad_range(self):
        with self.assertRaises(gc.CalendarError):
            gc.list_events(FakeService(), CAL, datetime.date(2026, 10, 27), datetime.date(2026, 10, 27), TZ)

    def test_list_pages(self):
        svc = FakeService(page_size=1)
        events = gc.list_events(svc, CAL, datetime.date(2026, 10, 25), datetime.date(2026, 10, 27), TZ)
        self.assertEqual(len(events), 3)
        self.assertEqual(len([c for c in svc.calls if c[0] == "list"]), 3)

    def test_list_leaves_out_cancelled(self):
        svc = FakeService()
        svc.store["doc1"]["status"] = "cancelled"
        events = gc.list_events(svc, CAL, datetime.date(2026, 10, 25), datetime.date(2026, 10, 27), TZ)
        self.assertNotIn("doc1", [e["id"] for e in events])

    def test_find_exact_title_only(self):
        svc = FakeService()
        svc.add("near", "CHO - Doctor Appointment - 10262026-0010", "2026-10-26T09:00:00-04:00", "2026-10-26T09:30:00-04:00")
        found = gc.find_events(svc, CAL, TITLE, TZ)
        self.assertEqual([e["id"] for e in found], ["doc1"])
        self.assertEqual(gc.find_events(svc, CAL, "CHO - Nothing - 10262026-0099", TZ), [])

    def test_find_needs_mandated_title(self):
        with self.assertRaises(gc.CalendarError):
            gc.find_events(FakeService(), CAL, "Doctor", TZ)

    def test_get_missing_and_deleted(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError):
            gc.get_event(svc, CAL, "nope")
        svc.deleted.add("gone")
        with self.assertRaises(gc.CalendarError):
            gc.get_event(svc, CAL, "gone")

    def test_get_other_error_passes_through(self):
        svc = FakeService()
        svc.events = lambda: types.SimpleNamespace(get=lambda **kw: Req(lambda: (_ for _ in ()).throw(FakeHttpError(500))))
        with self.assertRaises(FakeHttpError):
            gc.get_event(svc, CAL, "x")


class CreateTests(unittest.TestCase):
    def test_create_sends_title_start_end_only(self):
        svc = FakeService()
        r = gc.create_event(svc, CAL, "COS - Test - 10272026-0001", "2026-10-27T09:00", 45, TZ)
        self.assertEqual(r["action"], "created")
        sent = [c for c in svc.calls if c[0] == "insert"][0][1]["body"]
        self.assertEqual(sorted(sent), ["end", "start", "summary"])
        self.assertEqual(sent["end"]["dateTime"], "2026-10-27T09:45:00-04:00")
        self.assertIn(r["id"], svc.store)

    def test_create_dry_run_writes_nothing(self):
        svc = FakeService()
        r = gc.create_event(svc, CAL, "COS - Test - 10272026-0001", "2026-10-27T09:00", 30, TZ, dry_run=True)
        self.assertEqual(r["action"], "dry-run create")
        self.assertEqual(svc.writes(), [])

    def test_create_refuses_duplicate(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError) as cm:
            gc.create_event(svc, CAL, TITLE, "2026-10-26T07:00", 30, TZ)
        self.assertIn("duplicate", str(cm.exception))
        self.assertEqual(svc.writes(), [])

    def test_create_refuses_date_mismatch(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError):
            gc.create_event(svc, CAL, "COS - Test - 10272026-0001", "2026-10-28T09:00", 30, TZ)
        self.assertEqual(svc.writes(), [])

    def test_create_refuses_bad_title_time_minutes(self):
        svc = FakeService()
        for args in [("Doctor", "2026-10-27T09:00", 30), ("COS - Test - 10272026-0001", "later", 30),
                     ("COS - Test - 10272026-0001", "2026-10-27T09:00", 0)]:
            with self.assertRaises(gc.CalendarError):
                gc.create_event(svc, CAL, *args, tz=TZ)
        self.assertEqual(svc.writes(), [])


class MoveTests(unittest.TestCase):
    def test_move_same_day_keeps_title_and_length(self):
        svc = FakeService()
        r = gc.move_event(svc, CAL, "doc1", "2026-10-26T08:00", tz=TZ)
        self.assertEqual(r["action"], "moved")
        patch = [c for c in svc.calls if c[0] == "patch"][0][1]["body"]
        self.assertNotIn("summary", patch)
        self.assertEqual(patch["start"]["dateTime"], "2026-10-26T08:00:00-04:00")
        self.assertEqual(patch["end"]["dateTime"], "2026-10-26T08:30:00-04:00")

    def test_move_new_length(self):
        svc = FakeService()
        gc.move_event(svc, CAL, "doc1", "2026-10-26T08:00", minutes=60, tz=TZ)
        patch = [c for c in svc.calls if c[0] == "patch"][0][1]["body"]
        self.assertEqual(patch["end"]["dateTime"], "2026-10-26T09:00:00-04:00")

    def test_move_other_day_needs_new_title(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError) as cm:
            gc.move_event(svc, CAL, "doc1", "2026-10-27T07:00", tz=TZ)
        self.assertIn("--new-title", str(cm.exception))
        self.assertEqual(svc.writes(), [])

    def test_move_other_day_with_new_title(self):
        svc = FakeService()
        new = "CHO - Doctor Appointment - 10272026-0001"
        gc.move_event(svc, CAL, "doc1", "2026-10-27T07:00", new_title=new, tz=TZ)
        patch = [c for c in svc.calls if c[0] == "patch"][0][1]["body"]
        self.assertEqual(patch["summary"], new)

    def test_move_new_title_must_match_new_date_and_be_mandated(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError):
            gc.move_event(svc, CAL, "doc1", "2026-10-27T07:00", new_title="Doctor", tz=TZ)
        with self.assertRaises(gc.CalendarError):
            gc.move_event(svc, CAL, "doc1", "2026-10-27T07:00", new_title="CHO - Doctor Appointment - 10282026-0001", tz=TZ)
        self.assertEqual(svc.writes(), [])

    def test_move_refuses_new_title_that_exists(self):
        svc = FakeService()
        svc.add("other", "CHO - Doctor Appointment - 10272026-0001", "2026-10-27T07:00:00-04:00", "2026-10-27T07:30:00-04:00")
        with self.assertRaises(gc.CalendarError):
            gc.move_event(svc, CAL, "doc1", "2026-10-27T07:00", new_title="CHO - Doctor Appointment - 10272026-0001", tz=TZ)
        self.assertEqual(svc.writes(), [])

    def test_move_refuses_personal_recurring_and_all_day(self):
        svc = FakeService()
        for eid in ["gym1", "series1", "nope"]:
            with self.assertRaises(gc.CalendarError):
                gc.move_event(svc, CAL, eid, "2026-10-26T08:00", tz=TZ)
        svc.add("allday", "CHO - Fast - 10262026-0003", None, None, all_day=("2026-10-26", "2026-10-27"))
        with self.assertRaises(gc.CalendarError):
            gc.move_event(svc, CAL, "allday", "2026-10-26T08:00", tz=TZ)
        self.assertEqual(svc.writes(), [])

    def test_move_refuses_a_personal_timed_event(self):
        svc = FakeService()
        svc.add("lunch1", "Lunch with a friend", "2026-10-26T12:00:00-04:00", "2026-10-26T13:00:00-04:00")
        with self.assertRaises(gc.CalendarError) as cm:
            gc.move_event(svc, CAL, "lunch1", "2026-10-26T14:00", tz=TZ)
        self.assertIn("not a LifeOS event", str(cm.exception))
        self.assertNotIn("Lunch", str(cm.exception))
        self.assertEqual(svc.writes(), [])

    def test_move_nothing_to_change(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError):
            gc.move_event(svc, CAL, "doc1", "2026-10-26T07:00", tz=TZ)

    def test_move_dry_run(self):
        svc = FakeService()
        r = gc.move_event(svc, CAL, "doc1", "2026-10-26T08:00", tz=TZ, dry_run=True)
        self.assertEqual(r["action"], "dry-run move")
        self.assertEqual(svc.writes(), [])

    def test_personal_title_is_not_echoed(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError) as cm:
            gc.move_event(svc, CAL, "gym1", "2026-10-26T08:00", tz=TZ)
        self.assertNotIn("Gym", str(cm.exception))


class DeleteTests(unittest.TestCase):
    def test_delete_needs_approval_flag_and_note(self):
        svc = FakeService()
        for kw in [dict(), dict(approved=True), dict(approved=True, approval_note="  "), dict(approval_note="Slack")]:
            with self.assertRaises(gc.CalendarError):
                gc.delete_event(svc, CAL, "doc1", TITLE, **kw)
        self.assertEqual(svc.writes(), [])
        self.assertIn("doc1", svc.store)

    def test_delete_title_must_match(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError):
            gc.delete_event(svc, CAL, "doc1", "CHO - Other - 10262026-0001", True, "Slack")
        self.assertEqual(svc.writes(), [])

    def test_delete_refuses_personal_recurring(self):
        svc = FakeService()
        with self.assertRaises(gc.CalendarError):
            gc.delete_event(svc, CAL, "gym1", "Health | Gym Fiscal Bill", True, "Slack")
        with self.assertRaises(gc.CalendarError):
            gc.delete_event(svc, CAL, "series1", "CHO - Weekly Run - 10262026-0002", True, "Slack")
        self.assertEqual(svc.writes(), [])

    def test_delete_refuses_a_personal_timed_event_even_with_its_exact_title(self):
        svc = FakeService()
        svc.add("lunch1", "Lunch with a friend", "2026-10-26T12:00:00-04:00", "2026-10-26T13:00:00-04:00")
        with self.assertRaises(gc.CalendarError) as cm:
            gc.delete_event(svc, CAL, "lunch1", "Lunch with a friend", True, "Slack")
        self.assertIn("not a LifeOS event", str(cm.exception))
        self.assertEqual(svc.writes(), [])
        self.assertIn("lunch1", svc.store)

    def test_delete_works_and_is_verified(self):
        svc = FakeService()
        r = gc.delete_event(svc, CAL, "doc1", TITLE, True, "Slack, 2026-10-26")
        self.assertEqual(r["action"], "deleted")
        self.assertNotIn("doc1", svc.store)

    def test_delete_that_did_not_take_effect_is_an_error(self):
        svc = FakeService()
        svc.keep_on_delete = True
        with self.assertRaises(gc.CalendarError) as cm:
            gc.delete_event(svc, CAL, "doc1", TITLE, True, "Slack")
        self.assertIn("still there", str(cm.exception))

    def test_delete_dry_run_needs_no_approval_and_writes_nothing(self):
        svc = FakeService()
        r = gc.delete_event(svc, CAL, "doc1", TITLE, dry_run=True)
        self.assertEqual(r["action"], "dry-run delete")
        self.assertEqual(svc.writes(), [])


class CommandLineTests(unittest.TestCase):
    def test_list_prints_lines_and_count(self):
        code, out, err = run_main(gcal_list, ["--calendar", CAL, "--from", "2026-10-25", "--to", "2026-10-27"], FakeService())
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().split("\n")), 3)
        self.assertIn("doc1\t2026-10-26T07:00:00-04:00\t2026-10-26T07:30:00-04:00\t" + TITLE, out)
        self.assertIn("events: 3", err)

    def test_find_and_get(self):
        code, out, err = run_main(gcal_find, ["--calendar", CAL, "--title", TITLE], FakeService())
        self.assertEqual((code, out.count("\n")), (0, 1))
        code, out, err = run_main(gcal_get, ["--calendar", CAL, "--id", "doc1"], FakeService())
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("doc1\t"))
        code, out, err = run_main(gcal_get, ["--calendar", CAL, "--id", "missing"], FakeService())
        self.assertEqual(code, 1)
        self.assertIn("no event with that ID", err)

    def test_create_dry_run_then_real(self):
        svc = FakeService()
        argv = ["--calendar", CAL, "--title", "COS - Test - 10272026-0001", "--start", "2026-10-27T09:00"]
        code, out, err = run_main(gcal_create, argv + ["--dry-run"], svc)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("dry-run create\t"))
        self.assertEqual(svc.writes(), [])
        code, out, err = run_main(gcal_create, argv, svc)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("created\tnew1\t"))

    def test_move_and_delete_commands(self):
        svc = FakeService()
        code, out, err = run_main(gcal_move, ["--calendar", CAL, "--id", "doc1", "--start", "2026-10-26T08:00"], svc)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("moved\tdoc1\t2026-10-26T08:00:00-04:00"))
        base = ["--calendar", CAL, "--id", "doc1", "--title", TITLE]
        code, out, err = run_main(gcal_delete, base, svc)
        self.assertEqual(code, 1)
        self.assertIn("APR-0044", err)
        code, out, err = run_main(gcal_delete, base + ["--ceo-approved", "--approval-note", "Slack"], svc)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("deleted\tdoc1\t"))

    def test_missing_calendar_is_an_error(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GCAL_CALENDAR", None)
            code, out, err = run_main(gcal_list, ["--from", "2026-10-25", "--to", "2026-10-26"], FakeService())
        self.assertEqual(code, 1)
        self.assertIn("--calendar is required", err)

    def test_unexpected_api_error_is_reported_not_raised(self):
        svc = FakeService()
        svc.fail_patch = True
        code, out, err = run_main(gcal_move, ["--calendar", CAL, "--id", "doc1", "--start", "2026-10-26T08:00"], svc)
        self.assertEqual(code, 1)
        self.assertIn("HTTP 500", err)


class RoundTripTests(unittest.TestCase):
    def test_round_trip_leaves_nothing_behind(self):
        svc = FakeService()
        code, out, err = run_main(gcal_roundtrip_test, ["--calendar", CAL, "--date", "2026-10-26", "--ceo-approved"], svc)
        self.assertEqual(code, 0)
        for n in ("1 created", "2 moved to: 2026-10-26T07:30:00-04:00", "3 read by id: True", "4 deleted by id"):
            self.assertIn(n, out)
        self.assertEqual(sorted(svc.store), ["doc1", "gym1", "series1"])

    def test_round_trip_deletes_even_if_the_move_fails(self):
        svc = FakeService()
        svc.fail_patch = True
        code, out, err = run_main(gcal_roundtrip_test, ["--calendar", CAL, "--date", "2026-10-26", "--ceo-approved"], svc)
        self.assertEqual(code, 1)
        self.assertIn("4 deleted by id", out)
        self.assertEqual(sorted(svc.store), ["doc1", "gym1", "series1"])

    def test_round_trip_needs_approval_flag(self):
        svc = FakeService()
        code, out, err = run_main(gcal_roundtrip_test, ["--calendar", CAL, "--date", "2026-10-26"], svc)
        self.assertEqual(code, 1)
        self.assertIn("APR-0044", err)
        self.assertEqual(svc.writes(), [])

    def test_round_trip_dry_run(self):
        svc = FakeService()
        code, out, err = run_main(gcal_roundtrip_test, ["--calendar", CAL, "--date", "2026-10-26", "--dry-run"], svc)
        self.assertEqual(code, 0)
        self.assertEqual(svc.writes(), [])


class LoginFileTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "oauth")

    def tearDown(self):
        self.dir.cleanup()

    def write(self, mode, obj=None):
        with open(self.path, "wb") as fh:
            pickle.dump(obj if obj is not None else DummyCreds(), fh)
        os.chmod(self.path, mode)

    def test_missing_file(self):
        with self.assertRaises(gc.CalendarError):
            gc.load_credentials(self.path)

    def test_refuses_open_mode(self):
        self.write(0o644)
        with self.assertRaises(gc.CalendarError) as cm:
            gc.load_credentials(self.path)
        self.assertIn("chmod 600", str(cm.exception))

    def test_refuses_symlink(self):
        self.write(0o600)
        link = os.path.join(self.dir.name, "link")
        os.symlink(self.path, link)
        with self.assertRaises(gc.CalendarError):
            gc.load_credentials(link)

    def test_refuses_json_or_other_objects(self):
        self.write(0o600, obj={"not": "credentials"})
        with self.assertRaises(gc.CalendarError):
            gc.load_credentials(self.path)

    def test_missing_google_libraries_gives_a_clear_message(self):
        mod = types.ModuleType("fake_google_module")

        class Creds:
            pass

        Creds.__module__ = "fake_google_module"
        Creds.__qualname__ = "Creds"
        mod.Creds = Creds
        sys.modules["fake_google_module"] = mod
        try:
            data = pickle.dumps(Creds())
        finally:
            del sys.modules["fake_google_module"]
        with open(self.path, "wb") as fh:
            fh.write(data)
        os.chmod(self.path, 0o600)
        with self.assertRaises(gc.CalendarError) as cm:
            gc.load_credentials(self.path)
        self.assertIn("Google libraries are missing", str(cm.exception))

    def test_corrupt_login_file_gives_a_clear_message(self):
        with open(self.path, "wb") as fh:
            fh.write(b"not a pickle")
        os.chmod(self.path, 0o600)
        with self.assertRaises(gc.CalendarError) as cm:
            gc.load_credentials(self.path)
        self.assertIn("could not be read", str(cm.exception))

    def test_loads_a_closed_valid_login(self):
        self.write(0o600)
        self.assertTrue(gc.load_credentials(self.path).valid)
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o600)


class DummyCreds:
    valid = True

    def refresh(self, request):
        pass


@unittest.skipUnless(importlib.util.find_spec("googleapiclient"), "Google libraries not installed")
class RequestShapeTests(unittest.TestCase):
    """With the real Google client, check the requests the functions build (nothing is sent)."""

    def test_requests(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import HttpRequest

        service = build("calendar", "v3", credentials=Credentials(token="not-a-real-token"), cache_discovery=False)
        event = {"id": "ev1", "summary": TITLE, "start": {"dateTime": "2026-10-26T07:00:00-04:00"},
                 "end": {"dateTime": "2026-10-26T07:30:00-04:00"}}
        queue, seen = [], []

        def fake_execute(self, http=None, num_retries=0):
            seen.append((self.method, self.uri, self.body))
            item = queue.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

        with mock.patch.object(HttpRequest, "execute", fake_execute):
            queue[:] = [{"items": []}]
            gc.list_events(service, "calendar-under-test", datetime.date(2026, 10, 25), datetime.date(2026, 10, 27), TZ)
            m, uri, body = seen[-1]
            self.assertEqual(m, "GET")
            for part in ("/calendars/calendar-under-test/events?", "singleEvents=true", "orderBy=startTime",
                         "timeMin=2026-10-25T00%3A00%3A00-04%3A00", "timeMax=2026-10-27T00%3A00%3A00-04%3A00"):
                self.assertIn(part, uri)

            seen.clear()
            queue[:] = [{"items": []}, {"id": "new1"}]
            gc.create_event(service, "calendar-under-test", "COS - Test - 10272026-0001", "2026-10-27T09:00", 30, TZ)
            self.assertEqual([s[0] for s in seen], ["GET", "POST"])
            self.assertTrue(seen[1][1].split("?")[0].endswith("/calendars/calendar-under-test/events"))
            self.assertIn('"summary": "COS - Test - 10272026-0001"', seen[1][2])

            seen.clear()
            queue[:] = [dict(event), dict(event)]
            gc.move_event(service, "calendar-under-test", "ev1", "2026-10-26T08:00", tz=TZ)
            self.assertEqual([s[0] for s in seen], ["GET", "PATCH"])
            self.assertTrue(seen[1][1].split("?")[0].endswith("/events/ev1"))

            seen.clear()
            queue[:] = [dict(event), "", FakeHttpError(410)]
            gc.delete_event(service, "calendar-under-test", "ev1", TITLE, True, "Slack")
            self.assertEqual([s[0] for s in seen], ["GET", "DELETE", "GET"])
            self.assertTrue(seen[1][1].split("?")[0].endswith("/events/ev1"))


if __name__ == "__main__":
    unittest.main()
