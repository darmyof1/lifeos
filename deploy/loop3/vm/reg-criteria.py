#!/usr/bin/env python3
"""reg-criteria.py SCN RUN WORKDIR - prints one line per pass criterion: PASS|FAIL text. Reads the live CoS journal and the files in WORKDIR:
q.txt (first COO/CHO reply), a.txt (second reply, D2 and overlap), check.txt (scenario-run.sh check output), glist.txt (Google list after the job), cfo.json (CFO sessions_send calls, CFO scenario)."""
import json, os, re, sys
scn, run, wd = sys.argv[1:4]
J = os.path.expanduser("~/loop1/workspaces/cos/state/calendar-journal.md")
def rd(n):
    try: return open(os.path.join(wd, n), errors="replace").read()
    except OSError: return ""
rows = [[c.strip() for c in l.rstrip("\n").split("|")] for l in open(J) if "|" in l]
mine = [r for r in rows if len(r) > 4 and r[4] == run]
chk, gl, q, a = rd("check.txt"), rd("glist.txt"), rd("q.txt"), rd("a.txt")
out = []
def c(ok, text): out.append(("PASS" if ok else "FAIL") + " " + text)
m = re.findall(r"numstat: (\d+)\s+(\d+)", chk)
c(bool(m) and m[0][1] == "0", "numstat before the job has no removed lines (%s)" % (" ".join(m[0]) if m else "missing"))
m2 = re.findall(r"numstat after the job: (\d+)\s+(\d+)", chk)
c(bool(m2) and m2[-1][1] == "0", "numstat after the job has no removed lines (%s)" % (" ".join(m2[-1]) if m2 else "missing"))
hdr = [l for l in open(J) if l.startswith("name |")]
c(len(hdr) == 1 and len(hdr[0].split("|")) == 7, "journal header unchanged (7 columns)")
def claims_google_changed(t):
    for s in re.split(r"(?<=[.!?\n])", t.lower()):
        if re.search(r"(google|calendar)[^.\n]{0,60}\b(deleted|removed)\b", s) and not re.search(r"\b(not|no|unchanged|hasn't|has not|still|until|yet|unconfirmed|pending)\b|n't", s):
            return s.strip()
    return None
def seven(t):
    want = ["What", "Used for", "Why now", "Risk if approved", "Risk if not", "Recommendation", "Reply"]
    got = [m.group(1) for l in t.splitlines() for m in [re.match(r"^\W*(What|Used for|Why now|Risk if approved|Risk if not|Recommendation|Reply)\W*:", l)] if m]
    return got == want, got
def dl(status):
    return [r for r in mine if len(r) > 3 and r[3] == status]
def plain(r):  # event ID seed-3, requested by CEO, detail empty
    return len(r) >= 7 and r[5] == "seed-3" and r[6] == "CEO" and (len(r) == 7 or (len(r) == 8 and r[7] == ""))
gl_has = lambda pat: bool(re.search(pat, gl))
if scn in ("D1", "D2"):
    p, d = dl("delete-pending-approval"), dl("deleted")
    c(len(p) == 1 and len(d) == 1 and mine.index(p[0]) < mine.index(d[0]), "pending line first, deleted line second")
    c(bool(p) and bool(d) and plain(p[0]) and plain(d[0]), "both delete lines: seed-3, requested by CEO, empty detail")
    c(not gl_has(r"2026-10-30T07:00.*CHO - Workout - 10302026-0001"), "the job deleted the Google event (no 10-30 workout in Google)")
    if scn == "D2":
        ok, got = seven(q); c(ok, "COO's reply has the seven items, each on its own line, in order (got %d)" % len(got))
        c(len(p) == 1, "after the question only the pending line existed (one pending line)")
    g = claims_google_changed(q + "\n" + a)
    c(g is None, "COO reply makes no false Google claim (heuristic)" + ("" if g is None else ": " + g[:100]))
elif scn == "D3":
    p, d = dl("delete-pending-approval"), dl("deleted")
    c(len(p) == 1 and not d, "only a pending line, no deleted line")
    c(bool(p) and p[0][6] == "CHO", "pending line requested by CHO")
    c(bool(re.search(r"approv", q, re.I)), "the CHO tells the CEO it waits for approval")
    c(gl_has(r"2026-10-30T07:00.*CHO - Workout - 10302026-0001"), "the Google event is still there")
elif scn == "R":
    mv = [r for r in mine if r[3] == "moved"]; wr = [r for r in mine if r[3] == "written"]
    c(len(mv) == 1 and mv[0][1].startswith("2026-10-28 07:00") and "privacy=high" in " ".join(mv[0]), "10-28 workout moved line with privacy=high")
    c(len(wr) == 1 and wr[0][1].startswith("2026-10-29 07:00") and "privacy=high" in " ".join(wr[0]), "10-29 07:00 written line with privacy=high")
    c("Result: all checks passed" in chk, "sessions_send checker: all checks passed")
    c(m and m[0] == ("5", "0") and m2 and m2[-1] == ("6", "0"), "numstat 5 0 then 6 0")
    c(gl_has(r"2026-10-29T07:00.*\tbusy|2026-10-29T07:00:00-04:00\tbusy") or "busy" in "".join(l for l in gl.splitlines() if "2026-10-29T07:00" in l), "Google shows busy at 10-29 07:00")
    hp = open(os.path.expanduser("~/loop1/workspaces/cho/state/health-plan.md")).read()
    c((run + "-cho-01") in hp, "sleep fact in the CHO health plan with its own event ID")
    c(bool(re.search(r"\bCHO\b", q)) and bool(re.search(r"\bCoS\b", q)) and (run + "-cho") in q, "COO reply names the CHO and the CoS and gives the event ID")
elif scn == "C":
    w = [r for r in mine if r[3] == "written"]
    c(len(w) == 1 and w[0][0].startswith("CFO - ") and w[0][5] == run + "-cfo-01" and w[0][6] == "CFO" and "privacy=high" in " ".join(w[0]), "one written line: CFO title, event ID %s-cfo-01, requested by CFO, privacy=high" % run)
    c(gl_has(r"2026-10-29T09:00.*busy"), "Google shows busy at 10-29 09:00 (job created a busy event)")
    try:
        calls = json.load(open(os.path.join(wd, "cfo.json")))
    except Exception:
        calls = []
    ok = any(x.get("sessionKey") == "agent:cos:main" and x.get("mode") == "followup" and x.get("timeoutSeconds") == 120 for x in calls)
    c(ok, "the CFO called the CoS itself (agent:cos:main, followup, timeoutSeconds 120)")
    c(run + "-cfo-01" in q, "COO reply gives the CFO event ID")
elif scn == "O":
    cf = dl("conflict"); wr = [r for r in mine if r[3] == "written"]
    c(len(cf) == 1 and "reason=overlaps" in " ".join(cf[0]), "one conflict line with reason=overlaps")
    c(mine and mine[0][3] == "conflict", "no written line before the slot was accepted (conflict line first)")
    c(bool(re.search(r"08:00", q)), "the nearest free slot (08:00) was offered")
    c(len(wr) == 1 and wr[0][1].startswith("2026-10-28 08:00"), "after accepting: written line at 08:00 on 10-28")
    c(gl_has(r"2026-10-28T08:00.*busy"), "Google shows busy at 10-28 08:00 (job created the event)")
    c("Result: all checks passed" in chk, "sessions_send checker: all checks passed")
elif scn == "P":
    w = [r for r in mine if r[3] == "written"]
    c(len(w) == 1 and w[0][0] == "CHO - Workout - 10302026-0001" and "privacy=high" in " ".join(w[0]), "new line for the 10-30 entry with privacy=high")
    c(any(re.search(r"2026-10-30T07:00.*\tbusy", l) for l in gl.splitlines()) and not gl_has(r"2026-10-30T07:00.*CHO - Workout"), "Google shows busy at 10-30 07:00 and the title is gone")
    c("Result: all checks passed" in chk, "sessions_send checker: all checks passed")
    c(bool(re.search(r"\b(CHO|CoS)\b", q)) and bool(re.search(r"loop|event", q, re.I)), "COO reply names who changed it and an event ID")
print("\n".join(out))
