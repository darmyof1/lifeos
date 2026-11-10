# Loop 6 scope: hardening of the four agents (CFO send list, COO morning compaction)

Approved by APR-0121 (CEO, 2026-11-09). Synthetic data and the Google TEST calendar only. There is no second human in this project and no real-calendar work: both are dropped, not parked.

## Plain-language summary
1. CFO send list: the CFO's written instructions say it may message only the COO; the live setting also lets it message the CoS. The CEO chose COO only. The live setting is tightened to match the text. No agent instruction text changes.
2. COO morning compaction: the COO sometimes answers a first request from old memory (measured 4 of 6 right without a compaction, 6 of 6 with). A scheduled compaction of the COO's Slack channel session runs every day at 05:25 AST (after the 05:00 report, outside 03:30 to 05:10). One new cron line; rollback is deleting that line.

## What is built
1. One config key: agents.entries.cfo.tools.agentToAgent.send goes from ["coo","cos"] to ["coo"] (backup and a diff of that key only; CFO scenarios still pass).
2. scripts/ops/coo-compact.sh: dry run by default (--execute to act); refuses inside 03:30 to 05:10 AST; skips and logs if the COO channel session had a message in the last 10 minutes or a CEO request is waiting (a pending line without an answer); one log line per run in ~/loop1/state/coo-compact.log (time, result, session size before and after, no message text); exit codes documented; tests.
3. One crontab line: `25 5 * * * bash $HOME/lifeos-ro/scripts/ops/coo-compact.sh --execute >> $HOME/loop1/state/coo-compact.cron.log 2>&1 # lifeos-coo-compact`. No other crontab line changes.
4. Health-check lines: CFO send list equals ["coo"] (PASS; WARN otherwise); newest COO compaction younger than 36 hours (PASS; WARN otherwise, INFO before the first run).

## Pass criteria
- CFO: the live key shows ["coo"], nothing else in the config differs; the CFO scenarios still pass; a CFO turn that tries to send to the CoS is refused or never happens (shown in a log line).
- Compaction: a manual run outside the window works and is logged; the COO still answers the next first request correctly; the cron line fires once by cron (use a temporary extra line a few minutes ahead, removed afterwards, as in Loop 4) and is logged; the first real 05:25 run is read by the next handover or the health check.
- Crontab differs from its starting copy only by the new line; agent instructions, plugins (ledger, gate in shadow mode) and the delete gate are unchanged; tests and validator pass; health check PASS 75 or better with WARN 0 FAIL 0.

## Not in this loop
Enforcing the privacy gate; other chiefs; isolation; real data; the local-model box. (No second-human test and no real-calendar work, by the CEO's decision.)
