#!/usr/bin/env bash
# loop1-v1108-upgrade.sh - Loop 7 instruction set v1.10.8, COO only (APR-0128, wording approved word for word).
# (1) "You may send to" becomes "CHO, CoS, CFO, CLO. (ADR-0018)"; (2) one row is added to the "Who needs to know" table
# (CEO request about TV shows or other lifestyle items -> CLO); (3) one rule is appended at the end of the file.
# Refuses unless the COO is on v1.10.7. Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v1108-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v1108-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"
F="$W/coo/AGENTS.md"

OLD_SEND='CHO, CoS, CFO. (ADR-0018)'
NEW_SEND='CHO, CoS, CFO, CLO. (ADR-0018)'
ROW_AFTER='| CEO request about sleep, workouts or food | CHO |'
ROW='| CEO request about TV shows or other lifestyle items | CLO |'
RULE='- Lifestyle requests (APR-0128, instruction set v1.10.8): a request about TV shows or other lifestyle items goes to the CLO, never to the CHO. Call sessions_send with sessionKey agent:clo:main and put the whole task in the message: what to log, the dates and times, the run ID, and, if the CEO asked for an appointment, say so. Tell the CEO only what the CLO'"'"'s reply confirms and name the CLO as the one who confirmed it. Never invent the CHO or any other agent for a lifestyle request.'

[ -f "$F" ] || { echo "$F missing. Stop."; exit 1; }
if grep -q 'instruction set v1.10.8' "$F"; then echo "coo: already v1.10.8, skipped"; exit 0; fi
grep -q 'instruction set v1.10.7' "$F" || { echo "coo is not on v1.10.7. Run the earlier upgrades first. Stop."; exit 1; }
[ "$(grep -cxF -- "$OLD_SEND" "$F")" = 1 ] || { echo "coo: the line '$OLD_SEND' is not there exactly once. Stop."; exit 1; }
[ "$(grep -cxF -- "$ROW_AFTER" "$F")" = 1 ] || { echo "coo: the first table row is not there exactly once. Stop."; exit 1; }
if [ "$DRY" = 1 ]; then
  echo "coo: would replace the line:"; printf '    %s\n' "$OLD_SEND"; echo "  with:"; printf '    %s\n' "$NEW_SEND"
  echo "  add the table row after the first row:"; printf '    %s\n' "$ROW"
  echo "  and append at the end:"; printf '    %s\n' "$RULE"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
OLD_SEND="$OLD_SEND" NEW_SEND="$NEW_SEND" ROW_AFTER="$ROW_AFTER" ROW="$ROW" RULE="$RULE" F="$F" python3 - <<'PY'
import os
f = os.environ["F"]
text = open(f, encoding="utf-8").read()
if not text.endswith("\n"):
    text += "\n"
out = []
for l in text.split("\n")[:-1]:
    if l == os.environ["OLD_SEND"]:
        l = os.environ["NEW_SEND"]
    out.append(l)
    if l == os.environ["ROW_AFTER"]:
        out.append(os.environ["ROW"])
out.append(os.environ["RULE"])
open(f, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
git -C "$W/coo" add AGENTS.md
git -C "$W/coo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 1 instructions v1.10.8 (APR-0128)" -- AGENTS.md
echo "coo: v1.10.8 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
