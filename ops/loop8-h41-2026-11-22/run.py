#!/usr/bin/env python3
"""run.py <scratch|live> <agent> <session-id> <message> <outfile or -> : one explicit-session CLI run; prints tools, cost, reply."""
import json,os,subprocess,sys
mode,agent,sid,msg,out=sys.argv[1:6]
env=dict(os.environ)
home=os.path.expanduser("~")
def load(p):
    for l in open(p):
        l=l.strip()
        if l.startswith("export "): l=l[7:]
        if "=" in l and not l.startswith("#"):
            k,v=l.split("=",1); env[k]=v.strip('"').strip("'")
load(home+"/loop1/env.sh"); load(home+"/loop1/openai.env")
if mode=="scratch":
    S=home+"/scratch37-41"
    env.update(OPENCLAW_STATE_DIR=S+"/gw",OPENCLAW_CONFIG_PATH=S+"/gw/openclaw.json",OPENCLAW_GATEWAY_PORT="18941",HOME=S+"/home")
if os.path.exists(out) and out!="-": print("used"); sys.exit(1)
r=subprocess.run(["openclaw","agent","--agent",agent,"--session-id",sid,"--timeout","285","-m",msg,"--json"],env=env,capture_output=True,text=True,timeout=295)
t=r.stdout
try: d=json.loads(t[t.index("{"):])
except Exception: print("rc",r.returncode,"unparsed",t[-300:],r.stderr[-300:]); sys.exit(2)
def find(o,k):
    if isinstance(o,dict):
        if k in o: return o
        for v in o.values():
            x=find(v,k)
            if x: return x
    if isinstance(o,list):
        for v in o:
            x=find(v,k)
            if x: return x
a=find(d,"terminalReply") or {}
u=(find(d,"agentMeta") or {}).get("agentMeta",{}).get("usage",{})
reply=a.get("terminalReply",{}).get("text","")
tools=a.get("toolSummary",{}).get("tools")
cost=u.get("cost",{}).get("total")
print("TOOLS",tools,"COST",cost,"TOKENS",u.get("total"))
print("REPLY:",reply)
if out!="-":
    open(out,"w").write(json.dumps({"agent":agent,"session":"<sid>","message":msg,"tools":tools,"cost_usd":cost,"tokens":u.get("total"),"reply":reply},indent=1))
