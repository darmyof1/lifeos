#!/usr/bin/env bash
# gw.sh <name> <port> start|stop|term|ask <agent> <sid> <msg>
N="$1"; PORT="$2"; ACT="$3"; S=$HOME/scratch37-$N
export OPENCLAW_STATE_DIR=$S/gw OPENCLAW_CONFIG_PATH=$S/gw/openclaw.json OPENCLAW_GATEWAY_PORT=$PORT
set -a; . ~/loop1/openai.env; set +a
export HOME_REAL=$HOME
case "$ACT" in
  start) s=$(date +%s.%N); HOME=$S/home nohup openclaw gateway run --port $PORT > $S/gw.log 2>&1 & echo $! > $S/gw.pid
         until grep -q "http server listening" $S/gw.log 2>/dev/null; do sleep 0.5; done; e=$(date +%s.%N); python3 -c "print('startup %.1f s'%($e-$s))" | tee $S/startup.txt;;
  stop|term) for p in $(pgrep -f "^openclaw-gateway$"); do if tr '\0' '\n' < /proc/$p/environ 2>/dev/null | grep -q "^OPENCLAW_STATE_DIR=$S/gw$"; then kill -TERM $p; fi; done;;
  ask) A="$4"; R="$5"; M="$6"; O="$HOME/handover/h41/scenarios-scratch"; mkdir -p $O; [ ! -e "$O/$R.txt" ] || { echo used; exit 1; }
       HOME=$S/home timeout 295 openclaw agent --agent "$A" --session-id "$R" --timeout 285 -m "$M" > "$O/$R.txt" 2>&1; echo rc=$?;;
esac
