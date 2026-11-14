#!/usr/bin/env bash
# loop1-v11-clo-upgrade.sh - Loop 7 CLO instruction set v1.1 (APR-0128, wording approved word for word).
# (1) the line "Ask the CoS for a calendar entry only when the CEO asks for one (for example a premiere night)." is replaced by two bullets
# (the same line with a second example, and the handoff call); (2) two rules are appended to "Rules" (the end of the file).
# Refuses unless the CLO is on v1.0. Commits AGENTS.md only. Does not touch state/ or the OpenClaw config. Safe to run twice.
# Usage: bash deploy/loop1/loop1-v11-clo-upgrade.sh --dry-run
#        bash deploy/loop1/loop1-v11-clo-upgrade.sh   (the gateway must be stopped: systemctl --user stop openclaw-loop1-gateway)
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"
F="$W/clo/AGENTS.md"

OLD='- Ask the CoS for a calendar entry only when the CEO asks for one (for example a premiere night).'
NEW1='- Ask the CoS for a calendar entry only when the CEO asks for one (for example a premiere night, or "make an appointment to watch episode 4").'
NEW2='- Handoff call (APR-0128, instruction set v1.1): call sessions_send with exactly these fields: sessionKey agent:cos:main, message (the whole task: what to do, dates and times, run ID, your own event ID, normal privacy unless the CEO said private), mode followup, timeoutSeconds 120. Your event IDs are <run ID>-clo-01, -clo-02 and so on. Never set watch. Never use mode notify or resume. Do not look up the tool'"'"'s API files or list sessions first. The returned reply is the result. If a call fails or returns queued, resend the same message once with the same fields.'
R1='- If the CEO asks for something you cannot look up (for example when a show returns), say so in one sentence and ask him for the date. Record it only when he gives it.'
R2='- You may give a short synopsis of an episode from what you already know, and you must say it is from memory and may be wrong. (APR-0128)'

[ -f "$F" ] || { echo "$F missing. Stop."; exit 1; }
if grep -qF 'APR-0128, instruction set v1.1)' "$F"; then echo "clo: already v1.1, skipped"; exit 0; fi
grep -q 'instruction set v1.0' "$F" || { echo "clo is not on v1.0. Run the CLO creation first. Stop."; exit 1; }
[ "$(grep -cxF -- "$OLD" "$F")" = 1 ] || { echo "clo: the calendar line is not there exactly once. Stop."; exit 1; }
if [ "$DRY" = 1 ]; then
  echo "clo: would replace the line:"; printf '    %s\n' "$OLD"; echo "  with:"; printf '    %s\n' "$NEW1" "$NEW2"
  echo "  and append at the end:"; printf '    %s\n' "$R1" "$R2"
  echo "Dry run only. Nothing was changed."
  exit 0
fi
pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
OLD="$OLD" NEW1="$NEW1" NEW2="$NEW2" R1="$R1" R2="$R2" F="$F" python3 - <<'PY'
import os
f = os.environ["F"]
text = open(f, encoding="utf-8").read()
if not text.endswith("\n"):
    text += "\n"
out = []
for l in text.split("\n")[:-1]:
    if l == os.environ["OLD"]:
        out.extend([os.environ["NEW1"], os.environ["NEW2"]])
    else:
        out.append(l)
out.extend([os.environ["R1"], os.environ["R2"]])
open(f, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
git -C "$W/clo" add AGENTS.md
git -C "$W/clo" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 7 instructions v1.1 (APR-0128)" -- AGENTS.md
echo "clo: v1.1 added"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
