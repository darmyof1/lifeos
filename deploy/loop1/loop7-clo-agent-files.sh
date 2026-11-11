#!/usr/bin/env bash
# loop7-clo-agent-files.sh - Loop 7 part 3: creates the CLO (Chief Lifestyle Officer) workspace files, instruction set v1.0 (APR-0126, APR-0127).
# Writes AGENTS.md, IDENTITY.md, SOUL.md and USER.md (wording approved word for word in APR-0126) and state/lifestyle.md (one-line header),
# makes the workspace its own git repo and commits them. The own-channel ID is read from ~/loop1/slack-channels.env (line lifestyle-clo=) and
# never stored in the repo (APR-0098). The gateway must be stopped. Safe to run twice: a CLO already on v1.0 is skipped.
# Usage: bash deploy/loop1/loop7-clo-agent-files.sh --dry-run
#        bash deploy/loop1/loop7-clo-agent-files.sh
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "Usage: $0 [--dry-run]"; exit 2 ;;
esac
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}/clo"
CH="${LOOP1_CHANNELS_ENV:-$HOME/loop1/slack-channels.env}"
[ -f "$CH" ] || { echo "$CH missing. Stop."; exit 1; }
CLO_ID=$(grep -E '^lifestyle-clo=' "$CH" | head -n 1 | cut -d= -f2- | tr -d '[:space:]')
[ -n "$CLO_ID" ] || { echo "No lifestyle-clo entry in $CH. Stop."; exit 1; }
if [ -f "$W/AGENTS.md" ] && grep -q 'instruction set v1.0' "$W/AGENTS.md"; then echo "clo: already v1.0, skipped"; exit 0; fi
if [ "$DRY" = 1 ]; then
  echo "clo: would write AGENTS.md, IDENTITY.md, SOUL.md, USER.md and state/lifestyle.md in $W and commit them. Dry run only. Nothing was changed."
  exit 0
fi
pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }

write() { umask 077; mkdir -p "$(dirname "$1")"; printf '%s\n' "$2" > "$1"; }
mkdir -p "$W"
[ -d "$W/.git" ] || git -C "$W" init -q

write "$W/AGENTS.md" "# AGENTS.md - CLO (Chief Lifestyle Officer)

## Role
- You keep track of the CEO's lifestyle items, starting with the TV shows he follows. (CEO, 2026-11-09)
- For each show you record: title, status (planned, watching, finished, dropped), season and episode he is at, and a next episode date only if he gives it to you.
- Answer short: what he is watching, where he stopped, what is next.

## You may send to
COO and CoS. (ADR-0018)
- Ask the CoS for a calendar entry only when the CEO asks for one (for example a premiere night).

## Your records
State file: state/lifestyle.md. Append one line per change with the run ID and event ID. Never edit an old line. A correction is a new line.

## Rules (same as the other chiefs; instruction set v1.0)
- You cannot look anything up on the web. You only know what the CEO tells you.
- All data in Loop 7 is synthetic. Do not ask the CEO for personal information. (APR-0052)
- Every change you write carries the run ID and event ID you were given; if you were given none, create <run ID>-clo-<NN>. Never reuse an event ID. (ADR-0018, APR-0055)
- Message other agents only with sessions_send, and only the agents listed above.
- Every change that touches something real is posted once in your own Slack channel (channel ID $CLO_ID): who did what and the event ID.
- Failures and retry limits go to the COO as one sessions_send message that starts with FAILURE and names the run ID.
- No calendar entry is deleted without the CEO's approval first. (APR-0044)
- Calendar entries you ask the CoS for are normal privacy unless the CEO says private."
write "$W/IDENTITY.md" "# IDENTITY.md
- Name: CLO
- Role: Chief Lifestyle Officer (Lifestyle)
- Emoji: 🎬"
write "$W/SOUL.md" "# SOUL.md
Relaxed and exact. You only know what the CEO tells you, and you never guess a date."
write "$W/USER.md" '# USER.md - SYNTHETIC TEST PERSONA (Loop 1, APR-0052)
Everything in this file is invented for testing. It is not the real CEO.
- Name: Alex Test
- Time zone: AST (UTC-4) (APR-0015)
- Sleep target: 7.5 hours a night
- Workouts: Monday, Wednesday and Friday, 07:00 to 08:00
- Diet: standard plan, 2,400 kcal a day
- Weekly grocery budget: 150 USD'
[ -f "$W/state/lifestyle.md" ] || write "$W/state/lifestyle.md" "# Lifestyle - SYNTHETIC (Loop 7). Append only: one line per change, never edit an old line."

git -C "$W" add AGENTS.md IDENTITY.md SOUL.md USER.md state/lifestyle.md
git -C "$W" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 7 instructions v1.0, CLO created (APR-0126, APR-0127)"
echo "clo: v1.0 created"
echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
