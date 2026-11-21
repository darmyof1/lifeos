#!/usr/bin/env bash
# mk-scratch.sh <name> <port> <plugin 0|1> <cooread 0|1>  : builds ~/scratch37-<name> (own state, own HOME, header-only state files, no Slack)
set -e
N="$1"; PORT="$2"; PL="$3"; CR="$4"; S=$HOME/scratch37-$N
rm -rf "$S"; mkdir -p "$S/gw/extensions" "$S/ws" "$S/home/loop1"
ln -s "$S/ws" "$S/home/loop1/workspaces"
python3 - "$S" "$PORT" "$PL" "$CR" <<'PY'
import json, os, shutil, sys
S, PORT, PL, CR = sys.argv[1], int(sys.argv[2]), sys.argv[3] == "1", sys.argv[4] == "1"
H = os.path.expanduser("~")
c = json.load(open(H + "/loop1/state/openclaw.json"))
c.pop("channels", None); c.pop("bindings", None)
c["gateway"]["port"] = PORT
c["gateway"]["auth"]["token"] = "scratch37-" + os.urandom(6).hex()
for k, v in c["agents"]["entries"].items():
    old = v["workspace"]
    new = old.replace(H + "/loop1/workspaces", S + "/ws").replace(H + "/loop1/state/workspace", S + "/ws/main")
    v["workspace"] = new
    if "agentDir" in v:
        v["agentDir"] = S + "/gw/agents/" + k + "/agent"; os.makedirs(v["agentDir"], exist_ok=True)
    if not os.path.isdir(new):
        if os.path.isdir(old): shutil.copytree(old, new, ignore=shutil.ignore_patterns(".git", "state"))
        else: os.makedirs(new)
    st = old + "/state"
    os.makedirs(new + "/state", exist_ok=True)
    if os.path.isdir(st):
        for f in os.listdir(st):
            if f.startswith("send-log-"): continue
            with open(st + "/" + f, encoding="utf-8") as fh: first = fh.readline()
            open(new + "/state/" + f, "w").write(first if first.startswith("#") else "# state\n")
if CR:
    t = c["agents"]["entries"]["coo"].setdefault("tools", {})
    t["alsoAllow"] = ["read"]; t["fs"] = {"workspaceOnly": True}
c["plugins"]["entries"] = {k: v for k, v in c["plugins"]["entries"].items() if k not in ("ceo-ledger", "gate-plugin", "slack")}
if PL:
    c["plugins"]["entries"]["send-log"] = {"enabled": True}
    d = S + "/gw/extensions/send-log"; os.makedirs(d + "/node_modules")
    src = H + "/work37/deploy/after-loop7/send-log-plugin"
    for f in ("index.js", "log.js", "openclaw.plugin.json", "package.json"): shutil.copy(src + "/" + f, d + "/" + f)
    os.symlink(H + "/.npm-global/lib/node_modules/openclaw", d + "/node_modules/openclaw")
json.dump(c, open(S + "/gw/openclaw.json", "w"), indent=1)
PY
