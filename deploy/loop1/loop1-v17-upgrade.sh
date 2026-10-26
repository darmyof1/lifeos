#!/usr/bin/env bash
# loop1-v17-upgrade.sh - Loop 1/2 instruction set v1.7 (APR-0075). Run on the VM after v1.4 on the CHO and the CoS.
# Appends one CHO rule (the exact sessions_send call to the CoS) and one CoS rule (reply by answering; never sessions_send to the CHO).
# Commits cho/AGENTS.md and cos/AGENTS.md only. Does not touch state/. Safe to run twice: an agent already on v1.7 is skipped.
# Usage: bash deploy/loop1/loop1-v17-upgrade.sh --dry-run     (shows what would be added, changes nothing)
#        bash deploy/loop1/loop1-v17-upgrade.sh               (applies)
# The gateway must be stopped for a real run, as for the earlier upgrade scripts. Start it again afterwards.
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

CHO_RULE='- Handoff call (APR-0075, instruction set v1.7): to ask the CoS for a calendar change, call sessions_send with exactly these fields: sessionKey agent:cos:main, message (the whole task: what to do, dates and times, run ID, event ID), mode followup, timeoutSeconds 120. Never set watch. Never use mode notify or resume. Do not look up the tool'"'"'s API files or list sessions first. The returned reply is the result. If a call fails or returns queued, resend the same message once with the same fields.'
COS_RULE='- Reply by answering (APR-0075, instruction set v1.7): when the CHO'"'"'s message asks for a calendar change, your answer to that message is the report to the CHO, with the run ID, the event ID and the two journal lines. Never call sessions_send to the CHO. If a send returns sentBeforeError true, it was delivered: do not send again.'

# Check both agents before changing either.
for a in cho cos; do
  [ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
  grep -q 'instruction set v1.4' "$W/$a/AGENTS.md" || { echo "$a is not on v1.4. Run the earlier upgrades first. Stop."; exit 1; }
done
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
fi

add() {  # add <agent> <rule>
  local a="$1" rule="$2"
  if grep -q 'instruction set v1.7' "$W/$a/AGENTS.md"; then echo "$a: already v1.7, skipped"; return 0; fi
  if [ "$DRY" = 1 ]; then
    echo "$a: would append to $W/$a/AGENTS.md:"
    printf '    %s\n' "$rule"
    return 0
  fi
  printf '%s\n' "$rule" >> "$W/$a/AGENTS.md"
  git -C "$W/$a" add AGENTS.md
  git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.7 (APR-0075)" -- AGENTS.md
  echo "$a: v1.7 added"
}
add cho "$CHO_RULE"
add cos "$COS_RULE"
if [ "$DRY" = 1 ]; then
  echo "Dry run only. Nothing was changed."
else
  echo "Done. Start the gateway again with slack.env and openai.env sourced."
fi
