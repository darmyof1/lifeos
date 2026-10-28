# Structure test, step 2: one agent against the four-agent set (design, 2026-10-27)

Question for later, to be answered with data: does one agent holding the rules of all four domains, behind the same code guards, do the same scenarios as well as the four-agent set (COO, CHO, CoS, CFO)? Tonight is the design and a smoke test only. No counted comparison runs yet.

## 1. The solo agent
- Id `solo`, workspace `~/loop1/workspaces/solo` (a git repo), agent dir `~/loop1/state/agents/solo/agent`. CLI route only: `openclaw agent --agent solo --session-id <RUN>-solo ...`. No Slack binding, `agentToAgent.send` empty, not added to the agent-to-agent allow list.
- Same model (`openai/gpt-6-luna`) and the same tool policy as the CoS (files limited to the workspace; read, write, edit). Nothing else in the config changes.
- Files (in `structure-test/solo-agent-files/`, built by `compose-solo.py` from the repo copies in `agent-files/`, so they carry placeholders and no Slack ID): AGENTS.md (8413 bytes), SOUL.md, IDENTITY.md, USER.md (the same persona text as the other agents).
- Kept verbatim (taken by exact line prefix, the script fails if a line is missing): the CoS naming mandate and "Writing an entry" steps 1 to 3, the journal rules (never edit a line, header unchanged, append only, privacy mark format), event IDs, the move rule, the delete gate, the delete order and event ID rule, the plain delete lines rule, the health-facts rule (CHO), the CHO and CFO role lines, the records lines for state/health-plan.md and state/budget.md, "One answer".
- Dropped because they exist only for hand-offs: "You may send to" (all four), the routing table, all sessions_send rules (waiting, handoff call, acknowledgement errors, reply by answering, answer once), own-channel posts, FAILURE notes to the COO, "message other agents only with sessions_send", "every cross-agent message is shown...", late replies, handoff details, the CFO handoff call, "Your summary names every agent".
- Sentences I wrote or adapted myself (each is marked in AGENTS.md with an HTML comment; 2 are new, 9 are live rules with the hand-off words changed):
  1. (new) "You are the only agent. You receive the CEO's request and do all the work yourself: ... do not call sessions_send." (Role)
  2. (new) "Tell the CEO in one line about a conflict you logged: what happened, why it clashed, what you did and what it means for the day." (the COO's conflict notice, with the CoS as the source removed)
  3. (adapted) the CFO grocery-budget rule: "When a diet or meal plan changes, adjust ... state/budget.md" (the CFO's rule said "when the COO forwards").
  4. (adapted) "After you write a calendar entry, tell the CEO." (the COO's "When the CoS reports a calendar add, you notify the CEO").
  5. (adapted) Writing an entry step 4: "Reply to the CEO with the name and the event ID." (was: reply to the requester and the COO).
  6. (adapted) Privacy: domain-based. "every calendar entry for a health (CHO) or finance (CFO) matter is high privacy". The live rule keys on which chief asked.
  7. (adapted) Deletes v1.10: the "request comes from a chief" and "the COO passes on the approval" clauses removed; the CEO's later message is the approval.
  8. (adapted) Overlaps v1.10: "tell the COO" and "the real requester" replaced by the CEO.
  9. (adapted) Confirmed reports: "tell the CEO only what you wrote in the journal or state files yourself" (was: only what the CHO, CFO or CoS confirmed).
  10. (adapted) Approval requests: the COO's seven-item rule merged with the v1.10.1 and v1.10.3 layout rules, without "pass it to the CoS".
  11. (adapted) "Finish every request with one summary for the CEO ..." (was: what each agent changed).
  Also written: IDENTITY.md (name Solo, role line, an emoji) and SOUL.md (the three live soul sentences joined, no new text).
- Known consequence: event IDs the agent creates follow the live rule `<run ID>-<agent id>-<NN>` and so read `-solo-01`; `requested by` is always CEO.

## 2. Its state
`~/loop1/workspaces/solo/state/` holds copies of the committed seeds: calendar-journal.md (the CoS seed: header and the three seed lines; its sentence "Only the CoS writes here" is left as it is), health-plan.md (the CHO seed) and budget.md (the CFO seed). Committed in the solo workspace git. Reset between runs with `git checkout -- state/`.

## 3. The push job for solo
- By hand with `solo-run.sh`: `gcal_sync.py --journal ~/loop1/workspaces/solo/state/calendar-journal.md --state-dir ~/loop1/gcal-sync-solo [--allow-deletes]`, same test calendar, same code and rules as the cron (busy for privacy=high, delete only with pending plus deleted lines of the same event ID). The cron and the CoS path are untouched; the cron reads only the CoS journal.
- Google at the end of each solo run: `solo-run.sh prep` first deletes the busy events the previous run created (found from its own pushed lines, `gcal_delete.py --busy-key`, approval note "CEO handover 9, 2026-10-27"), then resets the solo state and pushes the seeds: events that exist by title are kept, a deleted seed workout is created again. Result: only the three seed events.
- The CoS path stays at its seed: no solo run reads or writes its journal, so a multi-agent run (scenario-run.sh prep) can follow straight after; its prep re-pushes the seeds by title. Solo runs and multi-agent runs are never run at the same moment.
- Session handling: each solo run uses its own session id, so no compaction is needed (the four live agents compact their main sessions in prep).

## 4. Criteria
Source: reg-criteria.py. "4-set" = how it is checked today; "solo" = how, or why dropped. Shared criteria use the same journal and Google checks for both.

| scenario | criterion | 4-set | solo |
|---|---|---|---|
| all | numstat before and after the job: no removed lines | scenario-run.sh numstat on the CoS journal | same, on the solo journal |
| all | header unchanged (7 columns) | CoS journal | solo journal |
| bad-sleep | 10-28 moved line, privacy=high | journal | same |
| bad-sleep | 10-29 07:00 written line, privacy=high | journal | same |
| bad-sleep | sessions_send checker all passed | check_sessions_send.py | dropped for solo (no sessions_send). Could make solo look better: the 4-set fails this on P-35 acknowledgement errors, solo cannot. |
| bad-sleep | numstat 5 0 then 6 0 | journal | same, but a duplicate write counts the same way |
| bad-sleep | Google shows busy at 10-29 07:00 | list | same |
| bad-sleep | sleep fact in health-plan with its own event ID | CHO health-plan | solo health-plan, ID `<run>-solo-NN` (pattern, not the `-cho-01` name) |
| bad-sleep | COO reply names the CHO and the CoS and the event ID | reply text | dropped for solo (no agents to name). Could make solo look better. Replaced by: reply gives the event ID and what changed. |
| D1 | pending then deleted, seed-3, requested by CEO, empty detail | journal | same |
| D1 | Google event deleted by the job | list | same |
| D1 | no false Google claim in the reply | reply heuristic | same |
| D2 | the seven items in order, each on its own line | reply | same |
| D2 | only a pending line after the question | journal | same |
| D3 | only a pending line, no deleted; requested by CHO | journal | pending only, no deleted; "requested by CHO" dropped (solo writes CEO). Neutral. |
| D3 | the CHO tells the CEO it waits | reply | the solo reply says it waits for approval |
| D3 | Google event still there | list | same |
| CFO | one written line, CFO title, event ID `<run>-cfo-01`, requested by CFO, privacy=high | journal | CFO title and privacy=high kept; event ID pattern and requested by dropped for solo. Neutral. |
| CFO | Google busy at 10-29 09:00 | list | same |
| CFO | the CFO called the CoS itself (followup, 120) | export | dropped for solo. Could make solo look better (the 4-set had hand-off faults in the past). |
| CFO | reply gives the CFO event ID | reply | reply gives the event ID |
| overlap | one conflict line, reason=overlaps | journal | same |
| overlap | no written line before accepting | journal | same |
| overlap | nearest free slot 08:00 offered | reply | same |
| overlap | written line at 08:00 after accepting; busy in Google at 08:00 | journal and list | same |
| overlap | checker all passed | check_sessions_send.py | dropped for solo (see above) |
| privacy | new line for 10-30 with privacy=high | journal | same |
| privacy | busy at 10-30 07:00, title gone | list | same |
| privacy | checker; reply names who changed it and an event ID | checker, reply | checker dropped; reply names an event ID |

Dropped criteria are all about hand-offs, which solo does not have. They can only make solo look better (a failure type it cannot have). The reading rule for the comparison: report the shared criteria first, and the dropped ones separately as "4-set only" faults, so they are not mistaken for a quality difference.

## 5. Metrics per run, both variants
For every run: pass or fail per criterion (shared and variant-only), input tokens and output tokens (summed over the exported sessions), cost (run-cost.py), number of agent turns and tool calls (counted in the exports), wall time (start to last reply), and the prompt size of each agent that ran: bytes of its four instruction files and the token count of its first turn (from the export). For the 4-set the sum over COO, CHO, CoS, CFO.

## 6. The counted comparison
- Three runs per scenario per variant, seven scenarios: 42 runs. Order: alternate variants within each scenario (4-set, solo, 4-set, solo, ...), scenarios in the suite order, new run IDs `loop3-cmp-001` and up (4-set) / `loop3-cmp-s-001` and up (solo). Same message text apart from the routing words.
- Estimated cost: 4-set about 0.007 USD per run (loop3-reg-001: 0.0455 for 7), solo expected lower, about 0.003 to 0.006. Total about 0.15 to 0.25 USD.
- Estimated time: about 3 to 5 minutes per 4-set run and about 1 to 2 minutes per solo run (no hand-offs), so about 2 to 2.5 hours in two sessions of about an hour each, outside 02:30 to 05:10 AST.
- Analysis: per scenario pass counts (x/3), the shared criteria first, cost and turns per variant, and the faults only the 4-set can have.
