#!/usr/bin/env bash
# loop1-v1104-upgrade.sh - Loop 3 instruction set v1.10.4 (APR-0103, wording approved by the CEO in APR-0104). Run on the VM after v1.10.3 (COO).
# Appends one rule to the COO only: the last item of a delete approval request asks for "approve <event ID>".
# Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1104-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1104-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COO_REPLY='- Delete reply line (APR-0103, instruction set v1.10.4): in every delete approval request, make the last item exactly "Reply: approve <event ID>, explain more, or keep", with the real event ID from the journal entry in place of <event ID>. This replaces the Reply wording of v1.10 for deletes. Add one short sentence after the seven items telling the CEO to type approve and the event ID, for example approve <event ID>, and that a bare approve will not delete. When the CEO writes approve and the event ID, pass it to the CoS with his words quoted and the event ID, as before. If the CEO writes approve without an event ID, do not pass it as an approval: ask once for approve and the event ID. Never write the event ID of a different request.'

a=coo
[ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.10.3' "$W/$a/AGENTS.md" || { echo "coo is not on v1.10.3. Run the v1.10.3 upgrade first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi
if grep -q 'instruction set v1.10.4' "$W/$a/AGENTS.md"; then echo "$a: already v1.10.4, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then
  echo "$a: would append to $W/$a/AGENTS.md:"
  printf '    %s\n' "$COO_REPLY"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
printf '%s\n' "$COO_REPLY" >> "$W/$a/AGENTS.md"
git -C "$W/$a" add AGENTS.md
git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.4 (APR-0103)" -- AGENTS.md
echo "$a: v1.10.4 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
