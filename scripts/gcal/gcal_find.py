#!/usr/bin/env python3
"""Find events by their exact mandated title. Read only (APR-0074).

This is the check P-28 runs before a retry, so a write that worked but looked failed is not repeated.
Usage: gcal_find.py --calendar <calendar-email> --title "CHO - Doctor Appointment - 10262026-0001"
Output: id, start, end, title, separated by tabs. No lines means no match.
"""
import argparse
import sys

import gcal_common as gc


def main(argv=None, service=None):
    p = argparse.ArgumentParser(description="Find events by exact title (read only).")
    gc.add_common_args(p)
    p.add_argument("--title", required=True, help="the full mandated title")
    args = p.parse_args(argv)

    def action(svc):
        events = gc.find_events(svc, args.calendar, args.title, args.tz)
        for event in events:
            print(gc.event_line(event))
        print("events: " + str(len(events)), file=sys.stderr)
        return 0

    return gc.run(args, service, action)


if __name__ == "__main__":
    sys.exit(main())
