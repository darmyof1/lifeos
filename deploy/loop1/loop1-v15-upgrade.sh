#!/usr/bin/env bash
# loop1-v15-upgrade.sh - Loop 1 instruction set v1.5 (proposed as P-34; apply only after the CEO says yes). Run on the VM after loop1-v14-upgrade.sh (v1.4).
# Appends one COO rule: the COO must carry the full task inline when it hands off, and resend once if an agent can't find it.
# Commits coo/AGENTS.md only. Does not touch state/. Safe to run twice: skips the COO if it is already on v1.5.
# Gateway must be stopped, as for the earlier upgrade scripts.
set -euo pipefail
W=~/loop1/workspaces
pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
[ -f "$W/coo/AGENTS.md" ] || { echo "$W/coo/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.3' "$W/coo/AGENTS.md" || { echo "COO is not on v1.3. Run the earlier upgrades first. Stop."; exit 1; }
if grep -q 'instruction set v1.5' "$W/coo/AGENTS.md"; then echo "coo: already v1.5, skipped"; exit 0; fi

RULE='- Handoff details (P-34, instruction set v1.5): when you route a request to another agent, put the whole task in the sessions_send body in plain words - what to do, the dates and times, and the run ID. Never tell an agent to find the task in its own history or queue. If an agent replies that it cannot find the task details, resend once with the full details inline, then treat that reply as the result. Report the retry to the CEO only if the resend also fails.'
printf '%s\n' "$RULE" >> "$W/coo/AGENTS.md"
git -C "$W/coo" add AGENTS.md
git -C "$W/coo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.5 (P-34)" -- AGENTS.md || true
echo "coo: v1.5 added"
echo "Done. Start the gateway again with slack.env and openai.env sourced."
