#!/usr/bin/env bash
# loop1-v11012-upgrade.sh - Loop 7 instruction set v1.10.12, COO only (APR-0137, wording approved as written).
# REPLACES the v1.10.11 "Status questions" rule in place with the v1.10.12 rule (no second rule is added).
# Refuses unless the COO is on v1.10.11. Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Config: this script does not touch the OpenClaw config. The COO read tool (agents.entries.coo.tools.alsoAllow ["read"] and
# agents.entries.coo.tools.fs.workspaceOnly true) is a separate, backed-up edit made with the gateway stopped (handover 38).
# Usage: bash deploy/loop1/loop1-v11012-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v11012-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"
F="$W/coo/AGENTS.md"
OLDSTART='- Status questions (instruction set v1.10.11):'

RULE='- Status questions (instruction set v1.10.12): you cannot see what the CEO says to another agent directly, and you may not remember what other agents routed through you in another session. When the CEO asks what he last told an agent, what an agent did, or whether something was logged, do not answer from your own memory. First read the file send-log-YYYY-MM.md for the current month in your state folder (if the month is new and it has no line for that agent, read last month'"'"'s file) and find the newest lines for that agent. Each line has a time, the words send or ceo-message, the agent names and a run ID; none of them holds what was said. A send line that says error with the text '"'"'changed while starting work'"'"' still means the message arrived. Then send that agent one question: read the last entries in your own state files and tell me what was last logged for the CEO, with the date, in one or two sentences. Add the time and run ID from the newest log line when there is one. Do not answer from conversation memory. Relay its answer, naming the agent, the date and the run ID. If the log has no line for that agent, say so, and still ask the agent. If the agent finds nothing, say so. Never write a file path or a file name in your answer; say which agent holds the record and that the CEO can ask it directly.'

[ -f "$F" ] || { echo "$F missing. Stop."; exit 1; }
if grep -q 'instruction set v1.10.12' "$F"; then echo "coo: already v1.10.12, skipped"; exit 0; fi
grep -q 'instruction set v1.10.11' "$F" || { echo "coo is not on v1.10.11. Run the earlier upgrades first. Stop."; exit 1; }
[ "$(grep -c -F -- "$OLDSTART" "$F")" = 1 ] || { echo "coo: the v1.10.11 Status questions rule is not there exactly once. Stop."; exit 1; }
if [ "$DRY" = 1 ]; then
  echo "coo: would replace the v1.10.11 Status questions rule (same place) with:"; printf '    %s\n' "$RULE"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
RULE="$RULE" OLDSTART="$OLDSTART" F="$F" python3 - <<'PY'
import os
f = os.environ["F"]
lines = open(f, encoding="utf-8").read().split("\n")
out = []
for l in lines:
    out.append(os.environ["RULE"] if l.startswith(os.environ["OLDSTART"]) else l)
open(f, "w", encoding="utf-8").write("\n".join(out))
PY
git -C "$W/coo" add AGENTS.md
git -C "$W/coo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.12 (APR-0137)" -- AGENTS.md
echo "coo: v1.10.12 replaced the status rule"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
