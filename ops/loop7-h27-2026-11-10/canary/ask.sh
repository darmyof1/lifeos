#!/usr/bin/env bash
# ask.sh AGENT RUNID PROMPT OUTFILE   (scratch gateway only)
export OPENCLAW_STATE_DIR=$HOME/scratch27/state OPENCLAW_CONFIG_PATH=$HOME/scratch27/state/openclaw.json
set -a; . ~/loop1/openai.env; set +a
timeout 200 openclaw agent --agent "$1" --session-id "$2" --timeout 180 -m "$3" >"$4" 2>&1; echo "exit $?"
