#!/usr/bin/env bash
# loop1-v1101-upgrade.sh - Loop 2 instruction set v1.10.1 (APR-0093). Run on the VM after v1.10.
# Appends one rule to the CoS and one to the COO (the CFO is not changed):
#   CoS: always write delete-pending-approval first; delete lines carry the entry's own journal event ID, never a title or an invented ID.
#   COO: when routing a delete, quote the CEO's words and give the journal event ID; never write approving unless his words say so; each approval-request item on its own line.
# Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1101-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1101-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COS_ORDER='- Delete order and event ID (APR-0093, instruction set v1.10.1): for every delete, append the delete-pending-approval line first, even when the message says the CEO approved. Append the deleted line second, and only when the CEO'"'"'s own words, quoted in the message, clearly tell you to delete that entry or later approve it. A deleted line with no delete-pending-approval line before it for the same event ID is wrong. In the event ID column of both lines use the event ID of the entry'"'"'s existing line in the journal (for example seed-3). Never use the title and never make up an ID. If you cannot find the entry, write nothing and say so.'
COO_DELETE='- Delete requests and approval layout (APR-0093, instruction set v1.10.1): when you pass a delete to the CoS, quote the CEO'"'"'s exact words and give the event ID from the journal entry (ask the CoS for it if you do not know it). Never write approving or approved in your message unless the CEO'"'"'s own words say so. When you post an approval request, put each item on its own line, in this order: What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply.'

for a in coo cos; do
  [ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
  grep -q 'instruction set v1.10' "$W/$a/AGENTS.md" || { echo "$a is not on v1.10. Run the v1.10 upgrade first. Stop."; exit 1; }
done
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi

add() {  # add <agent> <rule>
  local a="$1"; shift
  if grep -q 'instruction set v1.10.1' "$W/$a/AGENTS.md"; then echo "$a: already v1.10.1, skipped"; return 0; fi
  if [ "$DRY" = 1 ]; then
    echo "$a: would append to $W/$a/AGENTS.md:"
    printf '    %s\n' "$@"
    return 0
  fi
  printf '%s\n' "$@" >> "$W/$a/AGENTS.md"
  git -C "$W/$a" add AGENTS.md
  git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.1 (APR-0093)" -- AGENTS.md
  echo "$a: v1.10.1 added"
}
add cos "$COS_ORDER"
add coo "$COO_DELETE"
if [ "$DRY" = 1 ]; then
  echo "Dry run only. Nothing was changed."
else
  echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
fi
