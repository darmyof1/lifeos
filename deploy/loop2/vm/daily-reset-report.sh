#!/usr/bin/env bash
# 05:00 AST cron wrapper for daily-reset-report.py. Loads the same env as gcal_sync_cron.sh (state dir, alert target).
set -a; . "$HOME/loop1/env.sh"; [ -f "$HOME/loop1/gcal-sync/env" ] && . "$HOME/loop1/gcal-sync/env"; set +a
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"
exec python3 "$HOME/loop1/daily-reset-report.py" "$@"
