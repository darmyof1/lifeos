#!/usr/bin/env bash
# backup-run.sh - the cron entry point (Loop 4, APR-0117): backup-weekly.sh, then backup-push.sh, one log line per run.
#   backup-run.sh              dry run of both steps, no log line
#   backup-run.sh --execute    runs both; writes one line to ~/loop1/backups/run.log (time, archive, bytes, push result; nothing secret)
# Exit status is non-zero if any step failed. Calls the scripts that sit next to it.
set -uo pipefail
EXEC=0
case "${1:-}" in "") ;; --execute) EXEC=1 ;; -h|--help) sed -n 2,6p "$0"; exit 0 ;; *) echo "Usage: $0 [--execute]"; exit 2 ;; esac
export PATH="/usr/local/bin:/usr/bin:/bin:${PATH:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HOME/loop1/backups"; LOG="$OUT/run.log"
if [ "$EXEC" = 0 ]; then
  bash "$HERE/backup-weekly.sh" || exit 1
  bash "$HERE/backup-push.sh" || exit 1
  exit 0
fi
( umask 077; mkdir -p "$OUT" ) || exit 1
chmod 700 "$OUT"
logline() { printf '%s %s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$*" >> "$LOG"; chmod 600 "$LOG"; }
if ! B="$(bash "$HERE/backup-weekly.sh" --execute 2>&1)"; then
  logline "backup=FAILED push=not-run"; echo "$B" | tail -3; exit 1
fi
echo "$B" | tail -2
NEWEST="$(ls -1t "$OUT"/lifeos-backup-*.tar.gpg 2>/dev/null | head -1)"; NAME="$(basename "${NEWEST:-none}")"
BYTES="$(wc -c < "$NEWEST" 2>/dev/null | tr -d ' ')"
if P="$(bash "$HERE/backup-push.sh" --execute 2>&1)"; then
  echo "$P" | tail -2; logline "archive=$NAME bytes=${BYTES:-0} push=ok"; exit 0
fi
echo "$P" | tail -3; logline "archive=$NAME bytes=${BYTES:-0} push=FAILED"; exit 1
