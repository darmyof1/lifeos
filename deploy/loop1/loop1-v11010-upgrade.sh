#!/usr/bin/env bash
# loop1-v11010-upgrade.sh - Loop 7 instruction set v1.10.10, COO only (APR-0132, wording approved as written).
# One rule is appended at the end of the COO file: the COO answers status questions by asking the agent.
# Refuses unless the COO is on v1.10.9. Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v11010-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v11010-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"
F="$W/coo/AGENTS.md"

RULE='- Status questions (instruction set v1.10.10): you cannot see what the CEO says to another agent directly, and you may not remember what other agents routed through you in another session. When the CEO asks what he last told an agent, what an agent did, or whether something was logged, do not answer from your own memory. Send that agent one question: what did the CEO last ask you and what did you do, in one or two sentences. Relay its answer, naming the agent and the run ID. If the agent cannot answer, say so. Do not give file paths; say which agent holds the record and that the CEO can ask it directly.'

[ -f "$F" ] || { echo "$F missing. Stop."; exit 1; }
if grep -q 'instruction set v1.10.1[012]' "$F"; then echo "coo: already v1.10.10 or later, skipped"; exit 0; fi
grep -q 'instruction set v1.10.9' "$F" || { echo "coo is not on v1.10.9. Run the earlier upgrades first. Stop."; exit 1; }
if [ "$DRY" = 1 ]; then
  echo "coo: would append at the end:"; printf '    %s\n' "$RULE"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
RULE="$RULE" F="$F" python3 - <<'PY'
import os
f = os.environ["F"]
text = open(f, encoding="utf-8").read()
if not text.endswith("\n"):
    text += "\n"
open(f, "w", encoding="utf-8").write(text + os.environ["RULE"] + "\n")
PY
git -C "$W/coo" add AGENTS.md
git -C "$W/coo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.10 (APR-0132)" -- AGENTS.md
echo "coo: v1.10.10 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
