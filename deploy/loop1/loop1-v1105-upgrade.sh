#!/usr/bin/env bash
# loop1-v1105-upgrade.sh - Loop 3 instruction set v1.10.5 (APR-0105, wording approved by the CEO). Run on the VM after v1.10.4 (COO).
# Appends one rule to the COO only: the journal event ID (never the title) in the Reply line; ask only after the CoS wrote the pending line; an explicit CEO delete order goes to the CoS at once.
# Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1105-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1105-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COO_REPLY='- Delete request IDs and order (APR-0105, instruction set v1.10.5): the event ID in the Reply line is the journal event ID the CoS reported (for example seed-3), never the entry'\''s title or date. Post a delete approval request only after the CoS has written the delete-pending-approval line and told you the event ID. If the CEO'\''s own words already clearly tell you to delete the named entry, pass them to the CoS at once, as before, and do not ask for approval again.'

a=coo
[ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.10.4' "$W/$a/AGENTS.md" || { echo "coo is not on v1.10.4. Run the v1.10.4 upgrade first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi
if grep -q 'instruction set v1.10.5' "$W/$a/AGENTS.md"; then echo "$a: already v1.10.5, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then
  echo "$a: would append to $W/$a/AGENTS.md:"
  printf '    %s\n' "$COO_REPLY"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
printf '%s\n' "$COO_REPLY" >> "$W/$a/AGENTS.md"
git -C "$W/$a" add AGENTS.md
git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.5 (APR-0105)" -- AGENTS.md
echo "$a: v1.10.5 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
