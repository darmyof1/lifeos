#!/usr/bin/env bash
# loop1-v1103-upgrade.sh - Loop 2 instruction set v1.10.3 (APR-0095). Run on the VM after v1.10.1 (COO).
# Appends one rule to the COO only: a pending delete is always answered with the seven items, one per line.
# Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1103-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1103-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COO_SEVEN='- Delete approval layout (APR-0095, instruction set v1.10.3): when the CoS reports a delete-pending-approval line, always post the seven items, each on its own line: What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply. A plain sentence is not enough. Never answer a delete question in prose only.'

a=coo
[ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.10.1' "$W/$a/AGENTS.md" || { echo "coo is not on v1.10.1. Run the v1.10.1 upgrade first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi
if grep -q 'instruction set v1.10.3' "$W/$a/AGENTS.md"; then echo "$a: already v1.10.3, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then
  echo "$a: would append to $W/$a/AGENTS.md:"
  printf '    %s\n' "$COO_SEVEN"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
printf '%s\n' "$COO_SEVEN" >> "$W/$a/AGENTS.md"
git -C "$W/$a" add AGENTS.md
git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.3 (APR-0095)" -- AGENTS.md
echo "$a: v1.10.3 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
