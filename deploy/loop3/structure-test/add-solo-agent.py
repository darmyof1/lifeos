#!/usr/bin/env python3
"""add-solo-agent.py [--apply] - adds the `solo` agent to ~/loop1/state/openclaw.json (backup first). Dry run by default: prints the new entry only."""
import json, os, shutil, sys, time
f = os.path.expanduser("~/loop1/state/openclaw.json")
c = json.load(open(f))
cos = c["agents"]["entries"]["cos"]
new = {"name": "solo", "workspace": os.path.expanduser("~/loop1/workspaces/solo"), "agentDir": os.path.expanduser("~/loop1/state/agents/solo/agent"),
       "identity": {"name": "Solo", "emoji": ":jigsaw:"}, "model": cos["model"],
       "tools": {"agentToAgent": {"send": []}, "fs": dict(cos["tools"]["fs"]), "alsoAllow": list(cos["tools"]["alsoAllow"])}}
assert "solo" not in c["agents"]["entries"], "solo already present"
print("new entry agents.entries.solo:"); print(json.dumps(new, indent=2))
if "--apply" in sys.argv:
    b = f + ".pre-solo-" + time.strftime("%Y%m%d-%H%M"); shutil.copy2(f, b); print("backup:", b)
    c["agents"]["entries"]["solo"] = new
    json.dump(c, open(f, "w"), indent=2); open(f, "a").write("\n")
    print("applied")
