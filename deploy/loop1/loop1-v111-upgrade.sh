#!/usr/bin/env bash
# loop1-v111-upgrade.sh - Loop 7 part 3: CFO instruction set v1.11 (APR-0126, wording approved word for word; APR-0127).
# CFO only: (1) the send line "COO. (ADR-0018)" becomes "COO and CoS. (ADR-0018, APR-0092)";
#           (2) a new "## Investments" section goes in after "Your records".
# Refuses unless the CFO is on v1.10. Commits AGENTS.md only in the CFO workspace. Does not touch state/ or the OpenClaw config.
# Safe to run twice: a CFO already on v1.11 is skipped.
# Usage: bash deploy/loop1/loop1-v111-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v111-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"
F="$W/cfo/AGENTS.md"

OLD_SEND='COO. (ADR-0018)'
NEW_SEND='COO and CoS. (ADR-0018, APR-0092)'
SECTION='## Investments (APR-0126, instruction set v1.11)
- You also track the CEO'"'"'s investment funds. For each fund you record three things: contributions (money he adds), growth (interest or returns), and the balance.
- Records: state/investments.md. Append one line per change: date, fund name, kind (contribution, growth, or balance check), amount, running balance, run ID, event ID. Never edit an old line. A correction is a new line that says which line it corrects.
- When asked how much is in a fund or how much it grew: answer from the file. Give total contributed, total growth, and the balance. Say in one sentence how much of the growth came from his added money and how much from interest. Show the arithmetic in one line.
- You record what the CEO tells you and add it up. You never move money, never give investment advice, never look up prices or rates, and never ask for account numbers, passwords or login details.
- All amounts in Loop 7 are synthetic. If a message looks like real account data, stop and tell the CEO to keep it out of the chat. (APR-0052)'

[ -f "$F" ] || { echo "$F missing. Stop."; exit 1; }
if grep -q 'instruction set v1.11' "$F"; then echo "cfo: already v1.11, skipped"; exit 0; fi
grep -q 'instruction set v1.10' "$F" || { echo "cfo is not on v1.10. Run the earlier upgrades first. Stop."; exit 1; }
[ "$(grep -cxF "$OLD_SEND" "$F")" = 1 ] || { echo "cfo: the line '$OLD_SEND' is not there exactly once. Stop."; exit 1; }
grep -q '^Setup note: keep budgets in state/budget.md' "$F" || { echo "cfo: the 'Your records' line is not there. Stop."; exit 1; }
if [ "$DRY" = 1 ]; then
  echo "cfo: would replace in $F the line:"; printf '    %s\n' "$OLD_SEND"
  echo "  with:"; printf '    %s\n' "$NEW_SEND"
  echo "  and add after the Your records line:"; printf '    %s\n' "$SECTION"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
OLD_SEND="$OLD_SEND" NEW_SEND="$NEW_SEND" SECTION="$SECTION" F="$F" python3 - <<'PY'
import os
f = os.environ["F"]
lines = open(f, encoding="utf-8").read().split("\n")
out = []
for l in lines:
    if l == os.environ["OLD_SEND"]:
        l = os.environ["NEW_SEND"]
    out.append(l)
    if l.startswith("Setup note: keep budgets in state/budget.md"):
        out.append("")
        out.extend(os.environ["SECTION"].split("\n"))
open(f, "w", encoding="utf-8").write("\n".join(out))
PY
git -C "$W/cfo" add AGENTS.md
git -C "$W/cfo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 7 instructions v1.11 (APR-0126, APR-0127)" -- AGENTS.md
echo "cfo: v1.11 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
