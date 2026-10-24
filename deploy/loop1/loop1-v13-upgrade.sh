#!/usr/bin/env bash
# loop1-v13-upgrade.sh - Loop 1 instruction set v1.3 (APR-0064). Run on the VM after loop1-agent-files.sh (v1.2).
# Appends the v1.3 lines to each agent's AGENTS.md and commits AGENTS.md only in the workspace git. Does not touch or commit state/ files.
# (The first version used git add -A and committed the run-007 state; fixed 2026-10-24.)
# Safe to run twice: an agent that already has the v1.3 lines is skipped.
# Own-channel posts need each agent's Slack channel ID. The IDs are read from ~/loop1/slack-channels.env on the VM
# (lines staff-cos=, operations-coo=, health-cho=, finance-cfo=) and are never stored in the repo.
# Gateway must be stopped, as for the v1.2 script.
set -euo pipefail
W=~/loop1/workspaces
CH=~/loop1/slack-channels.env
pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
[ -f "$CH" ] || { echo "$CH missing. Stop."; exit 1; }
id_of() { v=$(grep -E "^$1=" "$CH" | head -n 1 | cut -d= -f2- | tr -d '[:space:]'); [ -n "$v" ] || { echo "No $1 entry in $CH. Stop." >&2; exit 1; }; printf '%s' "$v"; }
CHO_ID=$(id_of health-cho); COS_ID=$(id_of staff-cos); CFO_ID=$(id_of finance-cfo); id_of operations-coo >/dev/null
for a in coo cho cos cfo; do
  [ -f "$W/$a/AGENTS.md" ] || { echo "$W/$a/AGENTS.md missing. Run loop1-agent-files.sh first. Stop."; exit 1; }
  grep -q 'instruction set v1.2' "$W/$a/AGENTS.md" || { echo "$a is not on v1.2. Stop."; exit 1; }
done

F='- Failures (APR-0050, instruction set v1.3): if a request fails or you reach a retry limit, send the COO one sessions_send message that starts with FAILURE and names the run ID. Do not post failures yourself.'
post_line() { printf '%s' "- Own-channel post (APR-0050, instruction set v1.3): after you write a real change (calendar entry, plan change, budget change) or send a request that asks for one, post one line in your own Slack channel with the message tool, channel ID $1: who did what, and the event ID. Post once per event ID. Do not post routine reads or status checks."; }

add() {  # agent, then lines
  a=$1; shift
  if grep -q 'instruction set v1.3' "$W/$a/AGENTS.md"; then echo "$a: already v1.3, skipped"; return; fi
  printf '%s\n' "$@" >> "$W/$a/AGENTS.md"
  # Commit AGENTS.md only. Never git add -A here: state/ may hold uncommitted run data, and HEAD must stay the seed state.
  git -C "$W/$a" add AGENTS.md
  git -C "$W/$a" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.3 (APR-0064)" -- AGENTS.md || true
  echo "$a: v1.3 added"
}

add coo \
 '- Waiting (APR-0064, instruction set v1.3): when you send a request with sessions_send, set timeoutSeconds to 240 and wait for the reply. The reply is the result. Do not ask other agents to confirm it, and do not read other agents'"'"' sessions.' \
 '- One answer (APR-0064, instruction set v1.3): reply to the CEO once, as your final answer. Do not use the message tool to post in the channel you are answering in.' \
 '- Late replies (APR-0064, instruction set v1.3): if a reply arrives for a request you already answered, write one line starting "Late reply:" with the event ID. Do not repeat the summary.' \
 '- Failures (APR-0050, instruction set v1.3): put every FAILURE message you receive in your answer to the CEO, with the run ID.'
add cho "$(post_line "$CHO_ID")" "$F"
add cos "$(post_line "$COS_ID")" "$F"
add cfo "$(post_line "$CFO_ID")" "$F"
echo "Done. Start the gateway again with slack.env and openai.env sourced."
