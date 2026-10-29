#!/usr/bin/env python3
"""ceo-ledger.py - the runner's CEO approval ledger for the regression scenarios (APR-0101, handover 12).
  ceo-ledger.py append RUN EVENT TEXT     append one line to ~/loop1/ceo-ledger/scenario-ledger.jsonl (or $CEO_LEDGER)
Line: {"time":"<UTC ISO>","run":"<run>","event":"<event>","channel":"cli","sender":"CEO","text_sha256":"<sha256 of TEXT>"}
Only runner scripts call this, right after they send the CEO's own message that asks for or approves a delete. The directory is
mode 700, the file mode 600, opened append-only; a line is never edited. The ledger holds no IDs other than run and event IDs."""
import datetime, hashlib, json, os, sys

DEFAULT = os.path.expanduser("~/loop1/ceo-ledger/scenario-ledger.jsonl")


def make_line(run, event, text, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return json.dumps({"time": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "run": run, "event": event, "channel": "cli", "sender": "CEO",
                       "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}, separators=(",", ":"))


def append(path, run, event, text, now=None):
    if not run or not event:
        raise ValueError("run and event are required")
    d = os.path.dirname(path)
    os.makedirs(d, mode=0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, (make_line(run, event, text, now) + "\n").encode("utf-8"))
    finally:
        os.close(fd)


if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] != "append":
        sys.exit(__doc__)
    append(os.environ.get("CEO_LEDGER", DEFAULT), sys.argv[2], sys.argv[3], sys.argv[4])
    print("ledger line appended for %s %s" % (sys.argv[2], sys.argv[3]))
