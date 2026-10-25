You are working alone overnight in a sandbox on the LifeOS repo. The CEO is asleep and will not answer. Work until 09:00 AST, then stop.

Where you are
- Linux user "sandbox", no sudo. Your clone: ~/lifeos-sandbox, branch sandbox/agy-2026-10-25. You cannot push and must not try.
- Read-only inputs in /srv/sandbox-input: openclaw-dist (the OpenClaw 2026.10.5 code); health-check.py, health-check.patch and REPORT-HEALTHCHECK-UPDATE.md (the Loop 1 health-check update made on the VM).
- Start by reading deploy/loop1/STATE.md, deploy/loop1/LOOP1-CLOSE-RECORD.md, decisions/PENDING.md, and decisions/APPROVALS.md from APR-0052 on.

Hard limits
- Loop 1 is closed (APR-0071). Do not start OpenClaw, the gateway or any agent. Do not use Slack, OpenAI or any API key. Do not try to read the main account home folder.
- Do not edit decisions/APPROVALS.md or decisions/PENDING.md. Do not write "approved", "closed" or "confirmed" about anything the CEO has not decided.
- No real personal data. Synthetic examples only.
- Work only inside ~/lifeos-sandbox. pip install --user is fine; nothing that needs sudo.

When something needs a CEO decision
- Do not wait. Make the choice yourself and record it in sandbox/SANDBOX-DECISIONS.md as SD-001, SD-002 and so on: the question, the options, your choice, why, and the line "Needs CEO: yes". Then carry on as if that choice were made. These are proposals, not decisions.

Logging
- sandbox/WORKLOG.md: one entry per step with the time, what you did, the exact command, a short result, and any problem.
- Every claim in your drafts says how you checked it (file and line, or command and output), or says "not verified".
- Commit to your branch after each task with a clear message.

Tasks, in order
1. Health check: bring the VM update into deploy/loop1/health-check.py using /srv/sandbox-input. Run python3 -m py_compile on it. Run it offline if it can run without the Loop 1 files, and say what could not be run.
2. P-37: in /srv/sandbox-input/openclaw-dist, find where "SQLite automatic maintenance activity changed before age consumption" and "slow agent database reservation" come from. Explain when they happen and whether they retry. Write sandbox/P-37-findings.md. Code reading only.
3. P-31: draft a cost hard-stop design in sandbox/P-31-cost-hard-stop.md: how spend is read, the threshold, what gets stopped, and how it is tested. Respect APR-0056.
4. P-28: draft the calendar journal to Google Calendar design in sandbox/P-28-calendar-sync.md, keeping the journal append-only (APR-0054, APR-0057).
5. P-32: draft the Loop 2 memory design in sandbox/P-32-memory.md, including the run 014 finding that agent memory survives a state reset.

At the end
- Write sandbox/SUMMARY.md: each task as done, partial or not started; what you verified and what you assumed; the SD list; where you got stuck.
- Stop at 09:00 even if tasks remain.
