snap () 
{ 
    export OPENCLAW_STATE_DIR=$HOME/scratch29/state OPENCLAW_CONFIG_PATH=$HOME/scratch29/state/openclaw.json;
    openclaw sessions --all-agents --json 2>&1 | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in sorted(d['sessions'],key=lambda s:s['key']):
    print(s['key'].split('test29')[0], s.get('sessionId','?')[:8],'started',s.get('sessionStartedAt'),'updated',s.get('updatedAt'))
"
}
