#!/usr/bin/env bash
# loop1-v18-upgrade.sh - Loop 1/2 instruction set v1.8 (APR-0081). Run on the VM after v1.7 on the CHO.
# Appends one CHO rule: a health fact reported in a message is logged in state/health-plan.md with its own event ID.
# Commits cho/AGENTS.md only. Does not touch state/ or any other agent. Safe to run twice: an agent already on v1.8 is skipped.
# Usage: bash deploy/loop1/loop1-v18-upgrade.sh --dry-run     (shows what would be added, changes nothing)
#        bash deploy/loop1/loop1-v18-upgrade.sh               (applies)
# The gateway must be stopped for a real run, as for the earlier upgrade scripts. Start it again afterwards.
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

CHO_RULE='- Health facts (APR-0081, instruction set v1.8): when a message reports a health fact (sleep, weight, a symptom), append a line to state/health-plan.md with the run ID and its own event ID, even if the message also asks for something else.'

a=cho
[ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.7' "$W/$a/AGENTS.md" || { echo "$a is not on v1.7. Run the earlier upgrades first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
fi

if grep -q 'instruction set v1.8' "$W/$a/AGENTS.md"; then
  echo "$a: already v1.8, skipped"
elif [ "$DRY" = 1 ]; then
  echo "$a: would append to $W/$a/AGENTS.md:"
  printf '    %s\n' "$CHO_RULE"
else
  printf '%s\n' "$CHO_RULE" >> "$W/$a/AGENTS.md"
  git -C "$W/$a" add AGENTS.md
  git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.8 (APR-0081)" -- AGENTS.md
  echo "$a: v1.8 added"
fi
if [ "$DRY" = 1 ]; then
  echo "Dry run only. Nothing was changed."
else
  echo "Done. Start the gateway again with slack.env and openai.env sourced."
fi
