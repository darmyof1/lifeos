#!/usr/bin/env python3
"""Check the sessions_send calls of one scenario run against instruction set v1.7 (APR-0075, P-38).

Reads the trajectory exports of the CHO and the CoS (events.jsonl) written by
  openclaw sessions export-trajectory --session-key "agent:<id>:main" --workspace <dir> --output <run ID>-<id>
and prints every sessions_send call with its result, then PASS/FAIL/WARN lines.
Read-only. Exit code 1 if any check FAILs.

Usage:
  python3 scripts/verify/check_sessions_send.py EXPORTS_DIR RUN_ID [--since ISO_UTC]
  EXPORTS_DIR  the folder that holds <RUN_ID>-cho and <RUN_ID>-cos (…/.openclaw/trajectory-exports)
  --since      only count events at or after this UTC time, for example 2026-10-26T04:07:00Z.
               One export holds the whole session, so earlier runs are in it unless you cut them off.
"""
import argparse
import json
import os
import sys

MARKER = "SESSION_WORK_START_CHANGED"


def parse_ts(s):
    """ISO time to a sortable string of the form YYYY-MM-DDTHH:MM:SS.mmm (UTC). Z suffix optional."""
    s = (s or "").strip()
    if s.endswith("Z"):
        s = s[:-1]
    if "." not in s:
        s += ".000"
    return s


def agent_of(session_key):
    parts = (session_key or "").split(":")
    return parts[1] if len(parts) > 1 and parts[0] == "agent" else ""


def target_of(args):
    key = args.get("sessionKey") or ""
    if key:
        a = agent_of(key)
        if a:
            return a
    return args.get("agentId") or ""


def result_text(data):
    try:
        return data["result"]["content"][0]["text"]
    except Exception:
        r = data.get("result", "")
        return r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)


def result_status(data, text):
    try:
        body = json.loads(text)
        if isinstance(body, dict):
            st = body.get("status")
            if st:
                return str(st)
    except Exception:
        pass
    return "error" if data.get("success") is False else "ok"


def load_calls(path, since):
    """Return a list of dicts, one per sessions_send call, with its result."""
    calls, pending = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            data = d.get("data") or {}
            if data.get("name") != "sessions_send":
                continue
            ts = parse_ts(d.get("ts"))
            if since and ts < since:
                continue
            if d.get("type") == "tool.call":
                call = {"ts": ts, "sender": agent_of(d.get("sessionKey")), "args": data.get("args") or {},
                        "id": data.get("toolCallId"), "status": "no result", "text": ""}
                calls.append(call)
                pending.append(call)
            elif d.get("type") == "tool.result":
                text = result_text(data)
                match = None
                for c in pending:
                    if c["id"] and c["id"] == data.get("toolCallId"):
                        match = c
                        break
                if match is None and pending:
                    match = pending[0]
                if match is not None:
                    pending.remove(match)
                    match["text"] = text
                    match["status"] = result_status(data, text)
    return calls


def short(text, n=110):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n] + "..."


def run(exports, run_id, since):
    since = parse_ts(since) if since else ""
    calls = []
    for agent in ("cho", "cos"):
        path = os.path.join(exports, "%s-%s" % (run_id, agent), "events.jsonl")
        if not os.path.exists(path):
            print("MISSING: %s" % path)
            return 2
        calls += load_calls(path, since)
    calls.sort(key=lambda c: c["ts"])
    print("sessions_send calls (UTC):")
    for c in calls:
        a = c["args"]
        print("  %s %s -> %s  mode=%s watch=%s timeoutSeconds=%s  => %s  %s" % (
            c["ts"][11:23], c["sender"] or "?", target_of(a) or "?", a.get("mode", "-"), a.get("watch", "-"),
            a.get("timeoutSeconds", "-"), c["status"], short(c["text"])))
    if not calls:
        print("  (none)")

    fails, warns = [], []

    def check(ok, label, detail=""):
        print("%s  %s%s" % ("PASS" if ok else "FAIL", label, ("  (" + detail + ")") if detail else ""))
        if not ok:
            fails.append(label)

    cho_to_cos = [c for c in calls if c["sender"] == "cho" and target_of(c["args"]) == "cos"]
    cos_to_cho = [c for c in calls if c["sender"] == "cos" and target_of(c["args"]) == "cho"]

    check(len(cho_to_cos) >= 1, "CHO sent to the CoS", "%d call(s)" % len(cho_to_cos))
    if cho_to_cos:
        first = cho_to_cos[0]
        a = first["args"]
        check(a.get("mode") == "followup", "first CHO call uses mode followup", "mode=%s" % a.get("mode", "-"))
        check("watch" not in a, "first CHO call does not set watch")
        check(a.get("timeoutSeconds") == 120, "first CHO call has timeoutSeconds 120", "timeoutSeconds=%s" % a.get("timeoutSeconds", "-"))
        check(first["status"] == "ok", "first CHO call returned ok (a reply)", "status=%s" % first["status"])
        if len(cho_to_cos) > 1:
            warns.append("CHO sent %d calls to the CoS (v1.7 allows one resend)" % len(cho_to_cos))
    check(len(cos_to_cho) == 0, "CoS sent nothing to the CHO", "%d call(s)" % len(cos_to_cho))
    marker_hits = [c for c in calls if MARKER in c["text"]]
    check(not marker_hits, "no %s in any sessions_send result" % MARKER, "%d result(s)" % len(marker_hits))

    others = [c for c in calls if c not in cho_to_cos and c not in cos_to_cho]
    if others:
        warns.append("%d other sessions_send call(s), see the list above" % len(others))
    for w in warns:
        print("WARN  " + w)
    print("Result: %s" % ("FAIL (%d)" % len(fails) if fails else "all checks passed"))
    return 1 if fails else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("exports_dir")
    p.add_argument("run_id")
    p.add_argument("--since", default="")
    ns = p.parse_args(argv)
    return run(os.path.expanduser(ns.exports_dir), ns.run_id, ns.since)


if __name__ == "__main__":
    sys.exit(main())
