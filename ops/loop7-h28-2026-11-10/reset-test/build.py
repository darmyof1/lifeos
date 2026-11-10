import json,os,secrets,sys
H=os.path.expanduser("~")
live=json.load(open(H+"/loop1/state/openclaw.json"))
base=json.load(open(H+"/handover/h27/canary/scratch-config-sanitized.json"))
def make(name,port,variant):
    d=f"{H}/scratch28/{name}"; os.makedirs(d+"/state",exist_ok=True)
    c=json.loads(json.dumps(base))
    c["gateway"]={"mode":"local","port":port,"bind":"loopback","auth":{"mode":"token","token":secrets.token_hex(24)}}
    ents={"main":{"workspace":f"{d}/ws-main","agentDir":f"{d}/state/agents/main/agent"}}
    for a in ("p","q"):
        ents[a]={"name":"reset-"+a,"workspace":f"{d}/ws-{a}","agentDir":f"{d}/state/agents/{a}/agent","model":"openai/gpt-6-luna",
                 "tools":{"fs":{"workspaceOnly":True},"alsoAllow":["read","write","edit"]}}
        os.makedirs(f"{d}/ws-{a}",exist_ok=True)
    os.makedirs(f"{d}/ws-main",exist_ok=True)
    c["agents"]["entries"]=ents
    sess=json.loads(json.dumps(live["session"])) if variant=="live" else {}
    sess.setdefault("reset",{})
    sess["reset"]["mode"]="daily"; sess["reset"]["atHour"]=3
    c["session"]=sess
    if variant=="live":
        c["tools"]=json.loads(json.dumps(live["tools"])); c["tools"]["agentToAgent"]={"enabled":False,"allow":[]}
    json.dump(c,open(d+"/state/openclaw.json","w"),indent=1)
make("g1",19928,"plain"); make("g2",19929,"live")
