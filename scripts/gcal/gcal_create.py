#!/usr/bin/env python3
"""Create one event and print its Google event ID (APR-0074).

Only the title, start and end go to Google (APR-0032). The title must follow the mandate
<DOMAIN> - <Title> - <MMDDYYYY>-<NNNN> and its date must be the start date. An event with the same
title is never created twice. Run with --dry-run first.
Usage: gcal_create.py --calendar <calendar-email> --title "CHO - Doctor Appointment - 10262026-0001" \
         --start 2026-10-26T07:00 --minutes 30 [--dry-run]
"""
import argparse
import sys

import gcal_common as gc


def main(argv=None, service=None):
    p = argparse.ArgumentParser(description="Create one event (writes unless --dry-run).")
    gc.add_common_args(p, write=True)
    p.add_argument("--title", required=True, help="the full mandated title")
    p.add_argument("--start", required=True, help="local start, 2026-10-26T07:00")
    p.add_argument("--minutes", type=int, default=30, help="length in minutes (default 30)")
    args = p.parse_args(argv)

    def action(svc):
        r = gc.create_event(svc, args.calendar, args.title, args.start, args.minutes, args.tz, args.dry_run)
        body = r["body"]
        print("\t".join([r["action"], r["id"], body["start"]["dateTime"], body["end"]["dateTime"], body["summary"]]))
        return 0

    return gc.run(args, service, action)


if __name__ == "__main__":
    sys.exit(main())
