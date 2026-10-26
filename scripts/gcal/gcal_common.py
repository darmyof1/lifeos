"""Shared code for the Google Calendar REST scripts (APR-0074).

One function per scenario: list, find by title, get by ID, create, move, delete.
The scripts next to this file are thin command line wrappers around these functions.

Rules carried here:
- Only the title, start and end go to Google (APR-0032).
- Every event title follows the mandate <DOMAIN> - <Title> - <MMDDYYYY>-<NNNN> (APR-0034, APR-0035, APR-0037).
- Only mandated, single events can be moved or deleted. Personal events are never touched.
- Every delete needs the CEO's approval first (APR-0044).

The Google libraries are imported only when a real service is built, so the unit tests need none.
"""
import datetime
import os
import pickle
import re
import stat
from zoneinfo import ZoneInfo

DEFAULT_TOKEN = "~/.local/share/gcalcli/oauth"  # APR-0041: VM only, mode 600
DEFAULT_TZ = "America/Santo_Domingo"
DOMAINS = ("CHO", "CSP", "CDO", "CFO", "CFA", "CLO", "CSO", "CCO", "COO", "COS")
TITLE_RE = re.compile(r"^(" + "|".join(DOMAINS) + r") - (.+) - (\d{8})-(\d{4})$")


class CalendarError(Exception):
    """A refusal or failure with a message meant for the person running the script."""


# ---------------------------------------------------------------- titles and times

def title_date(title):
    """Return the date inside a mandated title, or None if the title does not follow the mandate."""
    m = TITLE_RE.match(title or "")
    if not m or m.group(2) != m.group(2).strip():
        return None
    try:
        return datetime.datetime.strptime(m.group(3), "%m%d%Y").date()
    except ValueError:
        return None


def validate_title(title):
    """Return the date inside the title, or raise if the title is not mandated (APR-0034)."""
    d = title_date(title)
    if d is None:
        raise CalendarError(
            "the title must follow <DOMAIN> - <Title> - <MMDDYYYY>-<NNNN> with a real date "
            "and a domain from " + ", ".join(DOMAINS) + " (APR-0034, APR-0035, APR-0037): " + repr(title))
    return d


def parse_local(text, tz=DEFAULT_TZ):
    """Parse a local time such as 2026-10-26T07:00 (no offset) in the given time zone."""
    try:
        dt = datetime.datetime.fromisoformat(text)
    except (ValueError, TypeError):
        raise CalendarError("time must look like 2026-10-26T07:00: " + repr(text))
    if dt.tzinfo is not None:
        raise CalendarError("give the local time without an offset, for example 2026-10-26T07:00")
    return dt.replace(tzinfo=ZoneInfo(tz))


def parse_google_time(text):
    """Parse a time returned by Google. Older Pythons do not accept a trailing Z."""
    return datetime.datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)


def parse_day(text):
    try:
        return datetime.date.fromisoformat(text)
    except (ValueError, TypeError):
        raise CalendarError("date must look like 2026-10-26: " + repr(text))


def check_minutes(minutes):
    if not isinstance(minutes, int) or minutes < 1 or minutes > 1440:
        raise CalendarError("minutes must be a whole number from 1 to 1440")
    return minutes


def iso(dt):
    return dt.isoformat(timespec="seconds")


def event_body(title, start, minutes, tz=DEFAULT_TZ):
    """The request body for a new event: title, start and end only (APR-0032)."""
    end = start + datetime.timedelta(minutes=minutes)
    return {
        "summary": title,
        "start": {"dateTime": iso(start), "timeZone": tz},
        "end": {"dateTime": iso(end), "timeZone": tz},
    }


def event_line(event):
    """One tab-separated line: id, start, end, title."""
    start = event.get("start", {})
    end = event.get("end", {})
    title = re.sub(r"[\t\r\n]+", " ", event.get("summary", "(no title)"))
    return "\t".join([
        event.get("id", ""),
        start.get("dateTime", start.get("date", "")),
        end.get("dateTime", end.get("date", "")),
        title,
    ])


# ---------------------------------------------------------------- login and service

def load_credentials(path=DEFAULT_TOKEN):
    """Load the gcalcli login. It is a pickled Google credentials object, not JSON.

    The file is only read. It must be a regular file owned by this user and closed to others (APR-0041),
    because loading a pickle runs code from the file.
    """
    p = os.path.expanduser(path)
    try:
        st = os.lstat(p)
    except FileNotFoundError:
        raise CalendarError("no login file at " + p + ". Run gcalcli init first (guides/calendar-gcalcli.md).")
    if not stat.S_ISREG(st.st_mode):
        raise CalendarError("the login file is not a regular file: " + p)
    if st.st_uid != os.getuid():
        raise CalendarError("the login file is not owned by this user: " + p)
    if st.st_mode & 0o077:
        raise CalendarError("the login file is readable by others. Run: chmod 600 " + p)
    try:
        with open(p, "rb") as fh:
            creds = pickle.load(fh)
    except ImportError:
        raise CalendarError("the Google libraries are missing. Run this with the gcalcli Python: "
                            "~/.local/share/pipx/venvs/gcalcli/bin/python")
    except Exception as exc:
        raise CalendarError("the login file could not be read (" + type(exc).__name__ + "): " + p)
    if not (hasattr(creds, "valid") and hasattr(creds, "refresh")):
        raise CalendarError("the login file does not hold a Google login: " + p)
    if not creds.valid:
        from google.auth.transport.requests import Request
        try:
            creds.refresh(Request())
        except Exception as exc:
            raise CalendarError(
                "the Google login could not be refreshed (" + type(exc).__name__ + ": " + str(exc)[:200] +
                "). It may have expired or been revoked: see guides/calendar-gcalcli.md, Troubleshooting.")
    return creds


def build_service(token_path=DEFAULT_TOKEN):
    """A real Google Calendar service. Needs the Google libraries (the gcalcli pipx Python has them)."""
    creds = load_credentials(token_path)
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise CalendarError("the Google libraries are missing. Run this with the gcalcli Python: "
                            "~/.local/share/pipx/venvs/gcalcli/bin/python")
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def http_status(exc):
    """The HTTP status of a Google API error, or 0 if the error has none."""
    try:
        return int(getattr(getattr(exc, "resp", None), "status", 0))
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------- read scenarios

def list_events(service, calendar, day_from, day_to, tz=DEFAULT_TZ):
    """Events from day_from up to, not including, day_to. Cancelled events are left out."""
    zone = ZoneInfo(tz)
    t0 = datetime.datetime.combine(day_from, datetime.time(0, 0), tzinfo=zone)
    t1 = datetime.datetime.combine(day_to, datetime.time(0, 0), tzinfo=zone)
    if t1 <= t0:
        raise CalendarError("the end date must be after the start date (the end date is not included)")
    items, page = [], None
    while True:
        params = {"calendarId": calendar, "timeMin": iso(t0), "timeMax": iso(t1),
                  "singleEvents": True, "orderBy": "startTime", "maxResults": 250}
        if page:
            params["pageToken"] = page
        result = service.events().list(**params).execute()
        items.extend(result.get("items", []))
        page = result.get("nextPageToken")
        if not page:
            break
    return [e for e in items if e.get("status") != "cancelled"]


def find_events(service, calendar, title, tz=DEFAULT_TZ):
    """Events whose title is exactly this mandated title (the idempotency check of P-28)."""
    d = validate_title(title)
    one = datetime.timedelta(days=1)
    return [e for e in list_events(service, calendar, d - one, d + 2 * one, tz) if e.get("summary") == title]


def get_event(service, calendar, event_id):
    try:
        event = service.events().get(calendarId=calendar, eventId=event_id).execute()
    except Exception as exc:
        if http_status(exc) in (404, 410):
            raise CalendarError("no event with that ID")
        raise
    if event.get("status") == "cancelled":
        raise CalendarError("no event with that ID (it is cancelled)")
    return event


def require_lifeos_single_event(event):
    """Move and delete only touch mandated, single, timed events. Personal events are refused."""
    if title_date(event.get("summary")) is None:
        raise CalendarError("that event is not a LifeOS event (its title does not follow the mandate); "
                            "these scripts never change other events")
    if event.get("recurrence") or event.get("recurringEventId"):
        raise CalendarError("that event is part of a recurring series; these scripts only change single events")
    if "dateTime" not in event.get("start", {}):
        raise CalendarError("that event is an all-day event; these scripts only change timed events")


# ---------------------------------------------------------------- write scenarios

def create_event(service, calendar, title, start_text, minutes=30, tz=DEFAULT_TZ, dry_run=False):
    """Create one event. Refuses a title that already exists (no duplicates, P-28)."""
    d = validate_title(title)
    start = parse_local(start_text, tz)
    check_minutes(minutes)
    if start.date() != d:
        raise CalendarError("the date in the title is " + d.isoformat() + " but the start is on " +
                            start.date().isoformat() + " (APR-0035: the title carries the event date)")
    existing = find_events(service, calendar, title, tz)
    if existing:
        raise CalendarError("an event with this exact title already exists (ID " + existing[0].get("id", "?") +
                            "); not creating a duplicate")
    body = event_body(title, start, minutes, tz)
    if dry_run:
        return {"action": "dry-run create", "id": "", "body": body}
    created = service.events().insert(calendarId=calendar, body=body).execute()
    return {"action": "created", "id": created["id"], "body": body}


def move_event(service, calendar, event_id, start_text, minutes=None, new_title=None, tz=DEFAULT_TZ, dry_run=False):
    """Move one LifeOS event to a new start. The duration is kept unless minutes is given.

    The title carries the event date (APR-0035). Moving to another day needs new_title with the new date.
    """
    event = get_event(service, calendar, event_id)
    require_lifeos_single_event(event)
    old_title = event["summary"]
    old_start = parse_google_time(event["start"]["dateTime"])
    old_end = parse_google_time(event["end"]["dateTime"])
    new_start = parse_local(start_text, tz)
    if minutes is None:
        duration = old_end - old_start
    else:
        duration = datetime.timedelta(minutes=check_minutes(minutes))
    title = old_title
    if new_title is not None:
        validate_title(new_title)
        title = new_title
    if new_start.date() != title_date(title):
        raise CalendarError("the title date is " + title_date(title).isoformat() + " but the new start is on " +
                            new_start.date().isoformat() + ". Give --new-title with the new date (APR-0035).")
    if title != old_title:
        clash = [e for e in find_events(service, calendar, title, tz) if e.get("id") != event_id]
        if clash:
            raise CalendarError("an event with the new title already exists (ID " + clash[0].get("id", "?") + ")")
    new_end = new_start + duration
    if title == old_title and new_start == old_start and new_end == old_end:
        raise CalendarError("nothing to change: the event is already at that time")
    body = {"start": {"dateTime": iso(new_start), "timeZone": tz},
            "end": {"dateTime": iso(new_end), "timeZone": tz}}
    if title != old_title:
        body["summary"] = title
    if dry_run:
        return {"action": "dry-run move", "id": event_id, "body": body, "title": title}
    moved = service.events().patch(calendarId=calendar, eventId=event_id, body=body).execute()
    return {"action": "moved", "id": moved.get("id", event_id), "body": body, "title": title}


def _is_gone(service, calendar, event_id):
    try:
        event = service.events().get(calendarId=calendar, eventId=event_id).execute()
    except Exception as exc:
        if http_status(exc) in (404, 410):
            return True
        raise
    return event.get("status") == "cancelled"


def delete_event(service, calendar, event_id, expect_title, approved=False, approval_note="", dry_run=False):
    """Delete one LifeOS event by ID. Needs the CEO's approval first (APR-0044).

    The title must match the event with that ID, so a wrong ID deletes nothing.
    """
    if not dry_run and not (approved and approval_note.strip()):
        raise CalendarError("a delete needs the CEO's approval first (APR-0044). Pass --ceo-approved and "
                            "--approval-note saying where the CEO said yes.")
    event = get_event(service, calendar, event_id)
    require_lifeos_single_event(event)
    if event.get("summary") != expect_title:
        raise CalendarError("the title does not match the event with that ID; nothing was deleted")
    if dry_run:
        return {"action": "dry-run delete", "id": event_id, "title": expect_title, "approval": approval_note}
    service.events().delete(calendarId=calendar, eventId=event_id).execute()
    if not _is_gone(service, calendar, event_id):
        raise CalendarError("the delete was sent but the event is still there: " + event_id)
    return {"action": "deleted", "id": event_id, "title": expect_title, "approval": approval_note}


# ---------------------------------------------------------------- command line helpers

def add_common_args(parser, write=False):
    parser.add_argument("--calendar", default=os.environ.get("GCAL_CALENDAR"),
                        help="calendar email; or set GCAL_CALENDAR (never commit it)")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="gcalcli login file (default " + DEFAULT_TOKEN + ")")
    parser.add_argument("--tz", default=DEFAULT_TZ, help="time zone (default " + DEFAULT_TZ + ")")
    if write:
        parser.add_argument("--dry-run", action="store_true", help="check everything, change nothing")


def run(args, service, action):
    """Build the service if needed, run action(service) and turn refusals into an exit code."""
    import sys
    try:
        if not args.calendar:
            raise CalendarError("--calendar is required (or set GCAL_CALENDAR)")
        ZoneInfo(args.tz)
        if service is None:
            service = build_service(args.token)
        return action(service)
    except CalendarError as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        status = http_status(exc)
        print("error: Google API call failed" + (" (HTTP " + str(status) + ")" if status else "") +
              ": " + type(exc).__name__ + ": " + str(exc)[:300], file=sys.stderr)
        return 1
