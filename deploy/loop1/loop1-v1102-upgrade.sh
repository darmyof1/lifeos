#!/usr/bin/env bash
# loop1-v1102-upgrade.sh - Loop 2 instruction set v1.10.2 (APR-0094). Run on the VM after v1.10.1.
# Appends one rule to the CoS only: delete lines carry no privacy mark and no detail.
# Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1102-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1102-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COS_PLAIN='- Delete lines are plain (APR-0094, instruction set v1.10.2): on a delete-pending-approval line and on a deleted line copy only the run ID, the event ID and requested by. Leave the detail column empty: do not add privacy=high or any other detail, even when the entry or the requester is a CHO or CFO matter. A privacy mark on a delete line makes the push job treat the entry as a busy event and refuse the delete.'

a=cos
[ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.10.1' "$W/$a/AGENTS.md" || { echo "$a is not on v1.10.1. Run the v1.10.1 upgrade first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi
if grep -q 'instruction set v1.10.2' "$W/$a/AGENTS.md"; then echo "$a: already v1.10.2, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then
  echo "$a: would append to $W/$a/AGENTS.md:"
  printf '    %s\n' "$COS_PLAIN"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
printf '%s\n' "$COS_PLAIN" >> "$W/$a/AGENTS.md"
git -C "$W/$a" add AGENTS.md
git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.2 (APR-0094)" -- AGENTS.md
echo "$a: v1.10.2 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
