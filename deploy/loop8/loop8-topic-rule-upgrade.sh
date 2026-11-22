#!/usr/bin/env bash
# loop8-topic-rule-upgrade.sh - Loop 8 step 2: the topic rule for the CHO (v1.10), CFO (v1.12) and CLO (v1.2) (APR-0142, approved as written).
# Adds the rule "- New topics (...)" once, as the new last rule of the agent file. For the CLO it also widens the first Role line in place.
# Creates state/topics.md if missing: a header line and one line per file that already exists in state/ (NAMES ONLY, never content,
# never topics.md itself). Commits AGENTS.md only in the workspace git. Does not touch the OpenClaw config, other state files or other agents.
# Refuses unless the agent is on the expected old version (CHO v1.9, CFO v1.11, CLO v1.1). Safe to run twice ("already").
# Usage: bash deploy/loop8/loop8-topic-rule-upgrade.sh [cho|cfo|clo] [--dry-run]     (no agent id = all three)
#        The gateway must be stopped for a real run: systemctl --user stop openclaw-loop1-gateway
set -euo pipefail
DRY=0; AGENTS_ARG=""
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    cho|cfo|clo) AGENTS_ARG="$AGENTS_ARG $a" ;;
    *) echo "Usage: $0 [cho|cfo|clo] [--dry-run]"; exit 2 ;;
  esac
done
AGENTS_ARG="${AGENTS_ARG:-cho cfo clo}"
W="${LOOP1_WORKSPACES:-$HOME/loop1/workspaces}"

read -r -d '' RULE_TEMPLATE <<'RULE' || true
- New topics (instruction set <version>): when the CEO asks you to start tracking something that belongs to your own domain and you have no file for it, do not refuse and do not wait for a setup. First read your topic index, state/topics.md. If the topic is already listed, use its file. If it is not, propose a simple log in two short lines: the file name (state/<topic>.md, lowercase words joined by hyphens) and the columns (date, what, one or two fields that fit the topic, run ID, event ID), with one example line built from what he just told you. Ask him once to confirm or change it. After he says yes, create the file with a header line, append the first entry, and append one line to state/topics.md (topic, file, columns, date). Append only: never edit an old line; a correction is a new line that says which line it corrects. Every entry carries the run ID and event ID as in your other rules, and the usual one-line post in your own channel. Do not create a calendar entry unless he asks for one. Answer questions about a topic from its file only. If he asks what you track, read state/topics.md and list the topics. Never ask for or write passwords, account numbers or login details. If the topic belongs to another chief's domain, say which chief holds that domain and write nothing.
RULE

ver_new() { case "$1" in cho) echo v1.10;; cfo) echo v1.12;; clo) echo v1.2;; esac; }
ver_old() { case "$1" in cho) echo v1.9;; cfo) echo v1.11;; clo) echo v1.1;; esac; }

for A in $AGENTS_ARG; do
  F="$W/$A/AGENTS.md"
  [ -f "$F" ] || { echo "$A: $F missing. Stop."; exit 1; }
  if grep -q -F -- '- New topics (instruction set' "$F"; then echo "$A: already has the topic rule, skipped"; continue; fi
  OLD="$(ver_old "$A")"
  grep -q -F -- "instruction set $OLD" "$F" || { echo "$A is not on $OLD. Run the earlier upgrades first. Stop."; exit 1; }
  if [ "$A" = clo ]; then
    [ "$(grep -c -F -- 'starting with the TV shows he follows' "$F")" = 1 ] || { echo "clo: the first Role line is not there exactly once. Stop."; exit 1; }
  fi
  if [ "$DRY" = 1 ]; then
    echo "$A: would add this rule as the new last rule (instruction set $(ver_new "$A")):"; printf '    %s\n' "${RULE_TEMPLATE//<version>/$(ver_new "$A")}"
    [ "$A" = clo ] && echo "clo: would widen the first Role line to: such as the TV shows he follows, travel, hobbies, home projects and vehicle maintenance"
    n=0; [ -d "$W/$A/state" ] && n=$(find "$W/$A/state" -maxdepth 1 -type f ! -name topics.md | wc -l)
    if [ -f "$W/$A/state/topics.md" ]; then echo "$A: state/topics.md exists, would be left as is"; else echo "$A: would create state/topics.md with a header and $n file-name line(s) (names only)"; fi
    continue
  fi
  pgrep -f "openclaw.*gateway run" >/dev/null && { echo "Gateway is running. Stop it first: systemctl --user stop openclaw-loop1-gateway. Stop."; exit 1; }
  RULE_LINE="${RULE_TEMPLATE//<version>/$(ver_new "$A")}" F="$F" A="$A" python3 - <<'PY'
import os
f = os.environ["F"]
s = open(f, encoding="utf-8").read()
if not s.endswith("\n"):
    s += "\n"
s += os.environ["RULE_LINE"] + "\n"
if os.environ["A"] == "clo":
    s = s.replace("starting with the TV shows he follows", "such as the TV shows he follows, travel, hobbies, home projects and vehicle maintenance", 1)
open(f, "w", encoding="utf-8").write(s)
PY
  mkdir -p "$W/$A/state"
  T="$W/$A/state/topics.md"
  if [ ! -f "$T" ]; then
    umask 077
    { echo "# topic index (one line per topic: topic, file, columns, date)"
      for f in "$W/$A/state"/*; do
        [ -f "$f" ] || continue
        b="$(basename "$f")"; [ "$b" = topics.md ] && continue
        echo "- ${b%.*} | state/$b | columns not read | seeded $(date +%F)"
      done; } > "$T"
  fi
  git -C "$W/$A" add AGENTS.md
  git -C "$W/$A" -c user.name=loop1 -c user.email=loop1@localhost commit -q -m "Loop 8 topic rule $(ver_new "$A") (APR-0142)" -- AGENTS.md
  echo "$A: $(ver_new "$A") added the topic rule; topic index has $(($(wc -l < "$T") - 1)) line(s)"
done
[ "$DRY" = 1 ] && echo "Dry run only. Nothing was changed." || echo "Done. Start the gateway again: systemctl --user start openclaw-loop1-gateway"
