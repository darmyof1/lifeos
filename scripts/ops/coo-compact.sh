#!/usr/bin/env bash
# coo-compact.sh - compact the COO's Slack channel session (Loop 6, APR-0121; measure in APR-0116 handover 23 report).
#
# Same command and session as handover 23: openclaw sessions compact "<COO Slack channel session key>" --agent coo --max-lines 1
# The session key is found at run time (the one key that starts with agent:coo:slack:channel:), so no Slack ID is stored here.
#
# Usage: coo-compact.sh            dry run (default): says what it would do, changes nothing
#        coo-compact.sh --execute  compacts
#
# Rules, in this order:
#   1. REFUSED inside 03:30 to 05:10 AST (no compaction then): exit 2.
#   2. SKIPPED if the COO channel session had a message in the last 10 minutes.
#   3. SKIPPED if a CEO request is waiting: the newest journal line of any event is "requested" or "delete-pending-approval".
#   4. Otherwise compacts (with --execute) and logs the session size (tokens) before and after.
# One log line per run in $COO_COMPACT_LOG (default ~/loop1/state/coo-compact.log): time, result, sizes. Never message text.
# Exit codes: 0 compacted, dry run, or skipped by rule 2 or 3; 2 refused (window); 3 error (no session, several sessions, compact failed);
#             64 bad option.
#
# Test hooks (used by tests/unit/test_coo_compact.py): COO_COMPACT_BIN (the openclaw command), COO_COMPACT_NOW (HH:MM, AST),
# COO_COMPACT_NOWMS (epoch milliseconds), COO_COMPACT_JOURNAL, COO_COMPACT_LOG, COO_COMPACT_TOKEN_FILE, COO_COMPACT_ENV (0 = do not source env.sh).
set -u

EXECUTE=0
case "${1:-}" in
  "") ;;
  --execute) EXECUTE=1 ;;
  *) echo "usage: coo-compact.sh [--execute]" >&2; exit 64 ;;
esac

if [ "${COO_COMPACT_ENV:-1}" = "1" ] && [ -f "$HOME/loop1/env.sh" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$HOME/loop1/env.sh"
  set +a
fi
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:$PATH"

BIN="${COO_COMPACT_BIN:-openclaw}"
JOURNAL="${COO_COMPACT_JOURNAL:-$HOME/loop1/workspaces/cos/state/calendar-journal.md}"
LOG="${COO_COMPACT_LOG:-$HOME/loop1/state/coo-compact.log}"
TOKEN_FILE="${COO_COMPACT_TOKEN_FILE:-$HOME/loop1/gateway-token}"
mkdir -p "$(dirname "$LOG")"

STAMP="$(TZ=America/Puerto_Rico date '+%Y-%m-%d %H:%M:%S')"
MODE="dry-run"; [ "$EXECUTE" = 1 ] && MODE="execute"
log() { echo "$STAMP AST mode=$MODE result=$1${2:+ $2}" >>"$LOG"; echo "coo-compact: $1${2:+ ($2)}"; }

# 1. time window
HM="${COO_COMPACT_NOW:-$(TZ=America/Puerto_Rico date '+%H:%M')}"
MIN=$((10#${HM%%:*} * 60 + 10#${HM##*:}))
if [ "$MIN" -ge $((3 * 60 + 30)) ] && [ "$MIN" -lt $((5 * 60 + 10)) ]; then
  log refused "inside 03:30 to 05:10 AST"
  exit 2
fi

# 2. find the session and its last message time and size
NOWMS="${COO_COMPACT_NOWMS:-$(( $(date +%s) * 1000 ))}"
list_sessions() { "$BIN" sessions --all-agents --json 2>&1; }
parse() {  # prints: <count> <key> <lastMs> <tokens>   (key and numbers only; the JSON is read from stdin)
  python3 -c '
import json, sys
try:
    d = json.loads(sys.stdin.read())
    rows = [s for s in d.get("sessions", []) if str(s.get("key", "")).startswith("agent:coo:slack:channel:")]
except Exception:
    print("0 - 0 unknown"); sys.exit()
if len(rows) != 1:
    print("%d - 0 unknown" % len(rows)); sys.exit()
s = rows[0]
last = max(int(s.get("lastInteractionAt") or 0), int(s.get("updatedAt") or 0))
tok = s.get("totalTokens")
print("1 %s %d %s" % (s["key"], last, int(tok) if isinstance(tok, (int, float)) and s.get("totalTokensFresh", True) else "unknown"))
'
}
read -r COUNT KEY LASTMS BEFORE < <(list_sessions | parse)
if [ "$COUNT" != "1" ]; then
  log error "COO channel sessions found: $COUNT (need exactly 1)"
  exit 3
fi

AGE_MIN=$(( (NOWMS - LASTMS) / 60000 ))
if [ "$AGE_MIN" -lt 10 ]; then
  log skipped "session had a message $AGE_MIN min ago (limit 10); size=$BEFORE"
  exit 0
fi

# 3. a waiting CEO request: the newest line of an event is requested or delete-pending-approval
WAITING="$(python3 - "$JOURNAL" <<'PY'
import sys
last = {}
try:
    for line in open(sys.argv[1], encoding="utf-8"):
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 6 and p[3] in ("requested", "written", "pushed", "failed", "conflict", "moved", "delete-pending-approval", "deleted"):
            last[p[5]] = p[3]
except OSError:
    print("unreadable"); sys.exit()
print(sum(1 for v in last.values() if v in ("requested", "delete-pending-approval")))
PY
)"
if [ "$WAITING" = "unreadable" ]; then
  log skipped "journal unreadable, cannot tell if a request is waiting; size=$BEFORE"
  exit 0
fi
if [ "$WAITING" != "0" ]; then
  log skipped "$WAITING CEO request(s) waiting in the journal; size=$BEFORE"
  exit 0
fi

# 4. compact
if [ "$EXECUTE" != 1 ]; then
  log would-compact "size=$BEFORE; nothing changed"
  exit 0
fi
TOKEN="$(cat "$TOKEN_FILE" 2>/dev/null)"
OUT="$("$BIN" sessions compact "$KEY" --agent coo --max-lines 1 --token "$TOKEN" 2>&1)"; RC=$?
if [ $RC -ne 0 ] || ! echo "$OUT" | grep -qE 'Compacted session|No compaction needed'; then
  log error "compact failed (exit $RC): $(echo "$OUT" | grep -iE 'error|fail|unable|cannot' | head -1 | cut -c1-120 | tr -d '\r' | sed -E 's/channel:[A-Za-z0-9]+/channel:<id>/g'); size=$BEFORE"
  exit 3
fi
RESULT="compacted"; echo "$OUT" | grep -q 'No compaction needed' && RESULT="no-compaction-needed"
read -r _C _K _L AFTER < <(list_sessions | parse)
KEPT="$(echo "$OUT" | sed -n 's/.*kept \([0-9]*\) lines.*/\1/p' | head -1)"
# right after a compaction the gateway has no fresh token count until the next turn: then the after size is "unknown" and the kept lines say what is left
log "$RESULT" "size_before=$BEFORE size_after=${AFTER:-unknown}${KEPT:+ kept_lines=$KEPT}"
exit 0
