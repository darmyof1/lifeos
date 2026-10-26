#!/usr/bin/env bash
# loop1-v19-upgrade.sh - Loop 2 instruction set v1.9 (APR-0086). Run on the VM after v1.8 on the CHO and v1.7 on the CoS.
# Appends one privacy rule each to the CHO, the CoS and the CFO:
#   CHO and CFO: every calendar entry they ask the CoS for is high privacy, and they say so in the message.
#   CoS: writes privacy=high in the journal detail column for an entry the chief marked, for any entry of the CHO or the CFO, or when the CEO asked.
# Commits AGENTS.md only in each workspace. Does not touch state/ or any other agent. Safe to run twice: an agent already on v1.9 is skipped.
# Usage: bash deploy/loop1/loop1-v19-upgrade.sh --dry-run     (shows what would be added, changes nothing)
#        bash deploy/loop1/loop1-v19-upgrade.sh               (applies)
# The gateway must be stopped for a real run, as for the earlier upgrade scripts. Start it again afterwards.
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

CHO_RULE='- Privacy (APR-0086, instruction set v1.9): every calendar entry you ask the CoS for is high privacy. Say so in your message to the CoS: write privacy=high next to the run ID and the event ID.'
CFO_RULE='- Privacy (APR-0086, instruction set v1.9): every calendar entry you ask the CoS for is high privacy. Say so in your message to the CoS: write privacy=high next to the run ID and the event ID.'
COS_RULE='- Privacy mark (APR-0086, instruction set v1.9): the journal line is: name | start | end | status | run ID | event ID | requested by | detail. Write privacy=high in the detail column when the chief who asked marks the entry high privacy, when the chief is the CHO or the CFO (health and finance are high by default), or when the CEO asked for the entry to be private. Put the mark on the moved line and on the new line of a move. Never write a lower privacy for an entry that was high. The push job shows a marked entry in Google as busy; do not explain the mark in your reply.'

# Check every agent before changing any.
[ -f "$W/cho/AGENTS.md" ] || { echo "$W/cho/AGENTS.md missing. Stop."; exit 1; }
[ -f "$W/cos/AGENTS.md" ] || { echo "$W/cos/AGENTS.md missing. Stop."; exit 1; }
[ -f "$W/cfo/AGENTS.md" ] || { echo "$W/cfo/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.8' "$W/cho/AGENTS.md" || { echo "cho is not on v1.8. Run the earlier upgrades first. Stop."; exit 1; }
grep -q 'instruction set v1.7' "$W/cos/AGENTS.md" || { echo "cos is not on v1.7. Run the earlier upgrades first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
fi

add() {  # add <agent> <rule>
  local a="$1" rule="$2"
  if grep -q 'instruction set v1.9' "$W/$a/AGENTS.md"; then echo "$a: already v1.9, skipped"; return 0; fi
  if [ "$DRY" = 1 ]; then
    echo "$a: would append to $W/$a/AGENTS.md:"
    printf '    %s\n' "$rule"
    return 0
  fi
  printf '%s\n' "$rule" >> "$W/$a/AGENTS.md"
  git -C "$W/$a" add AGENTS.md
  git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.9 (APR-0086)" -- AGENTS.md
  echo "$a: v1.9 added"
}
add cho "$CHO_RULE"
add cos "$COS_RULE"
add cfo "$CFO_RULE"
if [ "$DRY" = 1 ]; then
  echo "Dry run only. Nothing was changed."
else
  echo "Done. Start the gateway again with slack.env and openai.env sourced."
fi
