#!/usr/bin/env bash
# Live proof of the privacy toggle on the TEST calendar (Loop 5, APR-0119). Fields only: Google event ID, start, title (synthetic).
set -u
PY="$HOME/.local/share/pipx/venvs/gcalcli/bin/python"
CAL="$(sed -n 's/^GCAL_CALENDAR=//p' "$HOME/loop1/gcal-sync/env" | tr -d "\"'")"
LEDGERS="--require-ceo-ledger $HOME/loop1/ceo-ledger/scenario-ledger.jsonl --require-ceo-ledger $HOME/loop1/ceo-ledger/slack-ledger.jsonl"
J="$HOME/loop1/workspaces/cos/state/calendar-journal.md"
glist() { GCAL_CALENDAR="$CAL" "$PY" "$HOME/lifeos-ro/scripts/gcal/gcal_list.py" --from 2026-10-26 --to 2026-11-01 2>/dev/null |
  awk -F'\t' '{ if ($4 ~ /^[A-Z]+ - .+ - [0-9]{8}-[0-9]{4}$/ || $4 == "busy") print "  "$1"\t"$2"\t"$4; else o++ } END { print "  other events: " (o+0) }'; }
step() { echo "=== STEP $1 (mode $2)  $(date +%T)"; LIFEOS_SYNC_ARGS="--privacy-display $2 $LEDGERS" bash "$HOME/work25/scripts/gcal/gcal_sync_cron.sh" >/dev/null; tail -n 4 "$HOME/loop1/gcal-sync/sync.log" | cut -c1-170; echo "  journal lines: $(grep -c . "$J")   numstat: $(git -C "$HOME/loop1/workspaces/cos" diff --numstat state/calendar-journal.md)"; glist; }
echo "--- before"; glist
step 1 busy
step 2 full
step 2b full
step 3 busy
step 3b busy
