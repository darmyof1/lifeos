#!/usr/bin/env bash
# comparison-driver.sh - the counted structure comparison (APR-0099, handover 10), alternating variants: four-agent suite, then two rounds of solo runs, three times.
# Resumable: state in ~/handover/structure-test/comparison/driver.state (next step number and the solo run counter). Never reuses a run ID.
# Stops cleanly (and says where) when a step could not finish before 02:30 AST. Steps: 1 suite cmp-001, 2 solo r1, 3 solo r2, 4 suite cmp-002, 5 solo r3, 6 solo r4, 7 suite cmp-003, 8 solo r5, 9 solo r6.
set -uo pipefail
. "$HOME/loop1/env.sh"; export TZ=America/Santo_Domingo
CMP="$HOME/handover/structure-test/comparison"; mkdir -p "$CMP"; ST="$CMP/driver.state"; LOG="$CMP/driver.log"
[ -f "$ST" ] || echo "STEP=1 SOLO_N=3 LAST=loop3-cmp-s-002 RDONE_BS=1" > "$ST"
# shellcheck disable=SC1090
. "$ST"
SCNS=(bad-sleep d1 d2 d3 cfo overlap privacy)
mins() { echo $(( 10#$(date +%H) * 60 + 10#$(date +%M) )); }
fits() { local need="$1" now; now=$(mins); [ $((now + need)) -lt 150 ] || [ "$now" -ge 310 ]; }   # finish before 02:30 (150), or already past 05:10
save() { echo "STEP=$STEP SOLO_N=$SOLO_N LAST=$LAST RDONE_BS=$RDONE_BS" > "$ST"; }
say() { echo "$(date '+%H:%M') $*" | tee -a "$LOG"; }
solo_round() {  # solo_round R  (round number 1..6)
  for sc in "${SCNS[@]}"; do
    if [ "$1" = 1 ] && [ "$sc" = bad-sleep ]; then continue; fi   # loop3-cmp-s-002 already is round 1 bad-sleep
    [ -e "$CMP/.done-r$1-$sc" ] && continue                         # resume: this round and scenario already ran
    fits 5 || { say "STOP: no time for another solo run (02:30 limit); next step stays $STEP"; return 1; }
    local id; id="$(printf 'loop3-cmp-s-%03d' "$SOLO_N")"
    "$HOME/loop1/h4-post.sh" "Comparison $id (solo, $sc) started" >/dev/null
    res="$("$HOME/loop1/solo-run.sh" one "$id" "$sc" "$LAST" 2>&1 | tail -1)"; say "$res"
    "$HOME/loop1/h4-post.sh" "Comparison $res" >/dev/null
    LAST="$id"; SOLO_N=$((SOLO_N + 1)); touch "$CMP/.done-r$1-$sc"; save
  done; return 0; }
solo_end() {  # leave Google at the three seed events and the solo state at its seed
  "$HOME/loop1/solo-run.sh" prep "loop3-cmp-solo-reset-$(date +%H%M)" --leftover "$LAST" 2>&1 | grep -E "STOP|numstat" | tee -a "$LOG"; }
suite_step() {
  fits 40 || { say "STOP: no time for a full suite (02:30 limit); next step stays $STEP"; return 1; }
  REG_OUTD="$CMP" "$HOME/loop1/regression-suite.sh" "$1" 2>&1 | tail -4 | tee -a "$LOG"; }
while [ "$STEP" -le 9 ]; do
  case "$STEP" in
    1) suite_step loop3-cmp-001 || break;;
    4) suite_step loop3-cmp-002 || break;;
    7) suite_step loop3-cmp-003 || break;;
    2) solo_round 1 || { solo_end; break; }; ;;
    3) solo_round 2 || { solo_end; break; }; solo_end;;
    5) solo_round 3 || { solo_end; break; };;
    6) solo_round 4 || { solo_end; break; }; solo_end;;
    8) solo_round 5 || { solo_end; break; };;
    9) solo_round 6 || { solo_end; break; }; solo_end;;
  esac
  STEP=$((STEP + 1)); save
done
say "driver ended at step $STEP (9 = last step done = 10)"
