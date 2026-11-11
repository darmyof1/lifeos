#!/usr/bin/env bash
# ask.sh AGENT RUNID "CEO message" OUTDIR : one CLI-route message (the route the earlier scenarios use), raw reply saved. Synthetic data only.
source ~/loop1/env.sh
A="$1"; R="$2"; M="$3"; O="$4"
H=$(TZ=America/Santo_Domingo date +%H%M); if [ "$H" -ge 0230 ] && [ "$H" -lt 0510 ]; then echo "refused: inside 02:30 to 05:10"; exit 1; fi
[ ! -e "$O/$R.txt" ] || { echo "run ID $R already used"; exit 1; }
T0=$(date -u +%Y-%m-%dT%H:%M:%S)
{ echo "# run $R, agent $A, started $(date -Is)"; echo "# message: $M"; echo "---- reply ----"; } > "$O/$R.txt"
timeout 295 openclaw agent --agent "$A" --session-id "$R" --timeout 285 -m "Loop 7 scenario run, run ID $R. I am the CEO. $M" >> "$O/$R.txt" 2>&1
echo "---- end (rc=$?, $(date -Is)) ----" >> "$O/$R.txt"
cat "$O/$R.txt"
