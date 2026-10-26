#!/usr/bin/env python3
"""Delete one LifeOS event by its Google event ID (APR-0074).

Every delete needs the CEO's approval first (APR-0044). The script refuses unless you pass
--ceo-approved and --approval-note (say where the CEO said yes). The title must match the event with that
ID, so a wrong ID deletes nothing. Only mandated, single, timed events can be deleted. Run with --dry-run first.
Usage: gcal_delete.py --calendar <calendar-email> --id <event-id> --title "<exact title>" \
         --ceo-approved --approval-note "Slack, 2026-10-26" [--dry-run]
"""
import argparse
import sys

import gcal_common as gc


def main(argv=None, service=None):
    p = argparse.ArgumentParser(description="Delete one LifeOS event by ID (needs CEO approval).")
    gc.add_common_args(p, write=True)
    p.add_argument("--id", required=True, help="the Google event ID")
    p.add_argument("--title", required=True, help="the exact current title of that event")
    p.add_argument("--ceo-approved", action="store_true", help="the CEO approved this delete (APR-0044)")
    p.add_argument("--approval-note", default="", help="where the CEO approved it, for the record")
    args = p.parse_args(argv)

    def action(svc):
        r = gc.delete_event(svc, args.calendar, args.id, args.title, args.ceo_approved, args.approval_note, args.dry_run)
        print("\t".join([r["action"], r["id"], r["title"], "approval: " + (r["approval"] or "(none, dry run)")]))
        return 0

    return gc.run(args, service, action)


if __name__ == "__main__":
    sys.exit(main())
