#!/usr/bin/env python3
"""run-cost.py RUN SINCE_UTC [agents...]: sum usage.cost.total of assistant messages in the run's trajectory exports at or after SINCE_UTC (ISO, e.g. 2026-10-27T00:30:00). Read-only. Estimate from the agents' own usage records; the OpenAI usage page is the reference."""
import json,sys
run,since=sys.argv[1],sys.argv[2]; ag=sys.argv[3:] or ['coo','cho','cos','cfo']
base='/home/ubuntu/loop1/evidence/traj/.openclaw/trajectory-exports/'
tot=0;parts=[]
for a in ag:
    try: ev=[json.loads(l) for l in open(f'{base}{run}-{a}/events.jsonl')]
    except OSError: continue
    s=0
    for e in ev:
        if e['type']=='assistant.message' and e['ts']>=since:
            s+=(e['data']['message'].get('usage') or {}).get('cost',{}).get('total',0) or 0
    parts.append(f'{a} {s:.4f}'); tot+=s
print(f'{run}: total {tot:.4f} USD ('+', '.join(parts)+')')
