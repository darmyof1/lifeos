#!/usr/bin/env python3
"""List events in a date range with their Google event IDs. Read only (APR-0074).

Usage: gcal_list.py --calendar <calendar-email> --from 2026-10-25 --to 2026-10-27
The end date is not included. Output: id, start, end, title, separated by tabs.
"""
import argparse
import sys

import gcal_common as gc


def main(argv=None, service=None):
    p = argparse.ArgumentParser(description="List events with their Google IDs (read only).")
    gc.add_common_args(p)
    p.add_argument("--from", dest="day_from", required=True, help="first day, YYYY-MM-DD")
    p.add_argument("--to", dest="day_to", required=True, help="end day, YYYY-MM-DD (not included)")
    args = p.parse_args(argv)

    def action(svc):
        events = gc.list_events(svc, args.calendar, gc.parse_day(args.day_from), gc.parse_day(args.day_to), args.tz)
        for event in events:
            print(gc.event_line(event))
        print("events: " + str(len(events)), file=sys.stderr)
        return 0

    return gc.run(args, service, action)


if __name__ == "__main__":
    sys.exit(main())
