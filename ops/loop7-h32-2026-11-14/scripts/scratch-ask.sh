#!/usr/bin/env bash
# bare message to the SCRATCH gateway: scratch-ask.sh <agent> <session-id> <message> <outdir>
export OPENCLAW_STATE_DIR=$HOME/scratch32/gw OPENCLAW_CONFIG_PATH=$HOME/scratch32/gw/openclaw.json OPENCLAW_GATEWAY_PORT=19933
set -a; . ~/loop1/openai.env; set +a
A="$1"; R="$2"; M="$3"; O="$4"
H=$(TZ=America/Puerto_Rico date +%H%M); if [ "$H" -ge 0230 ] && [ "$H" -lt 0510 ]; then echo "refused: inside 02:30 to 05:10"; exit 1; fi
[ ! -e "$O/$R.txt" ] || { echo "session $R already used"; exit 1; }
{ echo "# session $R, agent $A, sent $(TZ=America/Puerto_Rico date '+%F %T AST')"; echo "# command: openclaw agent --agent $A --session-id $R --timeout 285 -m \"$M\""; echo "---- reply ----"; } > "$O/$R.txt"
timeout 295 openclaw agent --agent "$A" --session-id "$R" --timeout 285 -m "$M" >> "$O/$R.txt" 2>&1
echo "---- end (rc=$?, vm clock $(TZ=America/Puerto_Rico date '+%F %T AST')) ----" >> "$O/$R.txt"
cat "$O/$R.txt"
