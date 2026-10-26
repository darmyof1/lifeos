# Report: loop2-scn-009 numstat 6 1 (handover to Claude Code, 2026-10-26)

## 1. Root cause
The CoS edited the journal header line (line 4). It added "| detail": "requested by" became "requested by | detail". That is the only changed line in the 6 1 / 7 1 diff. No seed line was touched. The job did not do it.
Evidence: CoS trajectory loop2-scn-009-cos, session 22:50:59 AST, seq 161, one edit tool call on state/calendar-journal.md. Its first edit replaced the header text and its second appended the moved and written lines.
Why: the v1.9 CoS rule defines the line format as "... | requested by | detail". The CoS saw the header did not match and "fixed" it.

## 2. Change
File: ~/loop1/workspaces/cos/AGENTS.md. Commit 78b71ff in the cos workspace, "Loop 1 instructions v1.9.1 (journal append only)". One line appended, nothing else changed (cho, cfo and the v1.9 line are untouched):
- Journal append only (instruction set v1.9.1): the header line "name | start | end | status | run ID | event ID | requested by" stays exactly as it is. The detail column is not added to it. Never edit, replace or delete an existing journal line, including the header. Only add new lines at the end of the file, and put privacy=high in the detail column of those new lines.
Script: ~/handover/loop1-v191-upgrade.sh (same pattern as the v1.9 script, safe to run twice, needs the gateway stopped).
Why smallest: it blocks the one behaviour seen (editing the header) and adds a line instead of rewriting v1.9.

## 3. Runs
- loop2-scn-010: VOID, my prep error. The CHO compaction failed right after the gateway restart and I did not read the error. The CHO remembered run 009, logged the sleep fact, and did not call the CoS. Not an instruction fault. The state was backed up as evidence/2026-10-26/loop2-scn-010-post-* and reset.
- loop2-scn-011: PASS. Numstat 5 0, then 6 0. Checker all passed (1 CHO call, followup, ok, no CoS send). Both CoS lines carry privacy=high. Sleep line with loop2-scn-011-cho-01. COO summary names the CHO and the CoS and gives -cho-01 and -cho-02. Google: one busy on 10-29 07:00, no Workout title for 10-28 or 10-29. Header untouched.
- loop2-scn-012: PASS, same results (numstat 5 0 then 6 0, event IDs loop2-scn-012-cho-01 and -cho-02).
- Log: 0 "maintenance paused". 1 "SQLite session write failed" for today, from the old gateway process (pid 3403610, before my restart), none from the current gateway (pid 3420522). P-37 stays closed.

## 4. For the CEO to record
- APR entry in your words for the v1.9.1 CoS rule above (text and commit 78b71ff).
- I now stop and start the gateway on your authority (given in this session). The gateway runs from my shell in the background, not your T1, with the log at ~/loop1/gateway.log. If you want T1 to own it again, stop mine (pkill -INT -f openclaw-gateway) and start yours.
- Prep lesson: after a gateway start, check each "sessions compact" output. An error line looks like "Check the Control UI or run openclaw gateway status". Fix: wait until the gateway is ready, then compact again.
- Open: the COO prompt wording "avoid duplicating an already-handled event" (P-39) can make the CHO skip the move when its memory is stale. It did not appear in 011 or 012 (clean sessions).

## 5. Repo-side (turn into a fix script on the Mac)
- ~/handover/loop1-v191-upgrade.sh to deploy/loop1/loop1-v191-upgrade.sh.
- ~/handover/REPORT.md into the decisions record.
- Optional: add "| detail" to the seed header in the cos seed state so the header matches the 8-column lines. Not needed now.
