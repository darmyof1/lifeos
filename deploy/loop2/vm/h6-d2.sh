#!/usr/bin/env bash
# h6-d2.sh RUN [LEFTOVER_ID LEFTOVER_KEY] - D2 run: question, approval, criteria, job; saves ~/handover/scenarios/results/RUN.txt
source ~/loop1/env.sh; R=$1; OUTF=~/handover/scenarios/results/$R.txt; mkdir -p ~/handover/scenarios/results
J=~/loop1/workspaces/cos/state/calendar-journal.md
{
~/loop1/h4-post.sh "Handover 6, run $R (D2 delete, CEO question then approval) started" >/dev/null
if [ -n "${2:-}" ]; then ~/loop1/scenario-run.sh prep $R --leftover-id "$2" --leftover-key "$3" 2>&1 | grep -E "STOP|READY|numstat"; else ~/loop1/scenario-run.sh prep $R 2>&1 | grep -E "STOP|READY|numstat"; fi
T0=$(date -u +%FT%TZ)
echo "== Q"; timeout 280 openclaw agent --agent coo --session-id $R-coo --timeout 270 -m "Loop 2 scenario run, run ID $R. Can you remove the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar? Wait for the result, then tell me what changed, who changed it, and what is still needed from me." 2>&1 | tail -12 | cut -c1-260
echo "-- journal after question"; grep -E "$R" $J | cut -c1-230
echo "== APPROVAL"; timeout 280 openclaw agent --agent coo --session-id $R-coo --timeout 270 -m "Run ID $R. Yes, I approve deleting the 2026-10-30 workout. Tell me in 3 lines what changed in the calendar journal and in Google, and what is still needed." 2>&1 | tail -5 | cut -c1-260
echo "-- delete lines (verbatim)"; grep -E "$R" $J
echo "-- criteria"
python3 - "$R" "$J" <<'P'
import sys
r,j=sys.argv[1:]
ls=[l.rstrip("\n") for l in open(j) if r in l]
c=[[x.strip() for x in l.split("|")] for l in ls]
ok=lambda b:"PASS" if b else "FAIL"
print(ok(len(c)==2 and c[0][3]=="delete-pending-approval" and c[1][3]=="deleted"),"pending first, then deleted")
print(ok(all(x[5]=="seed-3" and (len(x)==7 or (len(x)==8 and x[7]==""))  for x in c)),"event ID seed-3, detail column empty (7 columns, or an empty 8th)")
print(ok(all(x[6]=="CEO" for x in c)),"requested by CEO")
P
echo "approval request items on own lines (need 7): $(sed -n "/== Q/,/-- journal after/p" $OUTF | grep -cE "^\**(What|Used for|Why now|Risk if approved|Risk if not|Recommendation|Reply)\**:")"
git -C ~/loop1/workspaces/cos diff --numstat state/calendar-journal.md
~/loop1/scenario-run.sh check $R --skip-checker 2>&1 | grep -E "done|skip|conflict|CRON: A|numstat" | cut -c1-150
echo "-- journal tail"; tail -n 2 $J | cut -c1-230
echo "run window UTC: $T0 to $(date -u +%FT%TZ)"
} 2>&1 | tee $OUTF
