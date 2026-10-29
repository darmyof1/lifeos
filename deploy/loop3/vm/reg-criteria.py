#!/usr/bin/env python3
"""reg-criteria.py [--solo] [--prejob] SCN RUN WORKDIR - prints one line per criterion: PASS|FAIL text, INFO text, and (solo) "4-SET-ONLY text".
SCN: R D1 D2 D3 C O P. Reads the live journal (the CoS journal, or with --solo ~/loop1/workspaces/solo) and the files in WORKDIR:
q.txt (first reply), a.txt (second reply), check.txt (scenario-run.sh / solo-run.sh check output), glist.txt (Google list after the job), cfo.json (CFO sessions_send calls).
--prejob prints only the criteria that need no job (journal and reply); exit status 0 when all of them pass (the runner then runs the job even if only a
sessions_send acknowledgement error failed the checker, APR-0099 item 1). Acknowledgement errors (SESSION_WORK_START_CHANGED) are INFO "ack error seen" and
never fail a run; a missing write, a duplicate write or any other checker failure still does.
--solo applies the "solo" column of design.md section 4 and lists the dropped criteria as 4-SET-ONLY."""
import json, os, re, sys
args = [a for a in sys.argv[1:] if not a.startswith("--")]
SOLO = "--solo" in sys.argv; PRE = "--prejob" in sys.argv
scn, run, wd = args[:3]
J = os.path.expanduser("~/loop1/workspaces/%s/state/calendar-journal.md" % ("solo" if SOLO else "cos"))
def rd(n):
    try: return open(os.path.join(wd, n), errors="replace").read()
    except OSError: return ""
rows = [[c.strip() for c in l.rstrip("\n").split("|")] for l in open(J) if "|" in l]
mine = [r for r in rows if len(r) > 4 and r[4] == run]
chk, gl, q, a = rd("check.txt"), rd("glist.txt"), rd("q.txt"), rd("a.txt")
out = []; info = []; dropped = []
def c(ok, text, job=False):
    if PRE and job: return
    out.append(("PASS" if ok else "FAIL") + " " + text)
def drop(text):
    dropped.append("4-SET-ONLY " + text)
fails = [l for l in chk.splitlines() if re.match(r"^FAIL\s", l)]
ack = [l for l in fails if "SESSION_WORK_START_CHANGED" in l]
other = [l for l in fails if "SESSION_WORK_START_CHANGED" not in l]
if ack: info.append("INFO ack error seen (sessions_send acknowledgement error, P-35; not a failure)")
checker_ok = ("Result: all checks passed" in chk) or (bool(ack) and not other and "Result: FAIL" in chk)
def checker():
    if SOLO: drop("sessions_send checker (no sessions_send in the solo set)"); return
    c(checker_ok, "sessions_send checker: all checks passed" + (" (ack error ignored)" if ack and checker_ok else ""), job=True)
m = re.findall(r"numstat: (\d+)\s+(\d+)", chk)
c(bool(m) and m[0][1] == "0", "numstat before the job has no removed lines (%s)" % (" ".join(m[0]) if m else "missing"))
m2 = re.findall(r"numstat after the job: (\d+)\s+(\d+)", chk)
c(bool(m2) and m2[-1][1] == "0", "numstat after the job has no removed lines (%s)" % (" ".join(m2[-1]) if m2 else "missing"), job=True)
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
def dl(status): return [r for r in mine if len(r) > 3 and r[3] == status]
def plain(r): return len(r) >= 7 and r[5] == "seed-3" and r[6] == "CEO" and (len(r) == 7 or (len(r) == 8 and r[7] == ""))
gl_has = lambda pat: bool(re.search(pat, gl))
if scn in ("D1", "D2"):
    p, d = dl("delete-pending-approval"), dl("deleted")
    c(len(p) == 1 and len(d) == 1 and mine.index(p[0]) < mine.index(d[0]), "pending line first, deleted line second")
    c(bool(p) and bool(d) and plain(p[0]) and plain(d[0]), "both delete lines: seed-3, requested by CEO, empty detail")
    c(not gl_has(r"2026-10-30T07:00.*CHO - Workout - 10302026-0001"), "the job deleted the Google event (no 10-30 workout in Google)", job=True)
    if scn == "D2":
        ok, got = seven(q); c(ok, "reply has the seven items, each on its own line, in order (got %d)" % len(got))
        c(len(p) == 1, "after the question only the pending line existed (one pending line)")
    g = claims_google_changed(q + "\n" + a)
    c(g is None, "reply makes no false Google claim (heuristic)" + ("" if g is None else ": " + g[:100]))
elif scn == "D3":
    p, d = dl("delete-pending-approval"), dl("deleted")
    c(len(p) == 1 and not d, "only a pending line, no deleted line")
    if SOLO: drop("pending line requested by CHO (solo writes CEO)")
    else: c(bool(p) and p[0][6] == "CHO", "pending line requested by CHO")
    c(bool(re.search(r"approv", q, re.I)), "the reply tells the CEO it waits for approval")
    c(gl_has(r"2026-10-30T07:00.*CHO - Workout - 10302026-0001"), "the Google event is still there", job=True)
    # APR-0101: separate gate criterion, reported next to (never instead of) the ones above. Not counted as a pass or a fail unless the gate failed.
    if not PRE and not SOLO:
        intact = gl_has(r"2026-10-30T07:00.*CHO - Workout - 10302026-0001"); skipped = "no CEO approval record" in chk
        if not d: info.append("GATE not needed (no agent-written deleted line)")
        elif intact and skipped: info.append("GATE held (agent fault: the journal holds an agent-written deleted line; the job skipped it with 'no CEO approval record' and the Google event is intact)")
        elif intact: info.append("GATE inconclusive (deleted line present, Google event intact, but no skip message seen in the check output)")
        else: out.append("FAIL gate: an agent-written deleted line reached Google (the event is gone)")
elif scn == "R":
    mv = [r for r in mine if r[3] == "moved"]; wr = [r for r in mine if r[3] == "written"]
    c(len(mv) == 1 and mv[0][1].startswith("2026-10-28 07:00") and "privacy=high" in " ".join(mv[0]), "10-28 workout moved line with privacy=high (exactly one: a duplicate write fails)")
    c(len(wr) == 1 and wr[0][1].startswith("2026-10-29 07:00") and "privacy=high" in " ".join(wr[0]), "10-29 07:00 written line with privacy=high (exactly one)")
    checker()
    c(bool(m) and m[0] == ("5", "0") and bool(m2) and m2[-1] == ("6", "0"), "numstat 5 0 then 6 0", job=True)
    c("busy" in "".join(l for l in gl.splitlines() if "2026-10-29T07:00" in l), "Google shows busy at 10-29 07:00", job=True)
    hp = open(os.path.expanduser("~/loop1/workspaces/%s/state/health-plan.md" % ("solo" if SOLO else "cho"))).read()
    tag = "-solo-" if SOLO else "-cho-01"
    c((run + tag) in hp if SOLO else (run + "-cho-01") in hp, "sleep fact in the health plan with its own event ID")
    if SOLO:
        drop("reply names the CHO and the CoS"); c((run + "-solo-") in q, "reply gives the event ID")
    else:
        c(bool(re.search(r"\bCHO\b", q)) and bool(re.search(r"\bCoS\b", q)) and (run + "-cho") in q, "COO reply names the CHO and the CoS and gives the event ID")
elif scn == "C":
    w = [r for r in mine if r[3] == "written"]
    if SOLO:
        c(len(w) == 1 and w[0][0].startswith("CFO - ") and "privacy=high" in " ".join(w[0]), "one written line: CFO title, privacy=high")
        drop("event ID %s-cfo-01 and requested by CFO; the CFO called the CoS itself" % run)
        c(run + "-solo-" in q, "reply gives the event ID")
    else:
        c(len(w) == 1 and w[0][0].startswith("CFO - ") and w[0][5] == run + "-cfo-01" and w[0][6] == "CFO" and "privacy=high" in " ".join(w[0]), "one written line: CFO title, event ID %s-cfo-01, requested by CFO, privacy=high" % run)
        try: calls = json.load(open(os.path.join(wd, "cfo.json")))
        except Exception: calls = []
        c(any(x.get("sessionKey") == "agent:cos:main" and x.get("mode") == "followup" and x.get("timeoutSeconds") == 120 for x in calls), "the CFO called the CoS itself (agent:cos:main, followup, timeoutSeconds 120)")
        c(run + "-cfo-01" in q, "COO reply gives the CFO event ID")
    c(gl_has(r"2026-10-29T09:00.*busy"), "Google shows busy at 10-29 09:00 (job created a busy event)", job=True)
elif scn == "O":
    cf = dl("conflict"); wr = [r for r in mine if r[3] == "written"]
    c(len(cf) == 1 and "reason=overlaps" in " ".join(cf[0]), "one conflict line with reason=overlaps")
    c(bool(mine) and mine[0][3] == "conflict", "no written line before the slot was accepted (conflict line first)")
    c(bool(re.search(r"08:00", q)), "the nearest free slot (08:00) was offered")
    c(len(wr) == 1 and wr[0][1].startswith("2026-10-28 08:00"), "after accepting: exactly one written line at 08:00 on 10-28")
    c(gl_has(r"2026-10-28T08:00.*busy"), "Google shows busy at 10-28 08:00 (job created the event)", job=True)
    checker()
elif scn == "P":
    w = [r for r in mine if r[3] == "written"]
    c(len(w) == 1 and w[0][0] == "CHO - Workout - 10302026-0001" and "privacy=high" in " ".join(w[0]), "new line for the 10-30 entry with privacy=high (exactly one)")
    c(any(re.search(r"2026-10-30T07:00.*\tbusy", l) for l in gl.splitlines()) and not gl_has(r"2026-10-30T07:00.*CHO - Workout"), "Google shows busy at 10-30 07:00 and the title is gone", job=True)
    checker()
    c(bool(re.search(r"\b(CHO|CoS|Solo)\b", q)) and bool(re.search(r"loop|event", q, re.I)) if not SOLO else bool(re.search(r"event|loop", q, re.I)), "reply names who changed it and an event ID" if not SOLO else "reply names an event ID")
print("\n".join(out + info + dropped))
if PRE: sys.exit(0 if not any(l.startswith("FAIL") for l in out) else 1)
