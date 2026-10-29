#!/usr/bin/env bash
# loop1-v1106-upgrade.sh - Loop 3 instruction set v1.10.6 (APR-0106, wording approved by the CEO). Run on the VM after v1.10.5 (COO).
# Appends one rule to the COO only: only an order to delete goes to the CoS at once; a question always gets the pending line and the seven items first.
# Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1106-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1106-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COO_REPLY='- Orders and questions (APR-0106, instruction set v1.10.6): pass the CEO'\''s words to the CoS at once, with no approval request, only when they order the delete, for example "Delete the workout on 2026-10-30". A question or a wish, for example "Can you remove the workout?" or "Should we drop the workout?", is not an order. It always gets the delete-pending-approval line from the CoS and then the seven items, each on its own line, and you wait for "approve <event ID>". Never tell the CEO an entry is deleted or recorded as deleted after a question.'

a=coo
[ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.10.5' "$W/$a/AGENTS.md" || { echo "coo is not on v1.10.5. Run the v1.10.5 upgrade first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi
if grep -q 'instruction set v1.10.6' "$W/$a/AGENTS.md"; then echo "$a: already v1.10.6, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then
  echo "$a: would append to $W/$a/AGENTS.md:"
  printf '    %s\n' "$COO_REPLY"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
printf '%s\n' "$COO_REPLY" >> "$W/$a/AGENTS.md"
git -C "$W/$a" add AGENTS.md
git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.6 (APR-0106)" -- AGENTS.md
echo "$a: v1.10.6 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
