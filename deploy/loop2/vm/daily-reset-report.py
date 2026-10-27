#!/usr/bin/env python3
"""daily-reset-report.py - 05:00 AST read-only report on the 04:00 session reset (P-36, APR-0059/0090).
Reads the agents' sqlite stores read-only, never messages an agent, never prints secrets.
Appends the report to ~/loop1/reset-check/report.log and a snapshot to snapshots.jsonl (append-only).
Posts to Slack with `openclaw message send` unless --dry-run (target/account from ~/loop1/gcal-sync/env).
Usage: daily-reset-report.py [--dry-run]"""
import datetime as dt, json, os, sqlite3, subprocess, sys
H = os.path.expanduser("~")
STATE = f"{H}/loop1/state"
OUT = f"{H}/loop1/reset-check"
TZ = dt.timezone(dt.timedelta(hours=-4))  # AST, no DST
AGENTS = ["coo", "cho", "cos", "cfo"]
now = dt.datetime.now(TZ)
cut = now.replace(hour=4, minute=0, second=0, microsecond=0)
cut_ms = int(cut.timestamp() * 1000)
hm = lambda ms: dt.datetime.fromtimestamp(ms / 1000, TZ).strftime("%m-%d %H:%M")

def db(a):
    return sqlite3.connect(f"file:{STATE}/agents/{a}/agent/openclaw-agent.sqlite?mode=ro", uri=True, timeout=5)

def gateway():
    n = int(subprocess.run("pgrep -af 'openclaw.*gateway' | grep -v pgrep | wc -l", shell=True, capture_output=True, text=True).stdout.strip() or 0)
    up = subprocess.run("systemctl --user show -p ActiveEnterTimestamp --value openclaw-loop1-gateway", shell=True, capture_output=True, text=True).stdout.strip()
    secs = subprocess.run("ps -o etimes= -p $(systemctl --user show -p MainPID --value openclaw-loop1-gateway)", shell=True, capture_output=True, text=True).stdout.strip()
    h = f"{int(secs)//3600}h{int(secs)%3600//60:02d}m" if secs.isdigit() else "unknown"
    return n, h

def last_snapshots():
    prev = {}
    try:
        for l in open(f"{OUT}/snapshots.jsonl"):
            j = json.loads(l)
            if j["date"] != str(now.date()):
                prev[(j["agent"], j["key"])] = j
    except FileNotFoundError:
        pass
    return prev

def inspect(a):
    """Returns rows for the main session and any slack channel session of the agent."""
    rows = []
    c = db(a)
    first_after = c.execute("select min(created_at) from transcript_events where created_at>=?", (cut_ms,)).fetchone()[0]
    for key, sid, ej in c.execute("select session_key,current_session_id,entry_json from session_nodes where session_key=? or session_key like ?",
                                  (f"agent:{a}:main", f"agent:{a}:slack:%")):
        e = json.loads(ej) if ej else {}
        reset = c.execute("select created_at,event_json from transcript_events where session_id=? and (event_json like '%\"type\": \"reset\"%' or event_json like '%\"type\":\"reset\"%') order by created_at desc limit 1", (sid,)).fetchone()
        r_at = r_why = None
        if reset:
            r_at, r_why = reset[0], json.loads(reset[1]).get("reason")
        first_s = c.execute("select min(created_at) from transcript_events where session_id=? and created_at>=?", (sid, cut_ms)).fetchone()[0]
        rows.append(dict(agent=a, key=key, sessionId=sid, sessionStartedAt=e.get("sessionStartedAt"),
                         first_in_session=first_s, first_agent=first_after, reset_at=r_at, reset_why=r_why))
    return rows

def main():
    dry = "--dry-run" in sys.argv
    n, up = gateway()
    prev = last_snapshots()
    lines = [f"Daily reset report {now:%Y-%m-%d %H:%M} AST (reset at 04:00 is applied at the first message after 04:00)",
             f"Gateway: {n} process{'es' if n != 1 else ''}{' (OK)' if n == 1 else ' (EXPECTED 1)'}, up {up}"]
    snaps = []
    for a in AGENTS:
        try:
            rows = inspect(a)
        except Exception as ex:
            lines.append(f"{a}: could not read ({type(ex).__name__})"); continue
        for r in rows:
            kind = "main" if r["key"].endswith(":main") else "slack"
            p = prev.get((a, r["key"]))
            changed = "no earlier snapshot" if not p else ("NEW ID since " + p["date"] if p["sessionId"] != r["sessionId"] else "same ID as " + p["date"])
            if r["reset_at"] and r["reset_at"] >= cut_ms:
                state = f"reset applied {hm(r['reset_at'])} ({r['reset_why']})"
            elif r["first_in_session"]:
                state = f"first message after 04:00 at {hm(r['first_in_session'])}"
            elif r["first_agent"]:
                state = f"other session of this agent had a message at {hm(r['first_agent'])}"
            else:
                state = "no message since 04:00, reset pending (normal)"
            lines.append(f"{a} {kind}: {r['sessionId'][:8]}, {changed}; {state}")
            snaps.append(dict(date=str(now.date()), time=now.strftime("%H:%M"), agent=a, key=r["key"], sessionId=r["sessionId"],
                              sessionStartedAt=r["sessionStartedAt"], resetAt=r["reset_at"], resetWhy=r["reset_why"]))
    lines.append("Note: a channel session keeps its ID on reset (a reset marker is written inside it); a main session gets a new ID.")
    text = "\n".join(lines)
    print(text)
    if dry:
        print("(dry run: nothing saved, nothing posted)"); return
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/snapshots.jsonl", "a") as f:
        for s in snaps: f.write(json.dumps(s) + "\n")
    with open(f"{OUT}/report.log", "a") as f:
        f.write(f"=== {now:%Y-%m-%d %H:%M}\n{text}\n")
    tgt, acc = os.environ.get("LIFEOS_ALERT_TARGET", ""), os.environ.get("LIFEOS_ALERT_ACCOUNT", "default")
    if not tgt:
        print("posted: no (LIFEOS_ALERT_TARGET not set)"); return
    r = subprocess.run(["openclaw", "message", "send", "--channel", "slack", "--account", acc, "--target", tgt, "--message", text],
                       capture_output=True, text=True, timeout=120)
    with open(f"{OUT}/report.log", "a") as f:
        f.write(f"post exit {r.returncode}\n")
    print("posted:", "yes" if r.returncode == 0 else f"FAILED exit {r.returncode}")
main()
