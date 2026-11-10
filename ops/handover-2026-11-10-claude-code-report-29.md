# REPORT 29 - Loop 7 (APR-0126): finish P-36, the missing daily reset of the CHO, CoS and CFO channel sessions

Date: 2026-11-10 (AST), 14:28 to 15:20. Machine: the Loop 1 to 4 VM. Synthetic data only. The pull was the only live action (APR-0126 was on top). Part 1 ran in scratch and was deleted. Part 2 was NOT done, because Part 1 did not confirm the cause, as the handover orders. Nothing live changed: no crontab line, no script, no config, no plugin, no gateway restart, health-check.py not replaced.

## Plain verdict for P-36
- Cause as stated in handover 29 (agent-to-agent path skips the stale check): NOT confirmed. `sessions_send` reset the sessions in the scratch test.
- What the evidence does show: the setting works on every route. The real cause of the live picture is the traffic. The three live channel sessions have received no inbound user message since 10-29 (only that evening's real Slack messages, which reset them once). The check runs on a message that comes in through the inbound route; nothing else that wrote to those sessions ran it.
- Installed: nothing. Compaction job for the CHO, CoS and CFO: not installed (no Part 2).

## Part 1. Scratch test
Files: `ops/p36-channel-session-reset-finding.md` (new, the only file in the patch). Evidence in `h29/reset-test/`: scripts, replies, session tables before and after, session windows and reset markers per scratch agent, sanitized config, and the live event counts.
Setup: one scratch gateway (own state folder, port 19930, no Slack, no cron, cloud model, model key only in the process environment), the live `session` and `tools` blocks with atHour 15 (boundary 15:00 AST, outside 03:30 to 05:10) and agentToAgent enabled for the scratch agents. Messages before the boundary 14:29 to 14:31, after at 15:01. New run tags loop29-rst-*.
| route | session | before | after | reset marker |
|---|---|---|---|---|
| `openclaw agent --session-key` | main-style p1 | 1bd38e7b | 008b68b6 NEW | no |
| `openclaw agent --session-key` | channel-style q1 | a262d543 | 69e14e9d NEW | no |
| `sessions_send` from agent r | main-style p2 | 7b8857bb | 24c5670f NEW | no |
| `sessions_send` from agent r | channel-style q2 | 5122d0be | 8b66caaa NEW | no |
| gateway `chat.send` (stand-in for an inbound message) | channel-style q3 | edab78dc | edab78dc SAME, start time moved to 15:01 | yes, reason daily |
- The q3 result is the same shape as the live 10-29 resets (same session ID, start time moved, one marker). The other routes open a new session window with a new ID and no marker.
- q2 could not be reached by `sessions_send` before it existed (error "no session found"), so it was created by one direct message first; this is stated, not hidden.
- The `chat.send` route is only a stand-in for Slack. A real Slack message was not tested, and neither was the value 4 (inside the no-message window).
- Question "does a `sessions_send` after a real-style inbound route differently": not tested separately; the q3 and q2 results suggest no difference in whether the reset happens, but I did not run that exact sequence and do not claim it.
- Live read-only look (counts only, no text, database copies deleted): the CHO, CoS and CFO channel sessions hold 2 user messages each, both on 10-29; assistant messages: before 10-29 152 / 235 / 20, after 10-29 31 / 66 / 0. No user message and no reset event after 10-29 20:19. Which route wrote the later assistant messages I could not tell; it is none of the three tested routes (they would have produced new session IDs).
Cost: 9 short messages, not measured per run, well under 0.02 USD. The scratch gateway was stopped by pid after checking its state folder; the folder was deleted; one live gateway remains.

## Part 2. Not done
The prepared work is kept out of the patch: `h29/part2-prepared-not-in-patch/` holds `agent-compact.sh` (generalised from coo-compact.sh, log line ends with agent=<name>), the thin `coo-compact.sh` wrapper, `test_agent_compact.py`, and the health-check diff (three "newest <agent> compaction younger than 36 hours" lines). In scratch the 16 old COO tests passed unchanged through the wrapper and the new tests passed (23 in all). It can be applied and installed on the CEO's word in a new handover (three crontab lines at 05:30, 05:35, 05:40 AST). Rollback if ever installed: delete the lines marked lifeos-<agent>-compact.

## End state (rule 5)
- Gateway: one process, pid 3792080, not restarted. Crontab equal to its starting copy; config byte-equal to its backup; ledger and gate plugin files equal (`h29/crontab-end.txt`, `plugin-hashes-end.txt`). Calendar at the seed (journal 3 0; Prep was never run).
- Health check: PASS 77, WARN 0, FAIL 0, INFO 6. The handover asks for 78 or better. The one-point difference is not a fault: the line "log: MaxListenersExceededWarning" turned from PASS to INFO ("1 warning(s), 3 gateway start(s): known startup warning"). The scratch gateways (handover 28's two and today's one) write into the same daily log file as the live gateway, so their start-up warning is counted. It clears when the log rotates. I disclose it rather than edit the check.
- Unit suite OK. Validator: 1 blocking failure, "tracked file not in registry: ops/p36-channel-session-reset-finding.md", because the patch excludes artifacts.yaml as ordered; the planning chat adds that entry.
- Time window: nothing between 03:30 and 05:10; no agent run near 05:25 to 05:40.

## Patch and package
`~/handover/handover29.patch`: 1 new file, docs only, no artifacts.yaml, no commit, no push; applies to a fresh clone. `~/handover-29.tar.gz`: report, patch and h29/ only. The stray `~/lifeos-ro/0` is still there (not in the patch).

## For the CEO
1. P-36: the setting is fine; the sessions are not reset because nothing real arrives by the inbound route. The only fix that works without CEO messages is option B (morning compaction), already built and tested in scratch, not installed because the handover required the cause first. Say "install B" for a new handover, or leave it.
2. Planning chat: add the registry entry for the new ops note.
