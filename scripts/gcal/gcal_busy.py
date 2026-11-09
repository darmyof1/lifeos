"""High-privacy events in Google Calendar: they show as "busy" (APR-0032, APR-0079).

The event has the title "busy", a start, an end and one hidden field with the journal's event ID. The mandated title
(for example "CHO - Workout - 10262026-0001") never goes to Google for these events. They are found again by the hidden
field, never by title. Used by gcal_sync.py; no command line of its own.
"""
import datetime

import gcal_common as gc

BUSY_TITLE = "busy"
KEY_FIELD = "lifeos_event"


def key_of(event):
    return ((event.get("extendedProperties") or {}).get("private") or {}).get(KEY_FIELD)


def is_busy_event(event):
    return event.get("summary") == BUSY_TITLE and bool(key_of(event))


def busy_body(key, start, minutes, tz=gc.DEFAULT_TZ):
    body = gc.event_body(BUSY_TITLE, start, minutes, tz)
    body["transparency"] = "opaque"  # shows as busy
    body["extendedProperties"] = {"private": {KEY_FIELD: key}}
    return body


def find_busy(service, calendar, key, day, tz=gc.DEFAULT_TZ):
    """Busy events with this hidden key, searched on the day before, the day and the day after."""
    one = datetime.timedelta(days=1)
    return [e for e in gc.list_events(service, calendar, day - one, day + 2 * one, tz)
            if is_busy_event(e) and key_of(e) == key]


def is_keyed_event(event):
    """A LifeOS high-privacy event in either display mode: it has the hidden key and shows as busy or with its mandated title."""
    return bool(key_of(event)) and (event.get("summary") == BUSY_TITLE or gc.title_date(event.get("summary")) is not None)


def require_busy_event(event):
    """An event this job made for a privacy=high entry (hidden key present), shown as busy or, in full mode, with its title."""
    if not is_keyed_event(event):
        raise gc.CalendarError("that event is not a LifeOS busy event; nothing was changed")
    if event.get("recurrence") or event.get("recurringEventId"):
        raise gc.CalendarError("that event is part of a recurring series; only single events are changed")
    if "dateTime" not in event.get("start", {}):
        raise gc.CalendarError("that event is an all-day event; only timed events are changed")


def create_busy(service, calendar, key, day, start_text, minutes, tz=gc.DEFAULT_TZ, dry_run=False):
    start = gc.parse_local(start_text, tz)
    gc.check_minutes(minutes)
    if start.date() != day:
        raise gc.CalendarError("the start is not on the date of the entry")
    existing = find_busy(service, calendar, key, day, tz)
    if existing:
        raise gc.CalendarError("a busy event with this key already exists (ID %s); not creating a duplicate" % existing[0].get("id", "?"))
    body = busy_body(key, start, minutes, tz)
    if dry_run:
        return {"action": "dry-run create", "id": "", "body": body}
    created = service.events().insert(calendarId=calendar, body=body).execute()
    return {"action": "created", "id": created["id"], "body": body}


def make_busy(service, calendar, event_id, key, start_text, minutes, tz=gc.DEFAULT_TZ, dry_run=False):
    """Raise the privacy of a normal LifeOS event to busy (APR-0086).

    The title becomes busy, the description and the place are cleared, the time shows as busy and the hidden key is set.
    Only a mandated, single, timed event is changed. The other direction (busy to normal) is not supported (APR-0086).
    """
    event = gc.get_event(service, calendar, event_id)
    if is_busy_event(event):
        raise gc.CalendarError("that event is already a busy event")
    gc.require_lifeos_single_event(event)
    start = gc.parse_local(start_text, tz)
    body = busy_body(key, start, gc.check_minutes(minutes), tz)
    body["description"] = ""
    body["location"] = ""
    if dry_run:
        return {"action": "dry-run make busy", "id": event_id, "body": body}
    done = service.events().patch(calendarId=calendar, eventId=event_id, body=body).execute()
    return {"action": "made busy", "id": done.get("id", event_id), "body": body}


def move_busy(service, calendar, event_id, new_key, start_text, minutes, tz=gc.DEFAULT_TZ, dry_run=False):
    event = gc.get_event(service, calendar, event_id)
    require_busy_event(event)
    start = gc.parse_local(start_text, tz)
    end = start + datetime.timedelta(minutes=gc.check_minutes(minutes))
    body = {"start": {"dateTime": gc.iso(start), "timeZone": tz},
            "end": {"dateTime": gc.iso(end), "timeZone": tz},
            "extendedProperties": {"private": {KEY_FIELD: new_key}}}
    if dry_run:
        return {"action": "dry-run move", "id": event_id, "body": body}
    moved = service.events().patch(calendarId=calendar, eventId=event_id, body=body).execute()
    return {"action": "moved", "id": moved.get("id", event_id), "body": body}


def delete_busy(service, calendar, event_id, expect_key, approved=False, approval_note="", dry_run=False):
    """Delete one busy event by ID. Needs the CEO's approval (APR-0044). The hidden key must match."""
    if not dry_run and not (approved and approval_note.strip()):
        raise gc.CalendarError("a delete needs the CEO's approval first (APR-0044)")
    event = gc.get_event(service, calendar, event_id)
    require_busy_event(event)
    if key_of(event) != expect_key:
        raise gc.CalendarError("the hidden key does not match the event with that ID; nothing was deleted")
    if dry_run:
        return {"action": "dry-run delete", "id": event_id}
    service.events().delete(calendarId=calendar, eventId=event_id).execute()
    if not gc._is_gone(service, calendar, event_id):
        raise gc.CalendarError("the delete was sent but the event is still there: " + event_id)
    return {"action": "deleted", "id": event_id}


# ---------------------------------------------------------------- full display mode (APR-0119)
# privacy_display: full  -> a privacy=high entry goes to Google with its mandated title AND the hidden key, so the job can
# find it again and flip it back to busy. The journal keeps the real name in both modes.

def full_body(title, key, start, minutes, tz=gc.DEFAULT_TZ):
    body = gc.event_body(title, start, minutes, tz)
    body["transparency"] = "opaque"
    body["extendedProperties"] = {"private": {KEY_FIELD: key}}
    return body


def find_keyed(service, calendar, key, day, tz=gc.DEFAULT_TZ):
    """Events with this hidden key (busy or full title), on the day before, the day and the day after."""
    one = datetime.timedelta(days=1)
    return [e for e in gc.list_events(service, calendar, day - one, day + 2 * one, tz)
            if is_keyed_event(e) and key_of(e) == key]


def create_full(service, calendar, key, title, day, start_text, minutes, tz=gc.DEFAULT_TZ, dry_run=False):
    start = gc.parse_local(start_text, tz)
    gc.check_minutes(minutes)
    gc.validate_title(title)
    if start.date() != day:
        raise gc.CalendarError("the start is not on the date of the entry")
    existing = find_keyed(service, calendar, key, day, tz)
    if existing:
        raise gc.CalendarError("an event with this key already exists (ID %s); not creating a duplicate" % existing[0].get("id", "?"))
    body = full_body(title, key, start, minutes, tz)
    if dry_run:
        return {"action": "dry-run create", "id": "", "body": body}
    created = service.events().insert(calendarId=calendar, body=body).execute()
    return {"action": "created", "id": created["id"], "body": body}


def mark_full(service, calendar, event_id, key, title, start_text, minutes, tz=gc.DEFAULT_TZ, dry_run=False):
    """Full mode: a normal LifeOS event gets the hidden key (it keeps its mandated title)."""
    event = gc.get_event(service, calendar, event_id)
    if is_keyed_event(event):
        raise gc.CalendarError("that event already has a key")
    gc.require_lifeos_single_event(event)
    body = full_body(title, key, gc.parse_local(start_text, tz), gc.check_minutes(minutes), tz)
    if dry_run:
        return {"action": "dry-run mark", "id": event_id, "body": body}
    done = service.events().patch(calendarId=calendar, eventId=event_id, body=body).execute()
    return {"action": "marked", "id": done.get("id", event_id), "body": body}


def move_keyed(service, calendar, event_id, new_key, new_title, mode, start_text, minutes, tz=gc.DEFAULT_TZ, dry_run=False):
    """Move an existing keyed event (busy or full title); its title is set for the mode (busy, or the new mandated title)."""
    event = gc.get_event(service, calendar, event_id)
    require_busy_event(event)
    start = gc.parse_local(start_text, tz)
    end = start + datetime.timedelta(minutes=gc.check_minutes(minutes))
    body = {"summary": BUSY_TITLE if mode == "busy" else new_title,
            "start": {"dateTime": gc.iso(start), "timeZone": tz},
            "end": {"dateTime": gc.iso(end), "timeZone": tz},
            "extendedProperties": {"private": {KEY_FIELD: new_key}}}
    if dry_run:
        return {"action": "dry-run move", "id": event_id, "body": body}
    moved = service.events().patch(calendarId=calendar, eventId=event_id, body=body).execute()
    return {"action": "moved", "id": moved.get("id", event_id), "body": body}


def set_display(service, calendar, event_id, key, title, mode, dry_run=False):
    """Make the title of a keyed event match the mode. Busy to full: the real title (from the journal name). Full to busy: busy,
    with description and place cleared. Only an event carrying this hidden key is changed; it is never recreated.
    Returns "unchanged", "retitled (full)" or "blanked (busy)"."""
    event = gc.get_event(service, calendar, event_id)
    if not is_keyed_event(event) or key_of(event) != key:
        raise gc.CalendarError("that event does not carry this hidden key; nothing was changed")
    if event.get("recurrence") or event.get("recurringEventId") or "dateTime" not in event.get("start", {}):
        raise gc.CalendarError("that event is recurring or all-day; nothing was changed")
    if mode == "full" and event.get("summary") == BUSY_TITLE:
        body, action = {"summary": title}, "retitled (full)"
    elif mode == "busy" and event.get("summary") == title:
        body, action = {"summary": BUSY_TITLE, "description": "", "location": ""}, "blanked (busy)"
    else:
        return "unchanged"
    if not dry_run:
        service.events().patch(calendarId=calendar, eventId=event_id, body=body).execute()
    return action
