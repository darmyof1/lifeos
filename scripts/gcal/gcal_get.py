#!/usr/bin/env python3
"""Show one event by its Google event ID. Read only (APR-0074).

Usage: gcal_get.py --calendar <calendar-email> --id <event-id>
Output: id, start, end, title, separated by tabs. Exit 1 if there is no such event.
"""
import argparse
import sys

import gcal_common as gc


def main(argv=None, service=None):
    p = argparse.ArgumentParser(description="Show one event by ID (read only).")
    gc.add_common_args(p)
    p.add_argument("--id", required=True, help="the Google event ID")
    args = p.parse_args(argv)

    def action(svc):
        print(gc.event_line(gc.get_event(svc, args.calendar, args.id)))
        return 0

    return gc.run(args, service, action)


if __name__ == "__main__":
    sys.exit(main())
