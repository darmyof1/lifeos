#!/usr/bin/env bash
# loop1-v16-upgrade.sh - Loop 1 instruction set v1.6 (APR-0067, P-35 stays open). Run on the VM after v1.4 on the CoS.
# Appends one CoS rule: an acknowledgement error after a sent message is reported as delivered, not as FAILURE; no resend.
# Commits cos/AGENTS.md only. Does not touch state/. Safe to run twice.
# Gateway must be stopped, as for the earlier upgrade scripts.
set -euo pipefail
W=~/loop1/workspaces
pgrep -f "openclaw.*gateway" >/dev/null && { echo "Gateway is running. Stop it with Ctrl-C first. Stop."; exit 1; }
[ -f "$W/cos/AGENTS.md" ] || { echo "$W/cos/AGENTS.md missing. Stop."; exit 1; }
grep -q 'instruction set v1.4' "$W/cos/AGENTS.md" || { echo "CoS is not on v1.4. Run the earlier upgrades first. Stop."; exit 1; }
if grep -q 'instruction set v1.6' "$W/cos/AGENTS.md"; then echo "cos: already v1.6, skipped"; exit 0; fi

RULE='- Acknowledgement errors (P-35, instruction set v1.6): if a message you sent to a waiting agent is logged as sent but its acknowledgement fails (for example a session-start error or SESSION_WORK_START_CHANGED), do not report FAILURE to the COO. Report: delivered; acknowledgement error (P-35), and say whether the receiving agent has replied with the content. Do not resend, to avoid duplicates. Report FAILURE only if the message was not sent, or the receiving agent says it did not get the content.'
printf '%s\n' "$RULE" >> "$W/cos/AGENTS.md"
git -C "$W/cos" add AGENTS.md
git -C "$W/cos" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.6 (P-35)" -- AGENTS.md || true
echo "cos: v1.6 added"
echo "Done. Start the gateway again with slack.env and openai.env sourced."
