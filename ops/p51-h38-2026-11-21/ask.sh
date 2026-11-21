id=$1; ag=$2; shift 2; timeout 175 openclaw agent --agent $ag --session-id $id -m "$*" --json > scenarios/$id.json 2>&1; python3 - $id <<'P'
import json,sys
t=open(f"scenarios/{sys.argv[1]}.json").read()
d=json.loads(t[t.index("{"):])
def find(o):
    if isinstance(o,dict):
        if "terminalReply" in o: return o
        for v in o.values():
            r=find(v)
            if r: return r
    if isinstance(o,list):
        for v in o:
            r=find(v)
            if r: return r
r=find(d); x=r["terminalReply"]["text"]
print(sys.argv[1],"TOOLS",r["toolSummary"]["tools"]); print("REPLY:",x)
print("BAD:",[w for w in ["state/",".md",".csv","send-log","memory"] if w in x.lower()])
P
