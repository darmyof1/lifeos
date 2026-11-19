#!/usr/bin/env bash
# loop1-v11011-upgrade.sh - Loop 7 instruction set v1.10.11, COO only (APR-0133, wording approved as written).
# REPLACES the v1.10.10 "Status questions" rule in place with the v1.10.11 rule (no second rule is added).
# Refuses unless the COO is on v1.10.10. Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v11011-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v11011-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"
F="$W/coo/AGENTS.md"
OLDSTART='- Status questions (instruction set v1.10.10):'

RULE='- Status questions (instruction set v1.10.11): you cannot see what the CEO says to another agent directly, and you may not remember what other agents routed through you in another session. When the CEO asks what he last told an agent, what an agent did, or whether something was logged, do not answer from your own memory. Send that agent one question: read the last entries in your own state files and tell me what was last logged for the CEO, with the date, in one or two sentences. Do not answer from conversation memory. Relay its answer, naming the agent and the run ID. If the agent finds nothing, say so. Never write a file path or a file name in your answer; say which agent holds the record and that the CEO can ask it directly.'

[ -f "$F" ] || { echo "$F missing. Stop."; exit 1; }
if grep -q 'instruction set v1.10.11' "$F"; then echo "coo: already v1.10.11, skipped"; exit 0; fi
grep -q 'instruction set v1.10.10' "$F" || { echo "coo is not on v1.10.10. Run the earlier upgrades first. Stop."; exit 1; }
[ "$(grep -c -F -- "$OLDSTART" "$F")" = 1 ] || { echo "coo: the v1.10.10 Status questions rule is not there exactly once. Stop."; exit 1; }
if [ "$DRY" = 1 ]; then
  echo "coo: would replace the v1.10.10 Status questions rule (same place) with:"; printf '    %s\n' "$RULE"
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
git -C "$W/coo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.11 (APR-0133)" -- AGENTS.md
echo "coo: v1.10.11 replaced the status rule"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
