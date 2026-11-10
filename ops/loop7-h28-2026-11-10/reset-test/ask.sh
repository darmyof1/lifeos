#!/usr/bin/env bash
# ask.sh GATEWAY(g1|g2) AGENT SESSIONKEY RUNTAG OUTFILE  - scratch gateways only; ends with the exit code
export OPENCLAW_STATE_DIR=$HOME/scratch28/$1/state OPENCLAW_CONFIG_PATH=$HOME/scratch28/$1/state/openclaw.json
set -a; . ~/loop1/openai.env; set +a
timeout 150 openclaw agent --agent "$2" --session-key "$3" --timeout 120 -m "Scratch reset test $4. Reply with the single word OK." >"$5" 2>&1; echo "exit $?" >>"$5"
