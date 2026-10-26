#!/usr/bin/env python3
"""Move one LifeOS event to a new start, by its Google event ID (APR-0074).

The length stays the same unless --minutes is given. The title carries the event date (APR-0035), so
moving to another day needs --new-title with the new date. Only mandated, single, timed events can be
moved. Run with --dry-run first.
Usage: gcal_move.py --calendar <calendar-email> --id <event-id> --start 2026-10-26T07:30 [--dry-run]
"""
import argparse
import sys

import gcal_common as gc


def main(argv=None, service=None):
    p = argparse.ArgumentParser(description="Move one LifeOS event by ID (writes unless --dry-run).")
    gc.add_common_args(p, write=True)
    p.add_argument("--id", required=True, help="the Google event ID")
    p.add_argument("--start", required=True, help="new local start, 2026-10-26T07:30")
    p.add_argument("--minutes", type=int, default=None, help="new length in minutes (default: keep the length)")
    p.add_argument("--new-title", default=None, help="new mandated title, needed when the date changes")
    args = p.parse_args(argv)

    def action(svc):
        r = gc.move_event(svc, args.calendar, args.id, args.start, args.minutes, args.new_title, args.tz, args.dry_run)
        body = r["body"]
        print("\t".join([r["action"], r["id"], body["start"]["dateTime"], body["end"]["dateTime"], r["title"]]))
        return 0

    return gc.run(args, service, action)


if __name__ == "__main__":
    sys.exit(main())
