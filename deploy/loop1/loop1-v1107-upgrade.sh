#!/usr/bin/env bash
# loop1-v1107-upgrade.sh - Loop 3 instruction set v1.10.7 (APR-0110, wording approved by the CEO). Run on the VM after v1.10.6 (COO).
# Appends one rule to the COO only: a plain approve (no event ID) is passed to the CoS when exactly one delete request is waiting; the gate (APR-0110) decides.
# Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1107-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1107-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COO_REPLY='- Plain approve (APR-0110, instruction set v1.10.7): this replaces the v1.10.4 rule about an approve without an event ID. The last item of every delete approval request stays exactly "Reply: approve <event ID>, explain more, or keep". The short sentence after the seven items now says: type approve and the event ID, or just approve if this is the only request waiting. If the CEO writes approve without an event ID and exactly one delete request of his is waiting, pass it to the CoS with his words quoted and that request'\''s event ID. If more than one is waiting, or you are not sure which one he means, do not pass it: ask once for approve and the event ID. Never write the event ID of a different request.'

a=coo
[ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.10.6' "$W/$a/AGENTS.md" || { echo "coo is not on v1.10.6. Run the v1.10.6 upgrade first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi
if grep -q 'instruction set v1.10.7' "$W/$a/AGENTS.md"; then echo "$a: already v1.10.7, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then
  echo "$a: would append to $W/$a/AGENTS.md:"
  printf '    %s\n' "$COO_REPLY"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
printf '%s\n' "$COO_REPLY" >> "$W/$a/AGENTS.md"
git -C "$W/$a" add AGENTS.md
git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.7 (APR-0110)" -- AGENTS.md
echo "$a: v1.10.7 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
