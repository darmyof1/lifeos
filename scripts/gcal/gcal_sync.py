#!/usr/bin/env python3
"""Push job for the CoS calendar journal (P-28, APR-0077). Code, not the model (ADR-0008, ADR-0011).

Reads the journal (the CoS keeps it at state/calendar-journal.md), pushes entries to Google Calendar and
appends the result as NEW lines. It never edits or removes a line (APR-0054, APR-0057, APR-0058).

Journal line:  name | start | end | status | run ID | event ID | requested by [| detail]
Lines the job writes use "sync" as requested by, and a detail:  google=<id>   attempt=2; error=...   reason=...

What it does, per entry (the latest line of each name decides):
  written           push it: create the event, or move the old event when a "moved" line with the same run ID and
                    event ID came first (APR-0057), then append  pushed  with the Google event ID
  failed            retry on the next run until 5 attempts; the 5th failure is final and the alert goes to the COO channel
  deleted           only with --allow-deletes, only after a  delete-pending-approval  line for the same event ID (APR-0044);
                    with --require-ceo-ledger PATH (once per ledger file) also only if a ledger holds a CEO entry for it (APR-0100, APR-0102)
  requested, pushed, conflict, moved, delete-pending-approval   nothing to do
Before it creates anything it searches Google for the exact title (APR-0034). A write that worked but looked failed is
therefore not repeated. If the title exists at another time, or twice, the job appends  conflict  and touches nothing.

If Google says the login was revoked (invalid_grant, HTTP 401) all writes pause: a pause file is written, one alert is
sent, and later runs do nothing until the CEO has logged in again and removed the file (S-07, APR-0043).

Only title, start and end go to Google (APR-0032). Personal events are never touched: the scripts in gcal_common only
move or delete mandated, single, timed events.

Usage (run with the gcalcli Python, which has the Google libraries; see guides/calendar-sync-job.md):
  gcal_sync.py --calendar <calendar-id> [--dry-run] [--allow-deletes] [--journal PATH] [--state-dir DIR]
  gcal_sync.py --test-alert          send one test message to the alert channel and stop
Alert target (never committed): LIFEOS_ALERT_TARGET (for example channel:C0123456789) and LIFEOS_ALERT_ACCOUNT (default: default).
Exit codes: 0 done, 2 usage, 3 paused (login revoked), 4 could not start (login file, libraries, journal).
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

try:
    import fcntl
except ImportError:  # not on Linux or macOS; the lock is skipped
    fcntl = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcal_busy as gb  # noqa: E402
import gcal_common as gc  # noqa: E402

MAX_ATTEMPTS = 5
MAX_PER_RUN = 20
STATUSES = ("requested", "written", "pushed", "failed", "conflict", "moved", "delete-pending-approval", "deleted")
SYNC_BY = "sync"
DEFAULT_JOURNAL = "~/loop1/workspaces/cos/state/calendar-journal.md"
DEFAULT_STATE_DIR = "~/loop1/gcal-sync"
PAUSE_FILE = "PAUSED-login-revoked"


class Entry:
    __slots__ = ("lineno", "name", "start", "end", "status", "run", "event", "by", "detail")

    def __init__(self, lineno, name, start, end, status, run, event, by, detail=""):
        self.lineno, self.name, self.start, self.end, self.status = lineno, name, start, end, status
        self.run, self.event, self.by, self.detail = run, event, by, detail


# ---------------------------------------------------------------- the journal

def parse_journal(text):
    """Entries in file order. Header lines, notes and lines with an unknown status are skipped."""
    entries = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7 or gc.TITLE_RE.match(parts[0]) is None or parts[3] not in STATUSES:
            continue
        detail = " | ".join(parts[7:]) if len(parts) > 7 else ""
        entries.append(Entry(n, parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], detail))
    return entries


def clean(text, limit=120):
    """One short line that cannot break the table."""
    text = " ".join(str(text).replace("|", "/").split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def format_line(e, status, detail):
    return " | ".join([e.name, e.start, e.end, status, e.run, e.event, SYNC_BY, clean(detail, 200)])


def append_line(journal, line):
    """Append one line to the journal. The file may lack a final newline."""
    path = os.path.expanduser(journal)
    prefix = ""
    try:
        with open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            if fh.tell() > 0:
                fh.seek(-1, os.SEEK_END)
                if fh.read(1) != b"\n":
                    prefix = "\n"
    except FileNotFoundError:
        pass
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, (prefix + line + "\n").encode("utf-8"))
    finally:
        os.close(fd)


def latest_by_name(entries):
    """The latest entry of each name, in the order of their last line, and the failed-attempt count of each."""
    latest, attempts = {}, {}
    for e in entries:
        latest[e.name] = e
        attempts[e.name] = attempts.get(e.name, 0) + 1 if e.status == "failed" else 0
    return sorted(latest.values(), key=lambda e: e.lineno), attempts


def moved_hint(entries, e):
    """The moved line written just before this entry with the same run ID and event ID (APR-0057)."""
    hint = None
    if e.run and e.event:
        for x in entries:
            if x.lineno >= e.lineno:
                break
            if x.status == "moved" and x.run == e.run and x.event == e.event:
                hint = x
    return hint


def delete_was_requested(entries, e):
    return any(x.lineno < e.lineno and x.status == "delete-pending-approval" and x.event == e.event for x in entries)


LEDGER_GRACE_SECONDS = 300      # an approval may arrive this long before the job first saw the pending line (cron interval)
LEDGER_MAX_AGE_SECONDS = 48 * 3600


def _utc(text):
    t = datetime.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)


def _state_json(state_dir, name):
    try:
        with open(os.path.join(state_dir, name), encoding="utf-8") as fh:
            d = json.load(fh)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def _save_state_json(state_dir, name, data):
    os.makedirs(state_dir, exist_ok=True)
    tmp = os.path.join(state_dir, name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, sort_keys=True)
    os.replace(tmp, os.path.join(state_dir, name))


def pending_key(e):
    return e.run + "|" + e.event


def note_pending_seen(state_dir, entries, now=None):
    """APR-0102: the journal has no time column, so the job remembers when it first saw each delete-pending-approval line
    (state file ceo-ledger-seen.json). A Slack approval older than that moment (less the grace) does not count."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    seen = _state_json(state_dir, "ceo-ledger-seen.json")
    new = {pending_key(x): now.strftime("%Y-%m-%dT%H:%M:%SZ") for x in entries
           if x.status == "delete-pending-approval" and pending_key(x) not in seen}
    if new:
        seen.update(new)
        _save_state_json(state_dir, "ceo-ledger-seen.json", seen)


def find_ceo_approval(ledger, e, now=None, state_dir=None):
    """APR-0100/0102: the ledger entry (a dict) that approves this deleted line, or None. The ledger lives outside every agent
    workspace; one JSON object per line. Two kinds of entry, both need sender "CEO" and a time not later than now:
      scenario entry (runner, APR-0101):  run and event equal the deleted line's run and event.
      Slack entry (plugin, APR-0102):     the event ID is one of event_tokens; the entry is not older than LEDGER_MAX_AGE_SECONDS;
                                          it is not older than the first time the job saw the pending line (less
                                          LEDGER_GRACE_SECONDS); its message_id was not used for an earlier delete.
    A missing or unreadable ledger, a damaged line, or a Slack entry with no state_dir approves nothing."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    try:
        with open(os.path.expanduser(ledger), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return None
    seen = _state_json(state_dir, "ceo-ledger-seen.json") if state_dir else {}
    used = set(_state_json(state_dir, "ceo-ledger-used.json")) if state_dir else set()
    first_seen = None
    if seen.get(pending_key(e)):
        try:
            first_seen = _utc(seen[pending_key(e)])
        except ValueError:
            first_seen = None
    for line in lines:
        try:
            r = json.loads(line)
            t = _utc(r["time"])
        except (ValueError, KeyError, TypeError):
            continue
        if not isinstance(r, dict) or r.get("sender") != "CEO" or t > now:
            continue
        if "event_tokens" not in r:
            if r.get("run") == e.run and r.get("event") == e.event:
                return r
            continue
        tokens = r.get("event_tokens")
        mid = str(r.get("message_id") or "")
        if (isinstance(tokens, list) and e.event.lower() in [str(x).lower() for x in tokens] and mid and mid not in used
                and first_seen is not None and state_dir
                and t >= first_seen - datetime.timedelta(seconds=LEDGER_GRACE_SECONDS)
                and (now - t).total_seconds() <= LEDGER_MAX_AGE_SECONDS):
            return r
    return None


def ceo_approval_recorded(ledger, e, now=None, state_dir=None):
    return find_ceo_approval(ledger, e, now, state_dir) is not None


def approved_by_any(ledgers, e, now=None, state_dir=None):
    for ledger in ([ledgers] if isinstance(ledgers, str) else ledgers or []):
        r = find_ceo_approval(ledger, e, now, state_dir)
        if r is not None:
            return r
    return None


def mark_ledger_used(state_dir, record):
    """A Slack approval covers one delete once: remember its message_id after the delete ran."""
    mid = str((record or {}).get("message_id") or "")
    if mid:
        used = _state_json(state_dir, "ceo-ledger-used.json")
        used[mid] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _save_state_json(state_dir, "ceo-ledger-used.json", used)


def detail_value(detail, field):
    """Value of  field=value  in a detail column such as  google=abc; privacy=high ."""
    for part in (detail or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == field:
            return v.strip()
    return ""


def is_high_privacy(entries, name):
    """A high-privacy entry shows in Google as busy (APR-0032). The CoS marks it with privacy=high in the detail column."""
    return any(x.name == name and detail_value(x.detail, "privacy") == "high" for x in entries)


def high_for_entry(entries, e):
    """High privacy for this entry: marked on its name, or inherited through a move from a high-privacy old name,
    so a forgotten marker on the new line can never put a mandated title into Google."""
    if is_high_privacy(entries, e.name):
        return True
    hint = moved_hint(entries, e)
    return hint is not None and is_high_privacy(entries, hint.name)


def last_pushed(entries, name, before=None):
    """The latest pushed line of this name that has a Google event ID."""
    found = None
    for x in entries:
        if before is not None and x.lineno >= before:
            break
        if x.name == name and x.status == "pushed" and detail_value(x.detail, "google"):
            found = x
    return found


# ---------------------------------------------------------------- the push of one entry

class Conflict(Exception):
    pass


class TokenRevoked(Exception):
    pass


def is_token_revoked(exc):
    text = str(exc).lower()
    return "invalid_grant" in text or gc.http_status(exc) == 401


def entry_times(e, tz):
    """Start, end and length in minutes of an entry, or raise Conflict when the entry cannot be pushed as written."""
    try:
        gc.validate_title(e.name)
        start = gc.parse_local(e.start.replace(" ", "T"), tz)
        end = gc.parse_local(e.end.replace(" ", "T"), tz)
    except gc.CalendarError as exc:
        raise Conflict(str(exc)[:160])
    minutes = int((end - start).total_seconds() // 60)
    if minutes < 1 or minutes > 1440:
        raise Conflict("the end must be after the start, within one day")
    if start.date() != gc.title_date(e.name):
        raise Conflict("the date in the title is not the date of the start (APR-0035)")
    return start, end, minutes


def same_times(event, start, end):
    try:
        return (gc.parse_google_time(event["start"]["dateTime"]) == start and
                gc.parse_google_time(event["end"]["dateTime"]) == end)
    except (KeyError, ValueError):
        return False


def push_busy_entry(service, calendar, e, hint, entries, tz, dry_run):
    """A high-privacy entry: Google gets the title busy and a hidden key, never the mandated title (APR-0079)."""
    start, end, minutes = entry_times(e, tz)
    start_text = start.replace(tzinfo=None).isoformat(timespec="minutes")
    key = e.event
    if not key:
        raise Conflict("a high-privacy entry needs an event ID")
    found = gb.find_busy(service, calendar, key, start.date(), tz)
    if len(found) > 1:
        raise Conflict("more than one busy event in Google has this key")
    if len(found) == 1:
        if same_times(found[0], start, end):
            return "already in Google (busy)", found[0]["id"]
        raise Conflict("a busy event with this key exists in Google at another time")
    # The earlier Google event of this entry: through a move the old name, otherwise the same name marked high later.
    old = last_pushed(entries, hint.name if hint is not None else e.name, e.lineno)
    if old is not None:
        old_id = detail_value(old.detail, "google")
        try:
            event = gc.get_event(service, calendar, old_id)
        except gc.CalendarError:
            event = None
        if event is not None:
            if gb.is_busy_event(event):
                r = gb.move_busy(service, calendar, old_id, key, start_text, minutes, tz, dry_run)
                return "moved (busy)", r["id"]
            # Raising privacy: the normal event becomes a busy event (APR-0086). A personal event is refused (conflict).
            r = gb.make_busy(service, calendar, old_id, key, start_text, minutes, tz, dry_run)
            return "made busy", r["id"]
    r = gb.create_busy(service, calendar, key, start.date(), start_text, minutes, tz, dry_run)
    return "created (busy)", r["id"]


def push_entry(service, calendar, e, hint, tz, dry_run, entries=()):
    """Make Google match this entry. Returns (action, google_id). Raises Conflict or any Google error."""
    if high_for_entry(entries, e):
        return push_busy_entry(service, calendar, e, hint, entries, tz, dry_run)
    start, end, minutes = entry_times(e, tz)
    start_text = start.replace(tzinfo=None).isoformat(timespec="minutes")
    found = gc.find_events(service, calendar, e.name, tz)
    if len(found) > 1:
        raise Conflict("more than one event in Google has this exact title")
    if len(found) == 1:
        event = found[0]
        if same_times(event, start, end):
            return "already in Google", event["id"]
        if hint is not None and hint.name == e.name:
            r = gc.move_event(service, calendar, event["id"], start_text, minutes=minutes, tz=tz, dry_run=dry_run)
            return "moved in place", r["id"]
        raise Conflict("an event with this title exists in Google at another time")
    if hint is not None and hint.name != e.name:
        old = gc.find_events(service, calendar, hint.name, tz)
        if len(old) > 1:
            raise Conflict("more than one event in Google has the old title")
        if len(old) == 1:
            r = gc.move_event(service, calendar, old[0]["id"], start_text, minutes=minutes, new_title=e.name,
                              tz=tz, dry_run=dry_run)
            return "moved", r["id"]
    r = gc.create_event(service, calendar, e.name, start_text, minutes, tz, dry_run)
    return "created", r["id"]


def delete_entry(service, calendar, e, tz, dry_run, entries=()):
    note = "journal: deleted after delete-pending-approval, run " + e.run
    if is_high_privacy(entries, e.name):
        pushed = last_pushed(entries, e.name, e.lineno)
        if pushed is None:
            raise Conflict("no pushed line with a Google event ID for this high-privacy entry")
        try:
            r = gb.delete_busy(service, calendar, detail_value(pushed.detail, "google"), pushed.event,
                               approved=True, approval_note=note, dry_run=dry_run)
        except gc.CalendarError as exc:
            if str(exc) == "no event with that ID":
                return "already gone", ""
            raise
        return "deleted (busy)", r["id"]
    found = gc.find_events(service, calendar, e.name, tz)
    if len(found) > 1:
        raise Conflict("more than one event in Google has this exact title")
    if not found:
        return "already gone", ""
    r = gc.delete_event(service, calendar, found[0]["id"], e.name, approved=True, approval_note=note, dry_run=dry_run)
    return "deleted", r["id"]


# ---------------------------------------------------------------- alerts and pause

def now_text():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_alerter(state_dir, target, account, runner=subprocess.run):
    """alert(text) writes alerts.log and, when a target is set, posts to Slack with openclaw message send."""
    state = os.path.expanduser(state_dir)

    def alert(text):
        os.makedirs(state, exist_ok=True)
        text = clean(text, 400)
        result = "logged only (LIFEOS_ALERT_TARGET not set)"
        if target:
            cmd = ["openclaw", "message", "send", "--channel", "slack", "--account", account or "default",
                   "--target", target, "--message", text]
            try:
                r = runner(cmd, capture_output=True, text=True, timeout=60)
                result = "sent" if r.returncode == 0 else "send failed (exit %s): %s" % (r.returncode, clean(r.stderr or r.stdout, 160))
            except Exception as exc:
                result = "send failed (%s)" % type(exc).__name__
        with open(os.path.join(state, "alerts.log"), "a", encoding="utf-8") as fh:
            fh.write("%s | %s | %s\n" % (now_text(), result, text))
        return result

    return alert


def pause_path(state_dir):
    return os.path.join(os.path.expanduser(state_dir), PAUSE_FILE)


def write_pause(state_dir, reason):
    os.makedirs(os.path.expanduser(state_dir), exist_ok=True)
    with open(pause_path(state_dir), "w", encoding="utf-8") as fh:
        fh.write("%s | %s\n" % (now_text(), clean(reason, 200)))


class RunLock:
    """One run at a time. A second run exits quietly."""

    def __init__(self, state_dir):
        self.path = os.path.join(os.path.expanduser(state_dir), "run.lock")
        self.fh = None

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.fh = open(self.path, "a")
        if fcntl is not None:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self.fh.close()
                self.fh = None
        return self.fh is not None

    def __exit__(self, *exc):
        if self.fh is not None:
            self.fh.close()


# ---------------------------------------------------------------- one run

def pause_run(state_dir, alert, name, dry_run, out, exc, counts):
    out("error: the Google login was revoked or expired: %s" % clean(exc, 160))
    if not dry_run:
        write_pause(state_dir, "revoked while pushing " + name)
        alert("LifeOS calendar sync PAUSED: the Google login was revoked or expired. "
              "No calendar writes until the CEO logs in again (S-07). See guides/calendar-sync-job.md.")
    return 3, counts


def sync(service, calendar, journal, state_dir, alert, tz=gc.DEFAULT_TZ, dry_run=False, allow_deletes=False,
         max_per_run=MAX_PER_RUN, out=print, ceo_ledger=None, now=None):
    """Process the journal once. Returns (exit code, counts)."""
    counts = {"pushed": 0, "conflict": 0, "failed": 0, "final": 0, "deleted": 0, "skipped": 0}
    if os.path.exists(pause_path(state_dir)):
        out("paused: the Google login was revoked (%s). Log in again, then remove it." % pause_path(state_dir))
        return 3, counts
    path = os.path.expanduser(journal)
    try:
        with open(path, encoding="utf-8") as fh:
            entries = parse_journal(fh.read())
    except OSError as exc:
        out("error: cannot read the journal: %s" % exc)
        return 4, counts
    if ceo_ledger and not dry_run:
        note_pending_seen(state_dir, entries, now)
    todo, attempts = latest_by_name(entries)
    done = 0
    approvals = {}
    for e in todo:
        if e.status == "failed" and attempts[e.name] >= MAX_ATTEMPTS:
            continue
        if e.status not in ("written", "failed", "deleted"):
            continue
        if e.status == "deleted":
            if not allow_deletes:
                out("skip   %s: deleted in the journal, but --allow-deletes is not set (APR-0044)" % e.name)
                counts["skipped"] += 1
                continue
            if not delete_was_requested(entries, e):
                out("skip   %s: no delete-pending-approval line for event %s (APR-0044)" % (e.name, e.event))
                counts["skipped"] += 1
                continue
            if ceo_ledger:
                approvals[e.lineno] = approved_by_any(ceo_ledger, e, now, state_dir)
                if approvals[e.lineno] is None:
                    out("skip   %s: no CEO approval record for event %s (APR-0100)" % (e.name, e.event))
                    counts["skipped"] += 1
                    continue
        if done >= max_per_run:
            out("stop   %d entries done this run; the rest waits for the next run" % done)
            break
        done += 1
        try:
            if e.status == "deleted":
                action, gid = delete_entry(service, calendar, e, tz, dry_run, entries)
                detail = ("google=%s; deleted" % gid) if gid else "already gone"
                counts["deleted"] += 1
                if not dry_run and approvals.get(e.lineno):
                    mark_ledger_used(state_dir, approvals[e.lineno])
            else:
                action, gid = push_entry(service, calendar, e, moved_hint(entries, e), tz, dry_run, entries)
                detail = "google=" + gid + ("; privacy=high" if high_for_entry(entries, e) else "")
                counts["pushed"] += 1
            out("%s %s: %s %s" % ("would" if dry_run else "done ", e.name, action, gid))
            if not dry_run:
                append_line(journal, format_line(e, "pushed", detail))
        except (Conflict, gc.CalendarError) as exc:
            if is_token_revoked(exc):
                return pause_run(state_dir, alert, e.name, dry_run, out, exc, counts)
            counts["conflict"] += 1
            out("conflict %s: %s" % (e.name, exc))
            if not dry_run:
                append_line(journal, format_line(e, "conflict", "reason=" + str(exc)))
        except Exception as exc:
            if is_token_revoked(exc):
                return pause_run(state_dir, alert, e.name, dry_run, out, exc, counts)
            n = attempts.get(e.name, 0) + 1
            counts["failed"] += 1
            err = "%s: %s" % (type(exc).__name__, exc)
            out("failed %s: attempt %d of %d: %s" % (e.name, n, MAX_ATTEMPTS, clean(err, 160)))
            if not dry_run:
                detail = "attempt=%d; error=%s" % (n, clean(err, 100))
                if n >= MAX_ATTEMPTS:
                    detail += "; final"
                    counts["final"] += 1
                append_line(journal, format_line(e, "failed", detail))
                if n >= MAX_ATTEMPTS:
                    alert("LifeOS calendar sync: %s failed %d times and will not be retried (run %s, event %s). "
                          "CEO: please check." % (e.name, n, e.run, e.event))
    return 0, counts


# ---------------------------------------------------------------- command line

def main(argv=None, service=None, alert_runner=None):
    p = argparse.ArgumentParser(description="Push the CoS calendar journal to Google Calendar (P-28).")
    gc.add_common_args(p, write=True)
    p.add_argument("--journal", default=DEFAULT_JOURNAL, help="the CoS journal (default %s)" % DEFAULT_JOURNAL)
    p.add_argument("--state-dir", default=DEFAULT_STATE_DIR, help="lock, pause file and logs (default %s)" % DEFAULT_STATE_DIR)
    p.add_argument("--allow-deletes", action="store_true", help="also run approved deletes (APR-0044)")
    p.add_argument("--require-ceo-ledger", metavar="PATH", action="append", default=None,
                   help="run a delete only if a ledger (JSON lines, outside the agent workspaces) holds a CEO entry for it (APR-0100, APR-0102); "
                        "give the option once per ledger file (scenario ledger, Slack ledger)")
    p.add_argument("--max-per-run", type=int, default=MAX_PER_RUN)
    p.add_argument("--test-alert", action="store_true", help="send one test message to the alert channel and stop")
    args = p.parse_args(argv)

    alert = make_alerter(args.state_dir, os.environ.get("LIFEOS_ALERT_TARGET", ""),
                         os.environ.get("LIFEOS_ALERT_ACCOUNT", "default"), alert_runner or subprocess.run)
    if args.test_alert:
        print("alert: " + alert("LifeOS calendar sync: test alert. If you can read this, alerts reach this channel."))
        return 0
    if not args.calendar:
        print("error: --calendar is required (or set GCAL_CALENDAR)", file=sys.stderr)
        return 2
    if os.path.exists(pause_path(args.state_dir)):
        print("paused: the Google login was revoked (%s). Log in again, then remove it." % pause_path(args.state_dir))
        return 3
    with RunLock(args.state_dir) as got:
        if not got:
            print("another run is active; nothing to do")
            return 0
        try:
            if service is None:
                service = gc.build_service(args.token)
        except gc.CalendarError as exc:
            if is_token_revoked(exc):
                print("error: " + str(exc), file=sys.stderr)
                if not args.dry_run:
                    write_pause(args.state_dir, "revoked at login")
                    alert("LifeOS calendar sync PAUSED: the Google login was revoked or expired. "
                          "No calendar writes until the CEO logs in again (S-07). See guides/calendar-sync-job.md.")
                return 3
            print("error: " + str(exc), file=sys.stderr)
            return 4
        code, counts = sync(service, args.calendar, args.journal, args.state_dir, alert, args.tz, args.dry_run,
                            args.allow_deletes, args.max_per_run, ceo_ledger=args.require_ceo_ledger)
    print("%s: pushed %d, conflict %d, failed %d (final %d), deleted %d, skipped %d" % (
        "dry run" if args.dry_run else "summary", counts["pushed"], counts["conflict"], counts["failed"],
        counts["final"], counts["deleted"], counts["skipped"]))
    return code


if __name__ == "__main__":
    sys.exit(main())
