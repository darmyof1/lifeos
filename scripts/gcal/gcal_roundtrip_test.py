#!/usr/bin/env python3
"""Round-trip test of the REST scripts on one test event (APR-0074).

Creates a test event, moves it 30 minutes later, reads it back by ID, then deletes it by ID.
The event is deleted even if a step fails. It uses the title COS - REST API test - <MMDDYYYY>-9001
(counters from 9001 up are for tests). Deleting needs the CEO's approval (APR-0044): pass --ceo-approved.
Usage: gcal_roundtrip_test.py --calendar <calendar-email> --date 2026-10-26 --ceo-approved [--dry-run]
"""
import argparse
import sys

import gcal_common as gc


def main(argv=None, service=None):
    p = argparse.ArgumentParser(description="Create, move, read and delete one test event.")
    gc.add_common_args(p, write=True)
    p.add_argument("--date", required=True, help="test day, YYYY-MM-DD")
    p.add_argument("--ceo-approved", action="store_true", help="the CEO approved deleting the test event")
    args = p.parse_args(argv)

    def action(svc):
        day = gc.parse_day(args.date)
        title = "COS - REST API test - " + day.strftime("%m%d%Y") + "-9001"
        if args.dry_run:
            r = gc.create_event(svc, args.calendar, title, day.isoformat() + "T07:00", 30, args.tz, True)
            print("dry-run: would create, move, read and delete: " + r["body"]["summary"])
            return 0
        if not args.ceo_approved:
            raise gc.CalendarError("the test deletes its event, which needs the CEO's approval (APR-0044): "
                                   "pass --ceo-approved")
        created = gc.create_event(svc, args.calendar, title, day.isoformat() + "T07:00", 30, args.tz)
        event_id = created["id"]
        print("1 created: " + event_id)
        ok = False
        try:
            moved = gc.move_event(svc, args.calendar, event_id, day.isoformat() + "T07:30", None, None, args.tz)
            print("2 moved to: " + moved["body"]["start"]["dateTime"])
            read = gc.get_event(svc, args.calendar, event_id)
            if read.get("id") != event_id or read.get("summary") != title:
                raise gc.CalendarError("the event read back by ID does not match")
            print("3 read by id: True " + read["summary"])
            ok = True
        finally:
            try:
                gc.delete_event(svc, args.calendar, event_id, title, True, "round-trip test run by the CEO")
                print("4 deleted by id: " + event_id)
            except Exception as exc:
                print("4 DELETE FAILED for ID " + event_id + ": " + str(exc), file=sys.stderr)
                ok = False
        return 0 if ok else 1

    return gc.run(args, service, action)


if __name__ == "__main__":
    sys.exit(main())
