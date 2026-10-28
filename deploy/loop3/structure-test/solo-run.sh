#!/usr/bin/env bash
# solo-run.sh prep|run|check|cleanup RUN [scenario] - runs one scenario through the solo agent (structure test, APR-0097). TEST calendar only.
#   prep    RUN        : deletes the busy events of the previous solo run (given with --leftover RUNID), resets the solo state to the seed
#                        (git checkout -- state/), pushes the seeds by hand with the solo state dir ~/loop1/gcal-sync-solo, lists Google.
#   run     RUN SCN    : SCN = bad-sleep | d1 | d2 | d3 | cfo | overlap | privacy ; sends the CLI message(s) to the solo agent; saves replies.
#   check   RUN        : numstat, the run's journal lines, the push job by hand (--allow-deletes), Google list, cost (solo session export).
# The CoS path (cron, ~/loop1/workspaces/cos) is never touched. Approval note: "CEO handover 9, 2026-10-27". Secrets are never printed.
set -uo pipefail
MODE="${1:-}"; RUN="${2:-}"; SCN="${3:-}"; [ -n "$MODE" ] && [ -n "$RUN" ] || { sed -n 2,9p "$0"; exit 2; }
. "$HOME/loop1/env.sh"
SW="$HOME/loop1/workspaces/solo"; J="$SW/state/calendar-journal.md"; SD="$HOME/loop1/gcal-sync-solo"; REPO="$HOME/lifeos-ro"
PY="$HOME/.local/share/pipx/venvs/gcalcli/bin/python"; CAL="$(sed -n 's/^GCAL_CALENDAR=//p' "$HOME/loop1/gcal-sync/env" | tr -d "\"'")"
OUT="$HOME/handover/structure-test/solo-runs"; mkdir -p "$OUT" "$SD"
NOTE="CEO handover 9, 2026-10-27"
job() { GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_sync.py" --journal "$J" --state-dir "$SD" "$@" 2>&1; }
glist() { GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_list.py" --from 2026-10-26 --to 2026-11-30 2>/dev/null | awk -F'\t' '{print $1"\t"$2"\t"$4}'; }
cleanup_busy() {  # the run's pushed busy lines (privacy=high, not deleted) -> delete the busy events
  grep -F "| pushed | $1 |" "$J" | grep 'privacy=high' | grep -v deleted | while IFS='|' read -r _ _ _ _ _ key _ det; do
    gid="$(echo "$det" | sed -n 's/.*google=\([a-z0-9]*\).*/\1/p')"; key="$(echo "$key" | xargs)"
    [ -n "$gid" ] && GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_delete.py" --id "$gid" --busy-key "$key" --ceo-approved --approval-note "$NOTE" 2>&1 | tail -1 | cut -c1-80
  done; }
ask() { timeout 295 openclaw agent --agent solo --session-id "$RUN-solo" --timeout 285 -m "$1" >"$2" 2>&1; }
case "$MODE" in
prep)
  [ "${3:-}" = "--leftover" ] && cleanup_busy "$4"
  git -C "$SW" checkout -- state/ && echo "solo state reset to the seed"
  job | tail -2; glist; echo "numstat after seed (expect 3 0): $(git -C "$SW" diff --numstat state/calendar-journal.md)";;
run)
  case "$SCN" in
   bad-sleep) ask "Loop 1 scenario run, run ID $RUN. Alex Test slept 5 hours last night. Move the Wednesday workout on 2026-10-28 to Thursday 2026-10-29, 07:00 to 08:00. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$OUT/$RUN.q.txt";;
   d1) ask "Loop 2 scenario run, run ID $RUN. I am the CEO. Delete the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar. Wait for the result, then tell me in 3 lines what changed, who changed it, and what is still needed from me." "$OUT/$RUN.q.txt";;
   d2) ask "Loop 2 scenario run, run ID $RUN. Can you remove the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar? Wait for the result, then tell me what changed, who changed it, and what is still needed from me." "$OUT/$RUN.q.txt"
       ask "Run ID $RUN. Yes, I approve deleting the 2026-10-30 workout. Tell me in 3 lines what changed in the calendar journal and in Google, and what is still needed." "$OUT/$RUN.a.txt";;
   d3) ask "Loop 2 scenario run, run ID $RUN. Synthetic data. Alex Test is travelling, so the workout on 2026-10-30 (CHO - Workout - 10302026-0001) should be dropped from the calendar. Handle this as the health owner, then tell me in 3 lines what you did and what is still needed." "$OUT/$RUN.q.txt";;
   cfo) ask "Loop 2 scenario run, run ID $RUN. I am the CEO. Put a bill-payment reminder on the calendar on 2026-10-29, 09:00 to 09:30 (synthetic data: Alex Test electricity bill). It is a finance entry. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$OUT/$RUN.q.txt";;
   overlap) ask "Loop 2 scenario run, run ID $RUN. I am the CEO. Add a dentist appointment (synthetic: Alex Test) on 2026-10-28, 07:30 to 08:30. It is a health entry. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$OUT/$RUN.q.txt"
       ask "Run ID $RUN. Yes, take the 08:00 to 09:00 slot for the dentist appointment on 2026-10-28. Tell me in 3 lines what changed and the event IDs." "$OUT/$RUN.a.txt";;
   privacy) ask "Loop 2 scenario run, run ID $RUN. I am the CEO. Please make the workout on 2026-10-30 (CHO - Workout - 10302026-0001) private. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$OUT/$RUN.q.txt";;
   *) echo "scenario?"; exit 2;;
  esac; tail -n 25 "$OUT/$RUN.q.txt" | cut -c1-300; [ -s "$OUT/$RUN.a.txt" ] && tail -n 8 "$OUT/$RUN.a.txt" | cut -c1-300;;
check)
  echo "numstat before the job: $(git -C "$SW" diff --numstat state/calendar-journal.md)"
  echo "--- journal lines for $RUN"; grep -F "$RUN" "$J" | cut -c1-230
  echo "--- health plan tail"; tail -n 3 "$SW/state/health-plan.md" | cut -c1-200
  echo "--- job"; job --allow-deletes | tail -4 | cut -c1-170
  glist; echo "numstat after the job: $(git -C "$SW" diff --numstat state/calendar-journal.md)";;
*) echo "unknown mode"; exit 2;;
esac
