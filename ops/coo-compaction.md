# COO morning compaction (Loop 6, APR-0121)

What: once a day at 05:25 AST the COO's Slack channel session is compacted, so the first CEO request of the day is answered from fresh context. Handover 23 measured 4 of 6 right without a compaction and 6 of 6 with one (small sample).

Script: `scripts/ops/coo-compact.sh` (dry run by default, `--execute` to act). Same command as handover 23: `openclaw sessions compact <COO Slack channel session> --agent coo --max-lines 1`. The session key is found at run time (the one key that starts with `agent:coo:slack:channel:`), so no Slack ID is stored in the repo.

Rules, in this order:
1. Refuses inside 03:30 to 05:10 AST (exit 2).
2. Skips and logs when the COO channel session had a message in the last 10 minutes.
3. Skips and logs when a CEO request is waiting (the newest journal line of an event is `requested` or `delete-pending-approval`).
4. Otherwise compacts and logs the size before and after.

Exit codes: 0 compacted, dry run, or skipped; 2 refused (time window); 3 error; 64 bad option.

Log: `~/loop1/state/coo-compact.log`, one line per run: time (AST), mode, result, size in tokens before and after (after is `unknown` until the session's next turn), lines kept. Never message text, never a session ID. Cron output goes to `~/loop1/state/coo-compact.cron.log`.

Cron line (one line, marked for removal):

    25 5 * * * bash $HOME/lifeos-ro/scripts/ops/coo-compact.sh --execute >> $HOME/loop1/state/coo-compact.cron.log 2>&1 # lifeos-coo-compact

Rollback: delete the line marked `lifeos-coo-compact` from the crontab (`crontab -l | grep -v lifeos-coo-compact | crontab -`). Nothing else changes.

Health check: INFO until the first run, PASS while the newest run is younger than 36 hours, WARN after that or when the newest run ended in an error.

Note on Loop 6 item 1 (CFO send list): skipped by the CEO's decision. The CFO's instructions (v1.10, APR-0092) send calendar entries straight to the CoS, so the live list stays `["coo","cos"]`. The note saying "COO only" was wrong.
