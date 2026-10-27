#!/usr/bin/env bash
# loop1-v110-upgrade.sh - Loop 2 instruction set v1.10 (APR-0092). Run on the VM after v1.9.1 (CoS), v1.9 (CFO) and v1.5 (COO).
# Appends rules to three agents:
#   CoS: the delete gate (APR-0044) and overlaps (S-08): log a conflict line, keep the existing entry, offer the nearest free slot.
#   COO: report only what is confirmed; the standard approval request; one-line conflict notices; quote the CEO's words on deletes.
#   CFO: the same calendar handoff call as the CHO (v1.7), with its own event IDs.
# Commits AGENTS.md only in each workspace. Does not touch state/ or the OpenClaw config (the CFO send list is a separate step).
# Safe to run twice: an agent already on v1.10 is skipped.
# Usage: bash deploy/loop1/loop1-v110-upgrade.sh --dry-run   (shows the rules, changes nothing)
#        bash deploy/loop1/loop1-v110-upgrade.sh             (applies; the gateway must be stopped:
#                                                             systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="$HOME/loop1/workspaces"

COS_DELETE='- Deletes (APR-0044, APR-0092, instruction set v1.10): never write deleted because of a request alone. If the CEO'"'"'s own words, quoted in the message you received, clearly tell you to delete a named entry, append two lines for that entry: delete-pending-approval, then deleted, both with the same run ID and the same event ID, requested by CEO. If the request comes from a chief, or the CEO only asks a question (for example "can you remove"), append only the delete-pending-approval line and answer that it waits for the CEO'"'"'s approval. When the COO passes on the CEO'"'"'s approval with his words quoted and the event ID, append the deleted line with the same event ID as the pending line. Never say Google Calendar has changed: only the push job changes Google.'
COS_OVERLAP='- Overlaps (S-08, APR-0092, instruction set v1.10): before you append a written line for a new entry, check the journal for an entry that overlaps it in time on the same day. If one does, do not append written. The existing entry keeps its slot. Append one line for the new entry with status conflict, its run ID and event ID, the real requester in requested by, and the detail reason=overlaps <existing entry name>. Find the nearest free slot of the same length on the same day and offer it in your answer. Write the new entry only when the requester accepts that slot (a new written line at the new time). If the requester says the time cannot move, tell the COO so the CEO can decide. In requested by always name who really asked (CHO, CFO, COO or CEO).'
COO_CONFIRMED='- Confirmed reports only (APR-0092, instruction set v1.10): tell the CEO only what a reply from the CHO, CFO or CoS confirms, and name who confirmed it. If something is not confirmed, say "not confirmed". Never say Google Calendar has changed: only the push job changes Google. Never make up an event ID. Never tell another agent that the CEO approved something unless the CEO'"'"'s message says so; when you route a delete, quote the CEO'"'"'s words exactly.'
COO_APPROVAL='- Approval requests and notices (APR-0092, instruction set v1.10): when something needs the CEO'"'"'s approval (a delete a chief asked for, a delete the CEO only asked about, a time two chiefs both need), post one message with these lines: What. Used for. Why now. Risk if approved. Risk if not. Recommendation. Reply: approve, explain more, or keep. When the CEO approves a delete, pass it to the CoS with his words quoted and the event ID. When the CoS reports a conflict it resolved, tell the CEO in one line what happened, who asked, why it clashed, what the CoS did and what it means for the day; no action is needed unless he wants to override.'
CFO_HANDOFF='- Handoff call (APR-0044, APR-0092, instruction set v1.10): calendar entries you need go straight to the CoS, not through the COO. Call sessions_send with exactly these fields: sessionKey agent:cos:main, message (the whole task: what to do, dates and times, run ID, your own event ID, privacy=high), mode followup, timeoutSeconds 120. Your event IDs are <run ID>-cfo-01, -cfo-02 and so on. Never set watch. Never use mode notify or resume. Do not look up the tool'"'"'s API files or list sessions first. The returned reply is the result. If a call fails or returns queued, resend the same message once with the same fields.'

# Check every agent before changing any.
for a in coo cos cfo; do
  [ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
done
grep -q 'instruction set v1.5' "$W/coo/AGENTS.md" || { echo "coo is not on v1.5. Run the earlier upgrades first. Stop."; exit 1; }
grep -q 'instruction set v1.9.1' "$W/cos/AGENTS.md" || { echo "cos is not on v1.9.1. Run the earlier upgrades first. Stop."; exit 1; }
grep -q 'instruction set v1.9' "$W/cfo/AGENTS.md" || { echo "cfo is not on v1.9. Run the earlier upgrades first. Stop."; exit 1; }
if [ "$DRY" = 0 ]; then
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
fi

add() {  # add <agent> <rule> [<rule> ...]
  local a="$1"; shift
  if grep -q 'instruction set v1.10' "$W/$a/AGENTS.md"; then echo "$a: already v1.10, skipped"; return 0; fi
  if [ "$DRY" = 1 ]; then
    echo "$a: would append to $W/$a/AGENTS.md:"
    printf '    %s\n' "$@"
    return 0
  fi
  printf '%s\n' "$@" >> "$W/$a/AGENTS.md"
  git -C "$W/$a" add AGENTS.md
  git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10 (APR-0092)" -- AGENTS.md
  echo "$a: v1.10 added"
}
add cos "$COS_DELETE" "$COS_OVERLAP"
add coo "$COO_CONFIRMED" "$COO_APPROVAL"
add cfo "$CFO_HANDOFF"
if [ "$DRY" = 1 ]; then
  echo "Dry run only. Nothing was changed."
else
  echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
fi
