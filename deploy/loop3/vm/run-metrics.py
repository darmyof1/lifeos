#!/usr/bin/env python3
"""run-metrics.py RUN SINCE_UTC AGENT[:EXPORT_SUFFIX]... - per-run metrics from the trajectory exports (structure test, APR-0099).
Prints one JSON object: per agent input/output/cacheRead/cacheWrite tokens, cost, turns (assistant messages), tool calls, first-turn prompt tokens,
instruction-file bytes (the agent's four live files); and totals. Only events at or after SINCE_UTC count."""
import json, os, sys
run, since = sys.argv[1:3]; ags = sys.argv[3:]
base = os.path.expanduser("~/loop1/evidence/traj/.openclaw/trajectory-exports/")
res = {}; tot = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "cost": 0.0, "turns": 0, "tool_calls": 0, "first_turn_tokens": 0, "instr_bytes": 0}
for spec in ags:
    a = spec.split(":")[0]
    try: ev = [json.loads(l) for l in open(base + "%s-%s/events.jsonl" % (run, a))]
    except OSError: continue
    d = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "cost": 0.0, "turns": 0, "tool_calls": 0, "first_turn_tokens": 0}
    first = True
    for e in ev:
        if e["ts"] < since: continue
        if e["type"] == "tool.call": d["tool_calls"] += 1
        if e["type"] == "assistant.message":
            u = e["data"]["message"].get("usage") or {}
            d["turns"] += 1
            for k in ("input", "output", "cacheRead", "cacheWrite"): d[k] += u.get(k, 0) or 0
            d["cost"] += (u.get("cost") or {}).get("total", 0) or 0
            if first: d["first_turn_tokens"] = (u.get("contextUsage") or {}).get("promptTokens", 0) or 0; first = False
    ws = os.path.expanduser("~/loop1/workspaces/%s/" % a)
    d["instr_bytes"] = sum(os.path.getsize(ws + f) for f in ("AGENTS.md", "SOUL.md", "IDENTITY.md", "USER.md") if os.path.exists(ws + f))
    d["cost"] = round(d["cost"], 5); res[a] = d
    for k in tot: tot[k] += d[k]
tot["cost"] = round(tot["cost"], 5)
print(json.dumps({"run": run, "agents": res, "total": tot}))
