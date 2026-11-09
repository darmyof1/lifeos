#!/usr/bin/env python3
"""Summary of the privacy gate's shadow log (APR-0119). Read only.

Usage: gate-shadow-report.py [LOG_FILE]
Default LOG_FILE: ~/loop1/state/gate-shadow/gate-log.jsonl (the plugin writes under the OpenClaw state folder).

Prints counts by label; turns and would-block by agent, channel kind and trigger kind; per day; the first and last time; error lines.
It never prints a text and never prints a hash: the fields are read but only labels, reason codes, kinds, agents and times are shown.
A damaged line is counted and skipped.
"""
import collections
import json
import os
import sys

DEFAULT_LOG = "~/loop1/state/gate-shadow/gate-log.jsonl"
SAFE = {"agent", "channel_kind", "trigger_kind", "label", "reason"}


def clean(value):
    """Only a short plain word is shown. Anything else (a stray text field) becomes 'other'."""
    v = str(value) if value is not None else "absent"
    return v if len(v) <= 40 and all(ch.isalnum() or ch in "_-." for ch in v) else "other"


def summarize(lines):
    s = {"turns": 0, "errors": 0, "damaged": 0, "first": None, "last": None,
         "label": collections.Counter(), "reason": collections.Counter(),
         "agent": collections.Counter(), "channel_kind": collections.Counter(), "trigger_kind": collections.Counter(),
         "wb_agent": collections.Counter(), "wb_channel_kind": collections.Counter(), "wb_trigger_kind": collections.Counter(),
         "wb_total": 0, "day": collections.OrderedDict()}
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            r = json.loads(raw)
            t = str(r["time"])
        except (ValueError, KeyError, TypeError):
            s["damaged"] += 1
            continue
        if not isinstance(r, dict):
            s["damaged"] += 1
            continue
        s["first"] = t if s["first"] is None or t < s["first"] else s["first"]
        s["last"] = t if s["last"] is None or t > s["last"] else s["last"]
        if "error" in r:
            s["errors"] += 1
            continue
        s["turns"] += 1
        wb = r.get("would_block") is True
        s["label"][clean(r.get("label"))] += 1
        s["reason"][clean(r.get("reason"))] += 1
        for k in ("agent", "channel_kind", "trigger_kind"):
            s[k][clean(r.get(k))] += 1
            if wb:
                s["wb_" + k][clean(r.get(k))] += 1
        day = t[:10]
        d = s["day"].setdefault(day, [0, 0])
        d[0] += 1
        if wb:
            d[1] += 1
            s["wb_total"] += 1
    return s


def fmt(counter, wb=None):
    if not counter:
        return "  (none)"
    out = []
    for k, n in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append("  %-18s %5d" % (k, n) + (("   would block %d" % wb.get(k, 0)) if wb is not None else ""))
    return "\n".join(out)


def report(s):
    lines = ["PRIVACY GATE SHADOW REPORT (nothing was blocked; this is what enforce mode would have done)"]
    lines.append("turns logged: %d   would block: %d   error lines: %d   damaged lines: %d" % (s["turns"], s["wb_total"], s["errors"], s["damaged"]))
    lines.append("first: %s   last: %s" % (s["first"] or "-", s["last"] or "-"))
    lines += ["", "by label (what the prefilter said):", fmt(s["label"]),
              "", "by reason code:", fmt(s["reason"]),
              "", "by agent:", fmt(s["agent"], s["wb_agent"]),
              "", "by channel kind:", fmt(s["channel_kind"], s["wb_channel_kind"]),
              "", "by trigger kind:", fmt(s["trigger_kind"], s["wb_trigger_kind"]),
              "", "per day (turns, would block):"]
    lines += ["  %s %5d %5d" % (day, n, w) for day, (n, w) in sorted(s["day"].items())] or ["  (none)"]
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    path = os.path.expanduser(argv[0] if argv else DEFAULT_LOG)
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        print("cannot read the log: %s" % type(exc).__name__, file=sys.stderr)
        return 1
    print(report(summarize(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
