#!/usr/bin/env bash
# kill-switch.sh - stop LifeOS fast and put it back exactly (APR-0112). Run on the VM as the owner (ubuntu).
#   kill-switch.sh                 dry run: prints what --execute would do, changes nothing
#   kill-switch.sh --execute       stops the gateway service and pauses the calendar cron line; writes the marker
#   kill-switch.sh --restore       dry run of the restore
#   kill-switch.sh --restore --execute   starts the gateway again and un-pauses the calendar cron line
# It never deletes anything, never touches the stress-ng line or any other crontab line, never prints secrets.
# The marker is ~/loop1/kill-switch.marker (mode 600); the crontab before the pause is kept in ~/loop1/kill-switch-crontab.<time> (mode 600).
set -uo pipefail
SERVICE="${KS_SERVICE:-openclaw-loop1-gateway}"
DIR="$HOME/loop1"
MARKER="$DIR/kill-switch.marker"
RESTORE=0; EXEC=0
for a in "$@"; do
  case "$a" in
    --execute) EXEC=1 ;;
    --restore) RESTORE=1 ;;
    -h|--help) sed -n 2,8p "$0"; exit 0 ;;
    *) echo "Unknown option: $a"; sed -n 2,8p "$0"; exit 2 ;;
  esac
done
say() { echo "$*"; }
act() { if [ "$EXEC" = 1 ]; then "$@"; else say "[dry run] would run: $*"; fi; }
# the calendar job line: active (starts with */5) or paused (#*/5), and it runs gcal_sync_cron.sh
active_line_count() { crontab -l 2>/dev/null | grep -c '^\*/5 .*gcal_sync_cron\.sh'; }
paused_line_count() { crontab -l 2>/dev/null | grep -c '^#\*/5 .*gcal_sync_cron\.sh'; }
pause_cron()  { crontab -l | sed 's|^\*/5 \(.*gcal_sync_cron\.sh\)|#*/5 \1|' | crontab -; }
resume_cron() { crontab -l | sed 's|^#\*/5 \(.*gcal_sync_cron\.sh\)|*/5 \1|' | crontab -; }
gateway_active() { [ "$(systemctl --user is-active "$SERVICE" 2>/dev/null)" = "active" ]; }

if [ "$RESTORE" = 0 ]; then
  say "KILL SWITCH ($([ "$EXEC" = 1 ] && echo EXECUTE || echo dry run))"
  if [ -e "$MARKER" ]; then say "The marker $MARKER exists: the kill switch is already engaged. Use --restore. Nothing done."; exit 1; fi
  A="$(active_line_count)"; P="$(paused_line_count)"
  if [ "$A" -gt 1 ] || [ "$P" -gt 1 ] || { [ "$A" -ge 1 ] && [ "$P" -ge 1 ]; }; then say "STOP: the calendar cron line is not unique (active $A, paused $P). Nothing done."; exit 1; fi
  if [ "$A" = 0 ] && [ "$P" = 0 ]; then say "STOP: no calendar cron line (gcal_sync_cron.sh) found. Nothing done."; exit 1; fi
  GW=0; gateway_active && GW=1
  say "gateway service $SERVICE: $([ "$GW" = 1 ] && echo active || echo not active)"
  say "calendar cron line: $([ "$A" = 1 ] && echo active || echo already paused)"
  if [ "$EXEC" = 1 ]; then
    mkdir -p "$DIR" || exit 1
    TS="$(date +%Y%m%d-%H%M%S)"; BK="$DIR/kill-switch-crontab.$TS"
    ( umask 077; crontab -l > "$BK" ) || { say "STOP: could not save the crontab. Nothing done."; exit 1; }
    ( umask 077; { echo "time=$(date -Is)"; echo "gateway_was_active=$GW"; echo "cron_was_active=$A"; echo "crontab_backup=$BK"; } > "$MARKER" )
    chmod 600 "$MARKER" "$BK"
  fi
  # order: pause the cron first (so no push runs while stopping), then stop the gateway
  if [ "$A" = 1 ]; then act pause_cron; fi
  if [ "$GW" = 1 ]; then act systemctl --user stop "$SERVICE"; fi
  if [ "$EXEC" = 1 ]; then
    [ "$A" = 1 ] && { [ "$(active_line_count)" = 0 ] && say "check: calendar cron line paused" || say "WARNING: calendar cron line still active"; }
    [ "$GW" = 1 ] && { gateway_active && say "WARNING: gateway still active" || say "check: gateway stopped"; }
    say "Marker written: $MARKER"
    say "To restore: bash $0 --restore --execute"
  else
    say "[dry run] would write $MARKER and a crontab copy in $DIR"
    say "Run with --execute to act."
  fi
  exit 0
fi

# restore
say "KILL SWITCH RESTORE ($([ "$EXEC" = 1 ] && echo EXECUTE || echo dry run))"
if [ ! -r "$MARKER" ]; then say "No marker $MARKER: nothing to restore. Nothing done."; exit 1; fi
GW="$(sed -n 's/^gateway_was_active=//p' "$MARKER")"; CA="$(sed -n 's/^cron_was_active=//p' "$MARKER")"; BK="$(sed -n 's/^crontab_backup=//p' "$MARKER")"
say "marker: gateway_was_active=$GW cron_was_active=$CA"
if [ "$CA" = 1 ]; then
  [ "$(paused_line_count)" = 1 ] || { say "STOP: expected exactly one paused calendar cron line, found $(paused_line_count). Nothing done."; exit 1; }
  act resume_cron
fi
if [ "$GW" = 1 ]; then act systemctl --user start "$SERVICE"; fi
if [ "$EXEC" = 1 ]; then
  if [ "$CA" = 1 ] && [ -r "$BK" ]; then
    if crontab -l | cmp -s - "$BK"; then say "check: crontab identical to the copy taken at the kill"; else say "WARNING: crontab differs from the copy $BK (edited meanwhile?)"; fi
  fi
  [ "$GW" = 1 ] && { sleep 5; gateway_active && say "check: gateway active" || say "WARNING: gateway not active"; }
  rm -f "$MARKER"
  say "Marker removed. The crontab copy stays: $BK"
else
  say "[dry run] would remove the marker. Run with --restore --execute to act."
fi
exit 0
