#!/usr/bin/env bash
# loop1-v1109-upgrade.sh - Loop 7 instruction set v1.10.9, COO only (APR-0129, wording approved as written).
# One rule is appended at the end of the COO file: the COO builds its own run ID (coo-<YYYYMMDD>-<HHMM>, AST).
# Refuses unless the COO is on v1.10.8. Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1109-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1109-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"
F="$W/coo/AGENTS.md"

RULE='- Run IDs (instruction set v1.10.9): when the CEO'"'"'s message does not state a run ID, make one yourself in this form: coo-<YYYYMMDD>-<HHMM>, the date and the time in AST when you received the message, for example coo-20261114-1028. A message states a run ID only when it says "run ID" followed by the ID. Never use a word, name or code from the CEO'"'"'s messages, from other channels or from your history as a run ID or as part of one. Use the same run ID for every agent you message about that request, and name it in your answer.'

[ -f "$F" ] || { echo "$F missing. Stop."; exit 1; }
if grep -q 'instruction set v1.10.9' "$F"; then echo "coo: already v1.10.9, skipped"; exit 0; fi
grep -q 'instruction set v1.10.8' "$F" || { echo "coo is not on v1.10.8. Run the earlier upgrades first. Stop."; exit 1; }
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
git -C "$W/coo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.9 (APR-0129)" -- AGENTS.md
echo "coo: v1.10.9 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
