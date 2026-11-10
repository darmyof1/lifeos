#!/usr/bin/env bash
# chat.sh TAG OUTFILE - simulated inbound message through the scratch gateway's own chat.send (webchat), channel-style key for agent q3
export OPENCLAW_STATE_DIR=$HOME/scratch29/state OPENCLAW_CONFIG_PATH=$HOME/scratch29/state/openclaw.json
set -a; . ~/loop1/openai.env; set +a
TOK=$(python3 -c "import json,os;print(json.load(open(os.environ['OPENCLAW_CONFIG_PATH']))['gateway']['auth']['token'])")
openclaw gateway call chat.send --port 19930 --token "$TOK" --expect-final --timeout 120000 --json --params "{\"sessionKey\":\"agent:q3:slack:channel:test29q3\",\"message\":\"Scratch reset test $1. Reply with the single word OK.\",\"idempotencyKey\":\"$1\"}" >"$2" 2>&1; echo "exit $?" >>"$2"
