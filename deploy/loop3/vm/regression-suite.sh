#!/usr/bin/env bash
# regression-suite.sh SUITE [--only N] [--dry-run] - one-command Loop 3 regression suite on the TEST calendar (APR-0097).
#   SUITE   id prefix, e.g. loop3-reg-001; run IDs are <SUITE>-01 ... -07; the closing reset is <SUITE>-99-final.
#   1 bad-sleep-reschedule  2 D1 delete (CEO instruction)  3 D2 delete (CEO question, then approval)  4 D3 delete asked by a chief
#   5 CFO entry  6 overlap (conflict, offer, accept)  7 privacy request
# Uses ~/loop1/scenario-run.sh (prep, check), ~/loop1/reg-criteria.py (criteria), ~/loop1/run-cost.py (cost), ~/loop1/h4-post.sh (Slack lines).
# Writes ~/handover/regression/<SUITE>/<run>.txt per run and ~/handover/regression/<SUITE>.md (summary). Changes no instructions.
# Refuses to start if the suite would run into 02:30 AST through 05:10 AST. Pauses/resumes the cron safely (trap). Ends with a reset to the seed.
# The job step is the cron wrapper by hand (same code and GCAL_ALLOW_DELETES flag as the cron). Needs a running gateway (one process).
set -uo pipefail
SUITE="${1:-}"; [ -n "$SUITE" ] || { sed -n 2,6p "$0"; exit 2; }; shift
ONLY=""; DRY=0
while [ $# -gt 0 ]; do case "$1" in --only) ONLY="${2:-}"; shift;; --dry-run) DRY=1;; *) echo "unknown option $1"; exit 2;; esac; shift; done
# shellcheck disable=SC1091
. "$HOME/loop1/env.sh"
export TZ=America/Santo_Domingo
REPO="$HOME/lifeos-ro"; W="$HOME/loop1/workspaces"; PY="$HOME/.local/share/pipx/venvs/gcalcli/bin/python"
OUTD="$HOME/handover/regression"; RD="$OUTD/$SUITE"; SUM="$OUTD/$SUITE.md"; TMP="$(mktemp -d)"
EX="$HOME/loop1/evidence/traj/.openclaw/trajectory-exports"
NAMES=(x "bad-sleep-reschedule" "D1 delete (CEO instruction)" "D2 delete (CEO question, approval)" "D3 delete asked by a chief" "CFO entry" "overlap" "privacy request")
CODES=(x R D1 D2 D3 C O P)
RUNS="1 2 3 4 5 6 7"
if [ -n "$ONLY" ]; then
  [[ "$ONLY" =~ ^[1-7]$ ]] || { echo "--only takes 1 to 7"; exit 2; }
  RUNS="$ONLY"
fi

# ---- time window: no run that would touch 02:30 to 05:10 AST
NR=$(echo $RUNS | wc -w); EST=$(( NR * 5 + 3 )); NOW=$(( 10#$(date +%H) * 60 + 10#$(date +%M) )); END=$(( NOW + EST ))
overl() { [ "$1" -lt 310 ] && [ "$2" -gt 150 ]; }   # [start,end] against [02:30, 05:10] in minutes of the day
if overl "$NOW" "$END" || overl $((NOW - 1440)) $((END - 1440)); then
  echo "REFUSED: $NR run(s) need about $EST min; now $(date +%H:%M) AST; that runs into 02:30 to 05:10 AST (no agent messages, compaction or restarts then)."; exit 1
fi
cron_state() { local l; l="$(crontab -l 2>/dev/null | grep gcal_sync_cron.sh | head -1)"; case "$l" in '*/5'*) echo "CRON: ACTIVE (*/5)";; '#'*) echo "CRON: PAUSED";; *) echo "CRON: LINE MISSING";; esac; }
resume_cron() { crontab -l | sed 's|^#\(\*/5 .*gcal_sync_cron.sh\)|\1|' | crontab -; }
trap 'echo; resume_cron 2>/dev/null; cron_state' EXIT
post() { "$HOME/loop1/h4-post.sh" "$1" >/dev/null 2>&1; }
CAL="$(sed -n 's/^GCAL_CALENDAR=//p' "$HOME/loop1/gcal-sync/env" | tr -d "\"'")"
glist() { GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_list.py" --from 2026-10-26 --to 2026-11-30 2>/dev/null | awk -F'\t' '{print $1"\t"$2"\t"$4}'; }
if [ "$DRY" = 1 ]; then
  echo "[dry-run] suite $SUITE, runs: $RUNS, estimated $EST min, now $(date +%H:%M) AST: window ok"
  for n in $RUNS; do printf '[dry-run] %s-%02d  %s: prep, CLI message(s), criteria, check+job, cost, Slack start/end, result file\n' "$SUITE" "$n" "${NAMES[$n]}"; done
  echo "[dry-run] closing reset: ${SUITE}-99-final; summary $SUM"; exit 0
fi
N="$(pgrep -af 'openclaw.*gateway' | grep -E ' gateway run|openclaw-gateway| gateway --port' | grep -v -e pgrep -e grep -e 'bash -c' | wc -l)"
[ "$N" = 1 ] || { echo "STOP: gateway processes: $N (need 1)"; exit 1; }
mkdir -p "$RD"; WORK="$(mktemp -d)"
ask() {  # ask AGENT SESSION MESSAGE OUTFILE
  timeout 295 openclaw agent --agent "$1" --session-id "$2" --timeout 285 -m "$3" >"$4" 2>&1; }
cleanup_busy() {  # delete the busy events the run left in Google (the run's pushed lines with privacy=high, not deleted)
  local run="$1" gid key
  grep -F "| pushed | $run |" "$W/cos/state/calendar-journal.md" | grep 'privacy=high' | grep -v 'deleted' | while IFS='|' read -r _ _ _ _ _ key _ det; do
    gid="$(echo "$det" | sed -n 's/.*google=\([a-z0-9]*\).*/\1/p')"; key="$(echo "$key" | xargs)"
    [ -n "$gid" ] && GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_delete.py" --id "$gid" --busy-key "$key" --ceo-approved --approval-note "CEO handover 8, 2026-10-27" 2>&1 | tail -1 | cut -c1-80
  done
}
echo "| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |" > "$SUM.rows"
TOTAL=0; PASSN=0; FAILN=0; PREV=""
for n in $RUNS; do
  R="$(printf '%s-%02d' "$SUITE" "$n")"; S="${CODES[$n]}"; F="$RD/$R.txt"; WD="$WORK/$R"; mkdir -p "$WD"
  post "Regression $SUITE, run $R (${NAMES[$n]}) started"
  { echo "== $R  ${NAMES[$n]}  $(date '+%F %H:%M') AST"
    [ -n "$PREV" ] && { echo "-- cleanup of the previous run's busy events"; cleanup_busy "$PREV"; }
    echo "-- prep"; "$HOME/loop1/scenario-run.sh" prep "$R" 2>&1 | grep -E "STOP|READY|numstat|compact (coo|cho|cos|cfo):"
  } >"$F" 2>&1
  if grep -q "^STOP" "$F"; then echo "$R: prep STOPPED, see $F"; echo "| $R | ${NAMES[$n]} | FAIL | prep stopped | | |" >> "$SUM.rows"; FAILN=$((FAILN+1)); PREV="$R"; break; fi
  T0="$(date -u +%FT%TZ)"; SK=""
  case "$S" in
    R)  ask coo "$R-coo" "Loop 1 scenario run, run ID $R. Alex Test slept 5 hours last night. Move the Wednesday workout on 2026-10-28 to Thursday 2026-10-29, 07:00 to 08:00. Route this to the CHO, which owns health. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$WD/q.txt";;
    D1) ask coo "$R-coo" "Loop 2 scenario run, run ID $R. I am the CEO. Delete the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar. Wait for the result, then tell me in 3 lines what changed, who changed it, and what is still needed from me." "$WD/q.txt"; SK="--skip-checker";;
    D2) ask coo "$R-coo" "Loop 2 scenario run, run ID $R. Can you remove the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar? Wait for the result, then tell me what changed, who changed it, and what is still needed from me." "$WD/q.txt"
        ask coo "$R-coo" "Run ID $R. Yes, I approve deleting the 2026-10-30 workout. Tell me in 3 lines what changed in the calendar journal and in Google, and what is still needed." "$WD/a.txt"; SK="--skip-checker";;
    D3) ask cho "$R-cho" "Loop 2 scenario run, run ID $R. Synthetic data. The workout on 2026-10-30 (CHO - Workout - 10302026-0001) should be dropped from the calendar because Alex Test is travelling. Handle this as the CHO, then tell me in 3 lines what you did, who you asked, and what is still needed." "$WD/q.txt"; SK="--skip-checker";;
    C)  ask coo "$R-coo" "Loop 2 scenario run, run ID $R. I am the CEO. Put a bill-payment reminder on the calendar on 2026-10-29, 09:00 to 09:30 (synthetic data: Alex Test electricity bill). Route this to the CFO, which owns finance. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$WD/q.txt"; SK="--skip-checker --cfo";;
    O)  ask coo "$R-coo" "Loop 2 scenario run, run ID $R. I am the CEO. Add a dentist appointment (synthetic: Alex Test) on 2026-10-28, 07:30 to 08:30. Route this to the CHO, which owns health. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$WD/q.txt"
        ask coo "$R-coo" "Run ID $R. Yes, take the 08:00 to 09:00 slot for the dentist appointment on 2026-10-28. Tell me in 3 lines what changed and the event IDs." "$WD/a.txt";;
    P)  ask coo "$R-coo" "Loop 2 scenario run, run ID $R. I am the CEO. Please make the workout on 2026-10-30 (CHO - Workout - 10302026-0001) private. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs." "$WD/q.txt";;
  esac
  # shellcheck disable=SC2086
  "$HOME/loop1/scenario-run.sh" check "$R" $SK >"$WD/check.txt" 2>&1
  glist >"$WD/glist.txt"
  if [ "$S" = C ]; then python3 - "$R" "$WD/cfo.json" <<'P'
import json, sys, os
run, out = sys.argv[1:3]; calls = []
p = os.path.expanduser("~/loop1/evidence/traj/.openclaw/trajectory-exports/%s-cfo/events.jsonl" % run)
try:
    for l in open(p):
        o = json.loads(l); d = o.get("data", {})
        if o.get("type") == "tool.call" and d.get("name") == "sessions_send" and run in json.dumps(d.get("args", {})):
            calls.append(d["args"])
except OSError:
    pass
json.dump(calls, open(out, "w"))
P
  fi
  # cost: export the COO session (explicit) and the chiefs' main sessions before the next prep
  openclaw sessions export-trajectory --session-key "agent:coo:explicit:$R-coo" --workspace "$HOME/loop1/evidence/traj" --output "$R-coo" >/dev/null 2>&1
  [ "$S" = D3 ] && openclaw sessions export-trajectory --session-key "agent:cho:explicit:$R-cho" --workspace "$HOME/loop1/evidence/traj" --output "$R-cho" >/dev/null 2>&1
  for a in cho cos cfo; do [ -e "$EX/$R-$a" ] || openclaw sessions export-trajectory --session-key "agent:$a:main" --workspace "$HOME/loop1/evidence/traj" --output "$R-$a" >/dev/null 2>&1; done
  COST="$(python3 "$HOME/loop1/run-cost.py" "$R" "$T0" 2>&1 | tail -1)"
  CV="$(echo "$COST" | sed -n 's/.*total \([0-9.]*\) USD.*/\1/p')"; CV="${CV:-0}"
  CRIT="$(python3 "$HOME/loop1/reg-criteria.py" "$S" "$R" "$WD" 2>&1)"
  NP="$(echo "$CRIT" | grep -c '^PASS')"; NF="$(echo "$CRIT" | grep -vc '^PASS')"
  RES=PASS; [ "$NF" -gt 0 ] && RES=FAIL
  NB="$(grep -m1 '^numstat:' "$WD/check.txt" | sed 's/numstat: //;s/state.*//' | tr -s '[:space:]' ' ')"; NA="$(grep 'numstat after the job' "$WD/check.txt" | tail -1 | sed 's/.*: //;s/state.*//' | tr -s '[:space:]' ' ')"
  { echo "-- reply of the agent (first message)"; sed -e 's/^/   /' "$WD/q.txt" | tail -n 25 | cut -c1-300
    [ -s "$WD/a.txt" ] && { echo "-- reply (second message)"; sed -e 's/^/   /' "$WD/a.txt" | tail -n 8 | cut -c1-300; }
    echo "-- journal lines for $R (verbatim)"; grep -F "$R" "$W/cos/state/calendar-journal.md"
    echo "-- check output"; grep -E "Result|PASS|FAIL|numstat|done|created|made busy|skip|summary|conflict" "$WD/check.txt" | cut -c1-180
    echo "-- Google after the job"; cut -c1-120 "$WD/glist.txt"
    echo "-- criteria"; echo "$CRIT"
    echo "-- cost: $COST"
    echo "RESULT $R $RES ($NP pass, $NF fail)"
  } >>"$F"
  TOTAL="$(python3 -c "print(round($TOTAL+$CV,4))")"; if [ "$RES" = PASS ]; then PASSN=$((PASSN+1)); else FAILN=$((FAILN+1)); fi
  FL="$(echo "$CRIT" | grep -v '^PASS' | sed 's/^FAIL //' | tr '\n' ';' | cut -c1-200)"
  echo "| $R | ${NAMES[$n]} | $RES | $NP pass, $NF fail${FL:+ (fail: $FL)} | $NB / $NA | $CV |" >> "$SUM.rows"
  echo "$R $RES ($NP pass, $NF fail) cost $CV"
  post "Regression $SUITE, run $R (${NAMES[$n]}): $RES - $NP criteria pass, $NF fail, cost $CV USD"
  PREV="$R"
done
# ---- closing reset to the seed
echo "-- closing reset"; [ -n "$PREV" ] && cleanup_busy "$PREV"
"$HOME/loop1/scenario-run.sh" prep "${SUITE}-99-final" 2>&1 | grep -E "STOP|READY|numstat|other events"
resume_cron
{ echo "# Regression suite $SUITE ($(date '+%F %H:%M') AST)"; echo
  echo "Runs: $RUNS. Pass $PASSN, fail $FAILN. Total cost $TOTAL USD (measured by exporting the COO, CHO, CoS and CFO sessions)."; echo
  echo "| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |"; echo "|---|---|---|---|---|---|"
  tail -n +2 "$SUM.rows"; echo; echo "Per-run files: regression/$SUITE/<run>.txt. Closing reset: ${SUITE}-99-final."; } > "$SUM"
rm -f "$SUM.rows"
post "Regression $SUITE done: $PASSN pass, $FAILN fail, total cost $TOTAL USD. Summary: ~/handover/regression/$SUITE.md"
echo "summary: $SUM"; sed -n 3,3p "$SUM"
