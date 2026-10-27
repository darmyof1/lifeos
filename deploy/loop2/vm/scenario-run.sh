#!/usr/bin/env bash
# scenario-run.sh - one-command prep and checks for a Loop 2 scenario run (replaces the long batches of runs 005 to 012).
# Install: ~/loop1/scenario-run.sh. Run from any directory, as ubuntu, in any terminal (T2).
#
#   scenario-run.sh prep  <RUN> [--leftover-id ID --leftover-key KEY | --leftover-title TITLE] [--dry-run]
#   scenario-run.sh check <RUN> [--skip-checker] [--cfo] [--dry-run]
#
# prep : needs exactly one gateway process; pauses the calendar cron; deletes the named leftover Google event
#        (approval note "CEO handover 3, 2026-10-26"); saves cho/cos/cfo state to ~/loop1/evidence/<date>/<RUN>-<agent>;
#        git checkout -- state/; compacts the cho, cos, cfo and coo main sessions and READS every output (any error means
#        STOP: the cron stays paused, wait and retry); pushes the seed lines by hand; lists Google.
# check: numstat, the run's journal lines, health plan tail, trajectory exports (cho, cos, plus cfo with --cfo), the
#        sessions_send checker; only if it passes: runs the job by hand, lists Google, numstat again, resumes the cron.
#        --skip-checker is for runs without a CHO handoff (the job then runs after your own review of the journal).
#        A failed checker leaves the cron paused and says so.
# The cron state is printed at the end every time (also when interrupted). Secrets are never printed.
set -uo pipefail
MODE="${1:-}"; RUN="${2:-}"
[ -n "$MODE" ] && [ -n "$RUN" ] || { sed -n 2,17p "$0"; exit 2; }
shift 2
DRY=0; SKIP=0; CFO=0; LID=""; LKEY=""; LTITLE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1;; --skip-checker) SKIP=1;; --cfo) CFO=1;;
    --leftover-id) LID="$2"; shift;; --leftover-key) LKEY="$2"; shift;; --leftover-title) LTITLE="$2"; shift;;
    *) echo "unknown option $1"; exit 2;;
  esac; shift
done
# shellcheck disable=SC1091
. "$HOME/loop1/env.sh"
REPO="$HOME/lifeos-ro"; W="$HOME/loop1/workspaces"; E="$HOME/loop1/evidence/$(date +%F)"
PY="$HOME/.local/share/pipx/venvs/gcalcli/bin/python"
CAL="$(sed -n 's/^GCAL_CALENDAR=//p' "$HOME/loop1/gcal-sync/env" | tr -d "\"'")"
NOTE="CEO handover 4, 2026-10-26"
cron_state() {
  local l; l="$(crontab -l 2>/dev/null | grep gcal_sync_cron.sh | head -1)"
  case "$l" in '*/5'*) echo "CRON: ACTIVE (*/5)";; '#'*) echo "CRON: PAUSED (line starts with #)";; *) echo "CRON: LINE MISSING";; esac
  crontab -l 2>/dev/null | grep -q stress-ng && echo "CRON: stress-ng line kept"
}
pause_cron()  { crontab -l | sed 's|^\*/5 .*gcal_sync_cron.sh|#&|' | crontab -; }
resume_cron() { crontab -l | sed 's|^#\(\*/5 .*gcal_sync_cron.sh\)|\1|' | crontab -; }
trap 'echo; echo "--- end ($MODE $RUN, exit status $?)"; cron_state' EXIT
trap 'echo "INTERRUPTED"; exit 130' INT TERM
run() { if [ "$DRY" = 1 ]; then echo "[dry-run] ${*//$CAL/<test-calendar>}"; else "$@"; fi; }
glist() {  # LifeOS titles and busy events in full, other events as a count only
  GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_list.py" --from "${1:-2026-10-26}" --to "${2:-2026-11-01}" 2>/dev/null |
    awk -F'\t' '{ if ($4 ~ /^[A-Z]+ - .+ - [0-9]{8}-[0-9]{4}$/ || $4 == "busy") print $1"\t"$2"\t"$4; else o++ } END { print "other events: " (o+0) }'
}
nstat() { git -C "$W/cos" diff --numstat state/calendar-journal.md; }

if [ "$MODE" = prep ]; then
  N="$(pgrep -af 'openclaw.*gateway' | grep -E ' gateway run|openclaw-gateway| gateway --port' | grep -v -e pgrep -e grep -e 'bash -c' | wc -l)"
  [ "$N" = 1 ] || { echo "STOP: gateway processes: $N (need exactly 1). Cron untouched."; exit 1; }
  systemctl --user is-active openclaw-loop1-gateway >/dev/null || { echo "STOP: gateway service not active. Cron untouched."; exit 1; }
  echo "prep $RUN: gateway ok (1 process)"
  [ "$DRY" = 1 ] && echo "[dry-run] would pause cron" || { pause_cron; crontab -l | grep gcal_sync_cron | grep -q '^#' || { echo "STOP: cron not paused"; exit 1; }; }
  if [ -n "$LID" ] && [ -n "$LKEY" ]; then
    run env GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_delete.py" --id "$LID" --busy-key "$LKEY" --ceo-approved --approval-note "$NOTE" || { echo "STOP: leftover delete failed; cron stays paused"; exit 1; }
  elif [ -n "$LID" ] && [ -n "$LTITLE" ]; then
    run env GCAL_CALENDAR="$CAL" "$PY" "$REPO/scripts/gcal/gcal_delete.py" --id "$LID" --title "$LTITLE" --ceo-approved --approval-note "$NOTE" || { echo "STOP: leftover delete failed; cron stays paused"; exit 1; }
  else echo "no leftover given (none deleted)"; fi
  if [ "$DRY" = 1 ]; then echo "[dry-run] would save state to $E/$RUN-<agent>, git checkout -- state/ for cho cos cfo, compact 4 sessions, push the seed, list Google"; exit 0; fi
  mkdir -p "$E"
  for a in cho cos cfo; do
    [ -e "$E/$RUN-$a" ] && { echo "STOP: $E/$RUN-$a exists (run ID reused?). Cron stays paused."; exit 1; }
    cp -r "$W/$a/state" "$E/$RUN-$a" && git -C "$W/$a" checkout -- state/ || { echo "STOP: state reset failed for $a"; exit 1; }
  done
  T="$(cat "$HOME/loop1/gateway-token")"
  for a in coo cho cos cfo; do
    OUT="$(openclaw sessions compact "agent:$a:main" --agent "$a" --max-lines 1 --token "$T" 2>&1)"; RC=$?
    echo "compact $a: $(echo "$OUT" | grep -iE 'compact|error|fail|check the' | head -2 | tr '\n' ' ' | cut -c1-160)"
    if [ $RC -ne 0 ] || echo "$OUT" | grep -qiE 'error|fail|check the control ui|unable|cannot|not reachable'; then
      echo "STOP: compact output for $a looks like an error. Wait 30 s (is the gateway ready?), then run prep again with a NEW run ID. Cron stays paused."; exit 1
    fi
    echo "$OUT" | grep -qE 'Compacted session|No compaction needed' || { echo "STOP: unexpected compact output for $a. Cron stays paused."; exit 1; }
  done
  bash "$REPO/scripts/gcal/gcal_sync_cron.sh" >/dev/null; tail -n 2 "$HOME/loop1/gcal-sync/sync.log" | cut -c1-160
  glist; echo "numstat after seed (expect 3 0): $(nstat)"
  echo "READY: post/run scenario $RUN now, then: scenario-run.sh check $RUN"
  exit 0
fi

if [ "$MODE" = check ]; then
  echo "numstat: $(nstat)"; nstat | awk '{ if ($2 != 0) print "WARNING: deleted lines in the journal" }'
  echo "--- journal lines for $RUN"; grep "$RUN" "$W/cos/state/calendar-journal.md" | cut -c1-210
  echo "--- health plan tail"; tail -n 4 "$W/cho/state/health-plan.md" | cut -c1-200
  EX="$HOME/loop1/evidence/traj/.openclaw/trajectory-exports"
  if [ "$DRY" = 1 ]; then echo "[dry-run] would export trajectories, run the checker, run the job, list, resume cron"; exit 0; fi
  AG="cho cos"; [ "$CFO" = 1 ] && AG="cho cos cfo"
  for a in $AG; do [ -e "$EX/$RUN-$a" ] || openclaw sessions export-trajectory --session-key "agent:$a:main" --workspace "$HOME/loop1/evidence/traj" --output "$RUN-$a" >/dev/null 2>&1; done
  OK=1
  if [ "$SKIP" = 0 ]; then
    python3 "$REPO/scripts/verify/check_sessions_send.py" "$EX" "$RUN" 2>&1 | grep -E '^(PASS|FAIL|WARN|Result)' | cut -c1-150
    python3 "$REPO/scripts/verify/check_sessions_send.py" "$EX" "$RUN" >/dev/null 2>&1 || OK=0
  else echo "checker skipped (--skip-checker)"; fi
  if [ "$OK" = 0 ]; then echo "CHECKER FAILED: job not run, cron stays PAUSED. Fix or reset, then resume by hand."; exit 1; fi
  bash "$REPO/scripts/gcal/gcal_sync_cron.sh" >/dev/null; tail -n 4 "$HOME/loop1/gcal-sync/sync.log" | cut -c1-170
  glist
  echo "numstat after the job: $(nstat)"
  resume_cron; exit 0
fi
echo "unknown mode $MODE"; exit 2
