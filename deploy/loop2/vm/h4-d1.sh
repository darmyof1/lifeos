#!/usr/bin/env bash
# h4-d1.sh RUN - one D1 delete run: prep, CEO instruction to the COO, journal lines, check (job runs with the cron flag)
source ~/loop1/env.sh; R=$1
~/loop1/h4-post.sh "Handover 5, run $R (D1 delete, CEO instruction) started"
~/loop1/scenario-run.sh prep $R 2>&1 | grep -E "STOP|READY|numstat"
timeout 290 openclaw agent --agent coo --session-id $R-coo --timeout 280 -m "Loop 2 scenario run, run ID $R. I am the CEO. Delete the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar. Wait for the result, then tell me in 3 lines what changed, who changed it, and what is still needed from me." 2>&1 | tail -4 | cut -c1-400
echo "--- journal"; grep -E "$R" ~/loop1/workspaces/cos/state/calendar-journal.md | cut -c1-230; git -C ~/loop1/workspaces/cos diff --numstat state/calendar-journal.md
~/loop1/scenario-run.sh check $R --skip-checker 2>&1 | grep -E "summary|done|skip|CRON: A" | cut -c1-150
