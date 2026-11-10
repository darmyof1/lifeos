#!/usr/bin/env bash
# ask.sh ROUTE TAG OUTFILE   routes: direct-p1 direct-q1 send-p2 send-q2   (scratch gateway only, never the live one)
export OPENCLAW_STATE_DIR=$HOME/scratch29/state OPENCLAW_CONFIG_PATH=$HOME/scratch29/state/openclaw.json
set -a; . ~/loop1/openai.env; set +a
case "$1" in
 direct-p1) A=p1; K=agent:p1:main; M="Scratch reset test $2. Reply with the single word OK." ;;
 direct-q1) A=q1; K=agent:q1:slack:channel:test29q1; M="Scratch reset test $2. Reply with the single word OK." ;;
 send-p2) A=r; K=agent:r:main; M="Scratch reset test $2. Use the sessions_send tool once with sessionKey agent:p2:main, mode followup, timeoutSeconds 60 and message: Scratch reset test $2, reply OK. Then tell me what came back in one line." ;;
 send-q2) A=r; K=agent:r:main; M="Scratch reset test $2. Use the sessions_send tool once with sessionKey agent:q2:slack:channel:test29q2, mode followup, timeoutSeconds 60 and message: Scratch reset test $2, reply OK. Then tell me what came back in one line." ;;
esac
timeout 170 openclaw agent --agent "$A" --session-key "$K" --timeout 150 -m "$M" >"$3" 2>&1; echo "exit $?" >>"$3"
