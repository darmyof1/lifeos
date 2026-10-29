#!/usr/bin/env bash
# solo-run.sh - runs scenarios through the solo agent (structure test, APR-0097, APR-0099). TEST calendar only. The CoS path (cron, ~/loop1/workspaces/cos) is never touched.
#   solo-run.sh prep  RUN [--leftover PREVRUN]  : deletes the busy events of the previous solo run, resets the solo state to the seed (git checkout -- state/),
#                                                 compacts the solo MAIN session (same command as scenario-run.sh does for the four agents) and reads its output (any
#                                                 error means STOP), pushes the seeds by hand with the solo state dir ~/loop1/gcal-sync-solo, lists Google.
#   solo-run.sh run   RUN SCN                   : SCN = bad-sleep | d1 | d2 | d3 | cfo | overlap | privacy ; sends the CLI message(s) to the solo agent's main session.
#   solo-run.sh check RUN                       : numstat, the run's journal lines, the push job by hand (--allow-deletes), Google list, numstat after.
#   solo-run.sh one   RUN SCN [PREVRUN]         : prep + run + check + criteria (reg-criteria.py --solo) + cost and metrics; writes
#                                                 ~/handover/structure-test/comparison/<RUN>.txt and <RUN>.metrics.json. Refuses to start inside 02:30 to 05:10 AST.
# Approval note: "CEO handover 10, 2026-10-27". Secrets are never printed.
set -uo pipefail
MODE="${1:-}"; RUN="${2:-}"; SCN="${3:-}"; [ -n "$MODE" ] && [ -n "$RUN" ] || { sed -n 2,12p "$0"; exit 2; }
. "$HOME/loop1/env.sh"; export TZ=America/Santo_Domingo
SW="$HOME/loop1/workspaces/solo"; J="$SW/state/calendar-journal.md"; SD="$HOME/loop1/gcal-sync-solo"; REPO="$HOME/lifeos-ro"
PY="$HOME/.local/share/pipx/venvs/gcalcli/bin/python"; CAL="$(sed -n 's/^GCAL_CALENDAR=//p' "$HOME/loop1/gcal-sync/env" | tr -d "\"'")"
CMP="$HOME/handover/structure-test/comparison"; QD="${SOLO_TMP:-$(mktemp -d)}"; mkdir -p "$CMP" "$SD"
NOTE="CEO handover 10, 2026-10-27"
job() { GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_sync.py" --journal "$J" --state-dir "$SD" "$@" 2>&1; }
glist() { GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_list.py" --from 2026-10-26 --to 2026-11-30 2>/dev/null | awk -F'\t' '{print $1"\t"$2"\t"$4}'; }
cleanup_busy() {  # the run's pushed busy lines (privacy=high, not deleted) -> delete the busy events
  grep -F "| pushed | $1 |" "$J" | grep 'privacy=high' | grep -v deleted | while IFS='|' read -r _ _ _ _ _ key _ det; do
    gid="$(echo "$det" | sed -n 's/.*google=\([a-z0-9]*\).*/\1/p')"; key="$(echo "$key" | xargs)"
    [ -n "$gid" ] && GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_delete.py" --id "$gid" --busy-key "$key" --ceo-approved --approval-note "$NOTE" 2>&1 | tail -1 | cut -c1-80
  done; }
# same message text as the suite, without the routing words; one persistent main session (agent:solo:main)
askl() {  # APR-0101: ask, then write the CEO ledger line for event seed-3 (D1, and D2's second message); the solo job does not use the ledger
  ask "$1" "$2"; python3 "$HOME/loop1/ceo-ledger.py" append "$RUN" seed-3 "$1" >/dev/null; }
ask() { timeout 295 openclaw agent --agent solo --session-key agent:solo:main --timeout 285 -m "$1" >"$2" 2>&1; }
do_prep() {  # do_prep [--leftover PREVRUN]
  [ "${1:-}" = "--leftover" ] && cleanup_busy "${2:-}"
  git -C "$SW" checkout -- state/ && echo "solo state reset to the seed"
  local T OUT RC; T="$(cat "$HOME/loop1/gateway-token")"
  OUT="$(openclaw sessions compact "agent:solo:main" --agent solo --max-lines 1 --token "$T" 2>&1)"; RC=$?
  echo "compact solo: $(echo "$OUT" | grep -iE 'compact|error|fail|check the' | head -2 | tr '\n' ' ' | cut -c1-160)"
  if echo "$OUT" | grep -qi "Session agent:solo:main not found"; then echo "compact solo: main session not created yet (first run), nothing to compact"
  elif [ $RC -ne 0 ] || echo "$OUT" | grep -qiE 'error|fail|check the control ui|unable|cannot|not reachable'; then echo "STOP: compact output for solo looks like an error"; return 1; fi
  echo "$OUT" | grep -qE 'Compacted session|No compaction needed|not created yet' || echo "$OUT" | grep -qi "not found" || { echo "STOP: unexpected compact output for solo"; return 1; }
  local try; for try in 1 2 3; do   # a transient Google error during the seed push (seen in loop3-cmp-s-008) leaves the seeds unpushed: retry
    job | tail -2; [ "$(git -C "$SW" diff --numstat state/calendar-journal.md | cut -f1)" = "3" ] && break
    echo "seed push attempt $try did not give numstat 3 0; retrying in 20 s"; sleep 20; done
  glist | cut -c1-120; echo "numstat after seed (expect 3 0): $(git -C "$SW" diff --numstat state/calendar-journal.md)"; }
do_run() {
  case "$1" in
   bad-sleep) ask "Loop 1 scenario run, run ID $RUN. Alex Test slept 5 hours last night. Move the Wednesday workout on 2026-10-28 to Thursday 2026-10-29, 07:00 to 08:00. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$QD/q.txt";;
   d1) askl "Loop 2 scenario run, run ID $RUN. I am the CEO. Delete the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar. Wait for the result, then tell me in 3 lines what changed, who changed it, and what is still needed from me." "$QD/q.txt";;
   d2) ask "Loop 2 scenario run, run ID $RUN. Can you remove the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar? Wait for the result, then tell me what changed, who changed it, and what is still needed from me." "$QD/q.txt"
       askl "Run ID $RUN. approve seed-3. Tell me in 3 lines what changed in the calendar journal and in Google, and what is still needed." "$QD/a.txt";;
   d3) ask "Loop 2 scenario run, run ID $RUN. Synthetic data. The workout on 2026-10-30 (CHO - Workout - 10302026-0001) should be dropped from the calendar because Alex Test is travelling. Handle this as the health owner, then tell me in 3 lines what you did and what is still needed." "$QD/q.txt";;
   cfo) ask "Loop 2 scenario run, run ID $RUN. I am the CEO. Put a bill-payment reminder on the calendar on 2026-10-29, 09:00 to 09:30 (synthetic data: Alex Test electricity bill). It is a finance entry. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$QD/q.txt";;
   overlap) ask "Loop 2 scenario run, run ID $RUN. I am the CEO. Add a dentist appointment (synthetic: Alex Test) on 2026-10-28, 07:30 to 08:30. It is a health entry. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$QD/q.txt"
       ask "Run ID $RUN. Yes, take the 08:00 to 09:00 slot for the dentist appointment on 2026-10-28. Tell me in 3 lines what changed and the event IDs." "$QD/a.txt";;
   privacy) ask "Loop 2 scenario run, run ID $RUN. I am the CEO. Please make the workout on 2026-10-30 (CHO - Workout - 10302026-0001) private. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$QD/q.txt";;
   *) echo "scenario?"; return 2;;
  esac; }
do_check() {
  echo "numstat: $(git -C "$SW" diff --numstat state/calendar-journal.md)"
  echo "--- journal lines for $RUN"; grep -F "$RUN" "$J" | cut -c1-230
  echo "--- health plan tail"; tail -n 3 "$SW/state/health-plan.md" | cut -c1-200
  echo "--- job"; job --allow-deletes | tail -4 | cut -c1-170
  glist; echo "numstat after the job: $(git -C "$SW" diff --numstat state/calendar-journal.md)"; }
case "$MODE" in
prep)  shift 2; do_prep "$@";;
run)   do_run "$SCN"; tail -n 25 "$QD/q.txt" | cut -c1-300; [ -s "$QD/a.txt" ] && tail -n 8 "$QD/a.txt" | cut -c1-300;;
check) do_check;;
one)
  PREV="${4:-}"; CODE=""; case "$SCN" in bad-sleep) CODE=R;; d1) CODE=D1;; d2) CODE=D2;; d3) CODE=D3;; cfo) CODE=C;; overlap) CODE=O;; privacy) CODE=P;; *) echo "scenario?"; exit 2;; esac
  NOW=$(( 10#$(date +%H) * 60 + 10#$(date +%M) )); END=$((NOW + 4))
  if [ "$NOW" -lt 310 ] && [ "$END" -gt 150 ]; then echo "REFUSED: $RUN would run into 02:30 to 05:10 AST"; exit 1; fi
  F="$CMP/$RUN.txt"; mkdir -p "$QD"; : >"$QD/a.txt"
  { echo "== $RUN  solo  $SCN  $(date '+%F %H:%M') AST"; echo "-- prep"
    if [ -n "$PREV" ]; then do_prep --leftover "$PREV"; else do_prep; fi; } >"$F" 2>&1
  if grep -q "^STOP" "$F"; then echo "$RUN: prep STOPPED, see $F"; exit 1; fi
  T0="$(date -u +%FT%TZ)"; S0=$(date +%s); do_run "$SCN"; WALL=$(( $(date +%s) - S0 ))
  do_check >"$QD/check.txt" 2>&1; glist >"$QD/glist.txt"
  openclaw sessions export-trajectory --session-key "agent:solo:main" --workspace "$HOME/loop1/evidence/traj" --output "$RUN-solo" >/dev/null 2>&1
  COST="$(python3 "$HOME/loop1/run-cost.py" "$RUN" "$T0" solo 2>&1 | tail -1)"; MET="$(python3 "$HOME/loop1/run-metrics.py" "$RUN" "$T0" solo 2>&1 | tail -1)"
  echo "$MET" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); d['wall_s']=$WALL; d['variant']='solo'; d['scenario']='$CODE'; print(json.dumps(d))" >"$CMP/$RUN.metrics.json" 2>/dev/null
  CRIT="$(python3 "$HOME/loop1/reg-criteria.py" --solo "$CODE" "$RUN" "$QD" 2>&1)"
  NP="$(echo "$CRIT" | grep -c '^PASS')"; NF="$(echo "$CRIT" | grep -c '^FAIL')"; RES=PASS; [ "$NF" -gt 0 ] && RES=FAIL
  { echo "-- reply of the agent (first message)"; sed -e 's/^/   /' "$QD/q.txt" | tail -n 25 | cut -c1-300
    [ -s "$QD/a.txt" ] && { echo "-- reply (second message)"; sed -e 's/^/   /' "$QD/a.txt" | tail -n 8 | cut -c1-300; }
    echo "-- check output"; cut -c1-200 "$QD/check.txt"
    echo "-- criteria"; echo "$CRIT"; echo "-- cost: $COST"; echo "-- metrics (wall ${WALL}s): $MET"; echo "RESULT $RUN $RES ($NP pass, $NF fail)"; } >>"$F"
  echo "$RUN $SCN $RES ($NP pass, $NF fail) cost $(echo "$COST" | sed -n 's/.*total \([0-9.]*\) USD.*/\1/p') wall ${WALL}s";;
*) echo "unknown mode"; exit 2;;
esac
