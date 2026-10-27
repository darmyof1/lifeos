# Report 2 (handover 2, 2026-10-26)

## A. Gateway keep-alive
- Before: started by me with setsid/nohup (parent pid 1, no terminal). It would survive an SSH disconnect but not a crash or a reboot.
- Now: a systemd user service, unit openclaw-loop1-gateway.service (copy in ~/handover/openclaw-loop1-gateway.service, installed at ~/.config/systemd/user/). It runs node .../openclaw/dist/index.js gateway run with OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH set as in env.sh, EnvironmentFile=slack.env and openai.env (values never printed), log appended to ~/loop1/gateway.log, Restart=always (5 s), KillSignal SIGINT. Enabled for login; linger is already yes, so it also starts at boot and survives every logout.
- Verified: one gateway process; Slack socket mode connected for all four accounts; a kill -9 of the main pid was followed by an automatic restart (new pid, one process, Slack reconnected in about 50 s); parent is the systemd user manager, no tty.
- Done during a quiet time (no run in progress); one restart for the switch, one for the crash test.
- CEO commands (any terminal on the VM, as ubuntu): systemctl --user status openclaw-loop1-gateway | stop | start | restart. Log: tail -f ~/loop1/gateway.log. Always stop it before changing any AGENTS.md. Do not start a second gateway by hand (setsid or T1) while the service runs: the check "one process" would fail. Stopping may take up to 330 s (graceful drain); it normally takes a few seconds.
- The older unit ~/.config/systemd/user/openclaw-gateway.service (from 2026-10-19, disabled, default state dir) is not used. I left it alone.

## B. 04:00 reset history (P-36)
- VM time zone: America/Santo_Domingo (AST, -0400, no DST). Cron uses it.
- Logs: /tmp/openclaw only holds 10-25 and 10-26 (older ones are gone) and have no reset lines. The evidence is in the agents' sqlite stores (read-only): session_nodes, transcript_events with their created_at times, and reset markers inside transcripts.
- Finding 1 (clear): the COO Slack channel session keeps ONE session ID (30e7a56a) since 10-23 23:13. A reset is a marker written inside that session ("reset" event), not a new ID. COO: reason "daily" at 10-24 18:41:08 AST = the first message after 04:00 that day (lazy reset confirmed). After that every reset marker is reason "new" (the CEO's @COO /new): 10-25 23:57:40 and 10-26 15:56:31 were /new at the first message after 04:00, so those nights show "new", not "daily"; the daily reset cannot be told apart there, because /new came first.
- Finding 2 (main sessions): main session IDs changed at the first activity after 04:00 on each night: 10-23 cos 19:43, cfo 21:52, cho 23:18; 10-24 coo 18:42, cho 18:41, cos 18:41, cfo 18:51; 10-25 cos 23:49, cfo 23:49, cho 23:58; 10-26 cho 15:57, cos 15:57; cfo main has had no message since 04:00 today, so a reset is pending (normal). Caveat: the prep compact (--max-lines 1) ran at about the same times, so for these stubs I cannot separate "daily reset" from "compaction". The 7.7 observation of 10-23 (CoS new ID at the first message after 04:00) agrees.
- Finding 3: for the CHO, CoS and CFO channel sessions no reset marker is readable in the store (only the COO's was); their IDs stayed the same (cho 1bc85fa1, cos 4079c376, cfo e533212d). I cannot prove from evidence that those reset daily. The report will show it from tomorrow.
- Nights with no message after 04:00 and no evidence: 10-23 for the channel sessions (created that evening).
- Script: ~/loop1/daily-reset-report.sh (wrapper) and ~/loop1/daily-reset-report.py (copies in ~/handover/). Read-only on the agents (sqlite mode=ro, no messages, no state change), prints no secrets. Cron line: 0 5 * * * bash $HOME/loop1/daily-reset-report.sh >> $HOME/loop1/reset-check/cron.out 2>&1 (05:00 AST). Output: gateway process count and uptime; per agent and per session (main, slack): ID, same or new ID against the previous day's snapshot, and either "reset applied HH:MM (reason)", "first message after 04:00 at HH:MM" or "no message since 04:00, reset pending (normal)". Appends to ~/loop1/reset-check/report.log and snapshots.jsonl (append-only), posts to the COO channel via openclaw message send with the target and account from ~/loop1/gcal-sync/env. Flag --dry-run prints only.
- Ran once for real at 20:05 AST: it posted "yes" to the COO channel; today's snapshot is saved, so tomorrow's 05:00 compares with it.

## C. Real calendar test (P-40 item 2), result
- Login reaches the real calendar (read via gcal_list.py with GCAL_CALENDAR set in the shell only; nothing written to a file in the repo or to ~/loop1/gcal-sync/env).
- Privacy: titles of non-LifeOS events were never shown or saved (a filter showed only counts). Window 2026-10-26 to 2026-11-08: 5 non-LifeOS events before and 5 after (identical list of start/end values); 0 LifeOS events before and after. The test day 2026-11-04 had 0 other events before and after.
- Test journal and state: ~/loop1/gcal-sync-real (journal copy in ~/handover/realcal-test-journal.md). Event: CHO - Realcal test - 11042026-9901.
- 1 dry run (would create) then create 14:00 to 14:30: created, list showed the title in full.
- 2 move (moved + written, same run ID rc1, event ID rc1-02): dry run "moved in place"; real run "moved in place", same Google ID, 15:00 to 15:30; list confirmed.
- 3 raise privacy (written with privacy=high, event rc1-03): "made busy", same Google ID; list showed the title busy at 15:00 to 15:30 and the mandated title gone.
- 4 delete with --busy-key rc1-03, approval note "CEO handover 2, 2026-10-26": deleted; list afterwards: 0 LifeOS events and 0 other events on the day.
- Final: counts unchanged; no LifeOS test event remains; ~/loop1/gcal-sync/env still holds the test calendar (no real calendar address in it); the */5 cron line and the stress-ng line are unchanged; the repo clone is clean.

## For the CEO to decide / record
- APR for the systemd user service as the gateway's owner (T1 no longer needed), and for the 05:00 reset report cron.
- P-36: the daily reset is confirmed once (COO 10-24, reason daily). CHO/CoS/CFO channel sessions need the first 05:00 reports to confirm. Since /new resets first, a "daily" reason will only appear on a night when the first message after 04:00 is not /new.
- P-40: the real-calendar path works end to end (create, move in place, busy, delete). Switching the cron to the real calendar is your decision; I did not.

## Files for the repo (in ~/handover/)
- openclaw-loop1-gateway.service, daily-reset-report.sh, daily-reset-report.py, realcal-test-journal.md, REPORT-2.md (and from before: REPORT.md, loop1-v191-upgrade.sh).
