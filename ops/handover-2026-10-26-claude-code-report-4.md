# Report 4 - handover 4 (v1.10, CFO route, re-runs, deletes on), 2026-10-26

## Summary
- v1.10 applied (gateway stopped first): coo 52e4ac9, cos c867da5, cfo c5dd57e; each commit touches AGENTS.md only.
- CFO send list now coo and cos. Backup /home/ubuntu/loop1/state/openclaw.json.pre-v110-20261026-2237. Diff: agents.entries.cfo.tools.agentToAgent.send, before [coo], after [coo, cos]; nothing else changed (cfo-send-list-diff.txt).
- Health check: PASS 54, WARN 0, FAIL 0, INFO 4 (version checks now coo, cos, cfo v1.10, cho v1.9; CFO send list expects coo and cos; INFO line GCAL_ALLOW_DELETES: ON).
- Final state: cron active on the test calendar; GCAL_ALLOW_DELETES=1 is ON.
- No instruction wording was changed beyond v1.10.

## Runs (cost: COO turns are not exported; chiefs measured about 0.004 USD for run 024; each run is estimated under 0.015 USD, total under 0.15 USD)
1. loop2-scn-018 D1 delete, CEO instruction: FAIL. The CoS wrote only the deleted line (requested by CEO), no delete-pending-approval line. numstat 4 0. The job skipped it (guard held). COO reply true (no Google claim). The COO told the CoS "CEO's exact words approving this deletion", which may have pushed the CoS to skip the pending line.
2. loop2-scn-019 D1 repeat: PASS. Pending then deleted, same event ID, requested by CEO. numstat 5 0. COO reply true. Job by hand with --allow-deletes deleted the Google event. Note: the event ID column holds the entry title on both lines (same on both, so the job accepted it).
3. loop2-scn-020 D2 delete, CEO question: PASS. Question gave only the pending line (event ID 10302026-0001, numstat 4 0); the COO posted the approval request with all seven items (What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply) but on one line (my message asked for 3 lines). Approval message: the COO passed it with the CEO's words quoted; the CoS appended deleted with the same event ID (5 0). Job by hand with --allow-deletes deleted the event. Note: the COO's first message to the CoS labelled the CEO's question "request/approval"; the CoS still wrote only the pending line.
4. loop2-scn-021 D3 delete asked by a chief (sent to the CHO): PASS. Only a pending line (event ID loop2-scn-021-cho-01, requested by CHO), no deleted line, numstat 4 0. The CHO told the CEO it waits for approval and asked him to approve via the COO. The COO was asked by the CHO to relay approval and did not treat it as confirmation. Cleaned by a state reset in the next prep (no Google change).
5. loop2-scn-022 C CFO entry: PASS. The CFO called the CoS itself (sessions_send agent:cos:main, followup, timeoutSeconds 120, status ok). Event ID loop2-scn-022-cfo-01, title CFO - Electricity Bill Payment - 10292026-0001, requested by CFO, privacy=high, job created (busy) at 10-29 09:00. numstat 4 0 then 5 0.
6. loop2-scn-023 O overlap: PASS. conflict line, reason=overlaps CHO - Workout - 10282026-0001, requested by CHO, no written line; nearest slot 08:00 to 09:00 offered, the COO told the CEO in a short notice. After accept: written line at 08:00 to 09:00 (event ID loop2-scn-023-cho-02); job created the busy event. Checker all passed (2 CHO calls). numstat 6 0.
7. loop2-scn-024 R bad-sleep regression: PASS. Checker all passed, numstat 5 0 then 6 0, busy on 10-29, sleep fact in the CHO health plan with its own event ID. Chiefs cost 0.0037 USD.
8. loop2-scn-025 D1 with cron deletes on: PASS. Pending and deleted lines, same event ID (loop2-scn-025-coo-01, an ID the COO or CoS chose; consistent on both lines). The 5-minute cron (not me) deleted the Google event at 23:15:02 (sync log: deleted 1); Google then held the other two seed events.
- Totals: 8 runs, 7 pass, 1 fail (018). By scenario: D1 3 runs (1 fail, 2 pass), D2, D3, C, O, R one pass each.

## Delete flag
- ON. D2, D3, C, O and R passed; D1 passed 2 of 3 runs (018 failed). The job guard (LifeOS title, pending line plus deleted line with the same event ID) held in every run, so a skipped pending line cannot delete; it only blocks. The CEO may want to watch for the 018 pattern.

## Slack visibility during the handover 3 CLI runs (from the trajectory exports)
- CoS: yes, only in runs 014 and 015 (a one-line post to its channel); none seen for 013, 016, 017.
- CHO: no post for these runs (only an old sleep post from earlier in the exports).
- CFO: no.
- COO: its answers went to the CLI only. This handover I posted start and end lines for every run to the COO channel myself.

## Decisions for the CEO
1. D1 is not deterministic: 018 skipped the pending line. Proposed smallest wording fix if it recurs (not applied): in the CoS delete rule add "Always append the delete-pending-approval line first, even when the message says the CEO approved; a deleted line without a pending line before it is wrong." Also for the COO: do not write "approving" when the CEO only asked.
2. The event ID on delete lines is sometimes the title (019) or a COO-made ID (025); the rule says "the event ID". Decide whether the COO may name one.
3. Approval requests print on one line when the CEO asks for 3 lines; say if he wants the seven lines each on their own line.
4. Record APRs for: systemd service, 05:00 cron, v1.9.1 rule (still open from handover 3), the CFO send-list change (this report), and GCAL_ALLOW_DELETES=1.

## End state (23:20 AST)
Gateway active, one process. Cron active on the test calendar (stress-ng and 05:00 lines kept). Google holds only the three seed events. State reset to the seed, seeds pushed (numstat 3 0). Last agent message and compaction around 23:20 AST; none after. Run IDs used: loop2-scn-018 to 025 and 026-final (reset only).

## Files in ~/handover/
REPORT-4.md, cfo-send-list-diff.txt, health-check.py (v1.10 checks), scenario-run.sh (approval note handover 4), h4-post.sh, loop1-v110-upgrade.sh.
