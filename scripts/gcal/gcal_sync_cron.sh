#!/usr/bin/env bash
# Cron wrapper for scripts/gcal/gcal_sync.py (P-28, APR-0078). Plain cron under ubuntu, every 5 minutes.
# It runs the push job with the gcalcli Python, writes one timestamped block per run to sync.log, and trims the log.
# It loads ~/loop1/env.sh first. Alerts reach Slack only while the gateway is running; otherwise they are written to alerts.log only.
# Settings come from the file ~/loop1/gcal-sync/env (you create it, mode 600, never committed):
#   GCAL_CALENDAR=<calendar id>            LIFEOS_ALERT_TARGET=channel:<COO channel ID>
#   LIFEOS_ALERT_ACCOUNT=<slack account>   (optional, default: default)
#   PATH=...                               (optional, only if cron cannot find openclaw)
#   GCAL_ALLOW_DELETES=1                   (optional, APR-0092: approved deletes reach Google. Set it only after the
#                                          delete gate passes. The job still deletes only a LifeOS event with a
#                                          delete-pending-approval line and a deleted line with the same event ID.)
# Options for tests: LIFEOS_SYNC_STATE (state folder), LIFEOS_SYNC_PY (Python to use), LIFEOS_SYNC_ARGS (extra options).
# Exit code is the job's: 0 done, 3 paused (login revoked), 4 could not start.
set -u
STATE="${LIFEOS_SYNC_STATE:-$HOME/loop1/gcal-sync}"
mkdir -p "$STATE"
# The alert goes through the OpenClaw gateway (terminal T1), so the OpenClaw environment is needed, as in every other shell.
if [ -f "$HOME/loop1/env.sh" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$HOME/loop1/env.sh"
  set +a
fi
if [ -f "$STATE/env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$STATE/env"
  set +a
fi
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:$PATH"
PY="${LIFEOS_SYNC_PY:-$HOME/.local/share/pipx/venvs/gcalcli/bin/python}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$STATE/sync.log"
OUT="$(mktemp)"
trap 'rm -f "$OUT"' EXIT
ALLOW=""
if [ "${GCAL_ALLOW_DELETES:-0}" = "1" ]; then
  ALLOW="--allow-deletes"
fi
# shellcheck disable=SC2086
"$PY" "$HERE/gcal_sync.py" --state-dir "$STATE" $ALLOW ${LIFEOS_SYNC_ARGS:-} >"$OUT" 2>&1
CODE=$?
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') exit $CODE"
  cat "$OUT"
} >>"$LOG"
if [ "$(wc -l <"$LOG")" -gt 2000 ]; then
  tail -n 1500 "$LOG" >"$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
exit "$CODE"
