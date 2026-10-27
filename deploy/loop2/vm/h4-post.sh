#!/usr/bin/env bash
# h4-post.sh "<message>" - post one line to the COO channel (handover 4). Stops after 02:30 AST. Never prints the target.
source ~/loop1/env.sh
H=$(TZ=America/Santo_Domingo date +%H%M); if [ "$H" -ge 0230 ] && [ "$H" -lt 1200 ]; then echo "post skipped: after 02:30"; exit 0; fi
set -a; . ~/loop1/gcal-sync/env; set +a
openclaw message send --channel slack --account "${LIFEOS_ALERT_ACCOUNT:-default}" --target "$LIFEOS_ALERT_TARGET" --message "$1" >/dev/null 2>&1 && echo "posted" || echo "post FAILED"
