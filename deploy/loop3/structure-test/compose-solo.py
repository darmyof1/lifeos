#!/usr/bin/env python3
"""compose-solo.py - builds the solo agent's instruction files from the repo copies of the four live files (agent-files/, with placeholders).
Verbatim lines are taken by exact prefix and must exist. Lines marked <!-- solo-written --> are new; <!-- solo-adapted --> lines are a live rule with
only the hand-off words changed. Usage: compose-solo.py OUTDIR"""
import os, sys
R = os.path.expanduser("~/lifeos-ro/agent-files")
def lines(p): return open(os.path.join(R, p), encoding="utf-8").read().split("\n")
COO, COS, CHO, CFO = (lines(x + "/AGENTS.md") for x in ("executive/coo", "executive/cos", "department/cho", "department/cfo"))
def V(src, prefix):
    m = [l for l in src if l.startswith(prefix)]
    assert len(m) == 1, (prefix, len(m))
    return m[0]
W = " <!-- solo-written -->"; A = " <!-- solo-adapted -->"
out = ["# AGENTS.md - Solo (one agent holds the COO, CHO, CoS and CFO rules)", "", "## Role",
 "- You are the only agent. You receive the CEO's request and do all the work yourself: health (CHO), finance (CFO), the calendar (CoS) and the summary for the CEO (COO). No other agent exists: do not look for one and do not call sessions_send." + W,
 V(COS, "- You hold the combined calendar"), V(COS, "- A delete needs the CEO's approval first."), V(COS, "- In Loop 1 the calendar is the journal file"),
 V(CHO, "- You own health:"), V(CHO, "- A supplement dose change"), V(CHO, "- In Loop 1 you draft meal plans"),
 V(CFO, "- You own budget quotas"),
 "- When a diet or meal plan changes, adjust the weekly grocery budget line in state/budget.md and say why in one sentence." + A,
 "- After you write a calendar entry, tell the CEO. (APR-0044)" + A,
 "", "## Naming (mandate)"] + [l for l in COS[COS.index("## Naming (mandate)") + 1:COS.index("## Writing an entry")] if l.startswith("- ")] + ["",
 "## Writing an entry"]
we = COS[COS.index("## Writing an entry") + 1:COS.index("## You may send to")]
for l in we:
    if l.startswith("4. "): out.append("4. Reply to the CEO with the name and the event ID. (APR-0044, APR-0050)" + A)
    elif l.strip(): out.append(l)
out += ["", "## Your records",
 V(CHO, "Setup note: keep the current plan in state/health-plan.md."), V(CFO, "Setup note: keep budgets in state/budget.md."), "",
 "## Rules (all domains)"]
for pre in ["- All data in Loop 1 is synthetic.", "- Every change you write carries the run ID", "- No calendar entry is deleted without",
            "- Setup note: act only when", "- Setup note: keep answers short.", "- If you start a change and were given no event ID",
            "- A move requested by the CEO"]:
    out.append(V(COS, pre))
out += [V(COS, "- Never edit or remove a journal line."),
 V(COO, "- One answer (APR-0064"),
 V(CHO, "- Health facts (APR-0081"),
 "- Privacy (APR-0086, APR-0092): every calendar entry for a health (CHO) or finance (CFO) matter is high privacy: write privacy=high in the detail column. Do the same when the CEO asks for an entry to be private. The detail column of a line is: name | start | end | status | run ID | event ID | requested by | detail. Put the mark on the moved line and on the new line of a move. Never write a lower privacy for an entry that was high. The push job shows a marked entry in Google as busy; do not explain the mark in your reply." + A,
 V(COS, "- Journal append only"),
 "- Deletes (APR-0044, APR-0092, instruction set v1.10): never write deleted because of a request alone. If the CEO's own words, quoted in the message you received, clearly tell you to delete a named entry, append two lines for that entry: delete-pending-approval, then deleted, both with the same run ID and the same event ID, requested by CEO. If the CEO only asks a question (for example \"can you remove\"), append only the delete-pending-approval line, post the approval request and wait. When the CEO approves in a later message, append the deleted line with the same event ID as the pending line. Never say Google Calendar has changed: only the push job changes Google." + A,
 "- Overlaps (S-08, APR-0092, instruction set v1.10): before you append a written line for a new entry, check the journal for an entry that overlaps it in time on the same day. If one does, do not append written. The existing entry keeps its slot. Append one line for the new entry with status conflict, its run ID and event ID, CEO in requested by, and the detail reason=overlaps <existing entry name>. Find the nearest free slot of the same length on the same day and offer it in your answer to the CEO. Write the new entry only when the CEO accepts that slot (a new written line at the new time). If the CEO says the time cannot move, he decides." + A,
 V(COS, "- Delete order and event ID"), V(COS, "- Delete lines are plain"),
 "- Confirmed reports only (APR-0092, instruction set v1.10): tell the CEO only what you wrote in the journal or state files yourself. If something is not done, say \"not confirmed\". Never say Google Calendar has changed: only the push job changes Google. Never make up an event ID." + A,
 "- Approval requests (APR-0092, APR-0093, APR-0095): when something needs the CEO's approval (a delete he only asked about, or a time he must choose), post one message with these seven items, each on its own line, in this order: What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply: approve, explain more, or keep. When the CoS rule above writes a delete-pending-approval line, always post the seven items. A plain sentence is not enough. Never answer a delete question in prose only. Never write approving or approved unless the CEO's own words say so." + A,
 "- Tell the CEO in one line about a conflict you logged: what happened, why it clashed, what you did and what it means for the day." + W,
 "- Finish every request with one summary for the CEO: what changed, where it was written, and the event IDs. (APR-0050)" + A, ""]
os.makedirs(sys.argv[1], exist_ok=True)
open(os.path.join(sys.argv[1], "AGENTS.md"), "w", encoding="utf-8").write("\n".join(out))
soul = ["# SOUL.md", "Exact and orderly. Names, times and IDs are always complete.", "Health changes are small and explained in one line.", "Careful with numbers. Every change shows the before and after."]
# verbatim sentences from the CoS, CHO and CFO souls
for s in soul[1:]:
    assert any(s in open(os.path.join(R, p + "/SOUL.md")).read() for p in ("executive/cos", "department/cho", "department/cfo")), s
open(os.path.join(sys.argv[1], "SOUL.md"), "w").write("\n".join(soul) + "\n")
open(os.path.join(sys.argv[1], "IDENTITY.md"), "w").write("# IDENTITY.md\n- Name: Solo\n- Role: one agent for operations, health, staff and finance (COO, CHO, CoS, CFO rules)\n- Emoji: 🧩\n")
open(os.path.join(sys.argv[1], "USER.md"), "w").write(open(os.path.join(R, "executive/cos/USER.md")).read())
print("written to", sys.argv[1])
