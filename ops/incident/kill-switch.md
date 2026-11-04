# Kill switch

Status: draft, drilled once on 2026-11-01 (APR-0112). Owner: the CEO. Script: scripts/ops/kill-switch.sh.

## When to use it
Use it when you think the system is doing something it should not and you want it to stop now, without deciding why: a wrong delete, a message you did not expect, a leaked token, two gateways, a runaway cost. It stops what acts. It deletes nothing and changes no agent file, config or journal.

## What it does
| Step | Action |
|---|---|
| 1 | Checks there is exactly one calendar job line in the crontab (the line that runs gcal_sync_cron.sh). Otherwise it stops and changes nothing. |
| 2 | Saves a copy of the whole crontab to ~/loop1/kill-switch-crontab.<time> (mode 600) and writes ~/loop1/kill-switch.marker (mode 600) with the time and what was running. |
| 3 | Pauses the calendar job line (puts a # in front, the same way the regression suites do). No other line is touched: the stress-ng line and the 05:00 reset-report line stay as they are. |
| 4 | Stops the gateway service (openclaw-loop1-gateway). The agents cannot answer and Slack stops reaching them. |
| 5 | Prints the command to restore. |

## How to run it
- Look first (changes nothing): `bash ~/lifeos-ro/scripts/ops/kill-switch.sh`
- Act: `bash ~/lifeos-ro/scripts/ops/kill-switch.sh --execute`
- Look at the restore (changes nothing): `bash ~/lifeos-ro/scripts/ops/kill-switch.sh --restore`
- Put it back: `bash ~/lifeos-ro/scripts/ops/kill-switch.sh --restore --execute`
Without `--execute` it only prints what it would do. It refuses to run twice (the marker exists) and stops if the crontab does not have exactly one calendar line.

## What it does not do
It does not revoke tokens, change the Slack apps, stop the VM, stop the stress-ng line, or touch Google. If a token leaked: run the kill switch, then revoke the token in its own console (Slack, Google, OpenAI), then restore with the new token. If the VM itself is suspect, stop it in the Oracle console.

## Restore
`--restore --execute` un-pauses the calendar line, starts the gateway only if it was running at the kill, compares the crontab with the saved copy ("crontab identical" or a warning), and removes the marker. A line that was already paused by a regression suite before the kill stays paused. After a restore run the health check (expect 73 PASS or better, 0 WARN, 0 FAIL) and look at the first cron run in ~/loop1/gcal-sync/sync.log.

## Drill, 2026-11-01 (outside the 03:30 to 05:10 AST window)
| Step | Result |
|---|---|
| Dry run | printed the two actions; nothing changed |
| `--execute` | 1.5 seconds; calendar line paused (one line differed, with a # added); gateway stopped (0 processes); marker mode 600; stress-ng line untouched |
| `--restore --execute` | 5.0 seconds (the script waits 5 seconds, then checks); gateway active, one process; crontab identical to the saved copy (diff empty) |
| Health check after | PASS 73, WARN 0, FAIL 0, INFO 4 (the INFO is the known startup warning after any gateway start) |
Evidence: the drill output files are in the handover package (kill-switch-drill/). The script has 13 unit tests with a fake systemctl and a fake crontab (tests/unit/test_kill_switch.py).
