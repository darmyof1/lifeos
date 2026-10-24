#!/usr/bin/env bash
# loop1-v14-upgrade.sh - Loop 1 instruction set v1.4 (APR-0065). Run on the VM after loop1-v13-upgrade.sh (v1.3).
# Appends the v1.4 lines to the CHO, CoS and CFO AGENTS.md and commits AGENTS.md only in each workspace git.
# Does not touch or commit state/ files. Safe to run twice: an agent already on v1.4 is skipped.
# The COO needs no v1.4 line (its wait and one-answer rules are in v1.3).
# Gateway must be stopped, as for the earlier upgrade scripts.
set -euo pipefail
W=~/loop1/workspaces
pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
for a in cho cos cfo; do
  [ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Stop."; exit 1; }
  grep -q 'instruction set v1.3' "$W/$a/AGENTS.md" || { echo "$a is not on v1.3. Run loop1-v13-upgrade.sh first. Stop."; exit 1; }
done

ANSWER='- Answer once (APR-0065, instruction set v1.4): when another agent'"'"'s message asks you to do something, your answer to that message is your report. Do not also send a separate sessions_send message about it to that agent or to the COO. Failures still go to the COO as FAILURE messages (instruction set v1.3).'
WAIT='- Waiting (APR-0065, instruction set v1.4): when you send a request to another agent that asks for a change, use timeoutSeconds 120 and wait for the reply. The reply is the result: report done only from it. If the wait ends with no reply, report "no reply from <agent>" and send the COO a FAILURE message.'
COSNOTE='- Replaces step 4 of "Writing an entry" (APR-0065, instruction set v1.4): reply to the requester only. The requester'"'"'s report carries your result to the COO. Your own-channel post (instruction set v1.3) still goes out.'

add() {  # agent, then lines
  a=$1; shift
  if grep -q 'instruction set v1.4' "$W/$a/AGENTS.md"; then echo "$a: already v1.4, skipped"; return; fi
  printf '%s\n' "$@" >> "$W/$a/AGENTS.md"
  # Commit AGENTS.md only. Never git add -A: state/ may hold uncommitted run data, and HEAD must stay the seed state.
  git -C "$W/$a" add AGENTS.md
  git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.4 (APR-0065)" -- AGENTS.md || true
  echo "$a: v1.4 added"
}

add cho "$WAIT" "$ANSWER"
add cos "$ANSWER" "$COSNOTE"
add cfo "$ANSWER"
echo "Done. Start the gateway again with slack.env and openai.env sourced."
