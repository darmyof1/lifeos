#!/usr/bin/env bash
# loop1-v191-upgrade.sh - Loop 2 instruction set v1.9.1 (fix for the run loop2-scn-009 journal edit). Run on the VM after v1.9.
# Appends one rule to the CoS: never edit the journal header or any existing line, only append lines.
# Commits AGENTS.md only in the CoS workspace. Does not touch state/ or any other agent. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v191-upgrade.sh --dry-run   (shows the rule, changes nothing)
#        bash deploy/loop1/loop1-v191-upgrade.sh              (applies; the gateway must be stopped)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"
RULE='- Journal append only (instruction set v1.9.1): the header line "name | start | end | status | run ID | event ID | requested by" stays exactly as it is. The detail column is not added to it. Never edit, replace or delete an existing journal line, including the header. Only add new lines at the end of the file, and put privacy=high in the detail column of those new lines.'
[ -f "$W/cos/AGENTS.md" ] || { echo "$W/cos/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.9' "$W/cos/AGENTS.md" || { echo "cos is not on v1.9. Stop."; exit 1; }
if grep -q 'instruction set v1.9.1' "$W/cos/AGENTS.md"; then echo "cos: already v1.9.1, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then printf 'cos: would append:\n    %s\nDry run only.\n' "$RULE"; exit 0; fi
pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
printf '%s\n' "$RULE" >> "$W/cos/AGENTS.md"
git -C "$W/cos" add AGENTS.md
git -C "$W/cos" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.9.1 (journal append only)" -- AGENTS.md
echo "cos: v1.9.1 added. Start the gateway again with slack.env and openai.env sourced."
