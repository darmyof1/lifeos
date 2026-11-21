# Health check: the COO tools-policy WARN (DRAFT, waiting for the CEO's decision; nothing is approved here)

Why: since handover 38 the COO has exactly one file tool (read) and no write or edit tool, on purpose (APR-0137). OpenClaw writes a gateway log line on every COO run: "tools policy: profile messaging (agent coo) ... Add alsoAllow write, edit". The health check has a rule (added after the 2026-10-22 incident, when an agent was missing file tools it needed) that turns any such line into WARN. It now counts 120 lines in the last 4000 and shows WARN 1 for a COO that is working as designed. A permanent WARN trains you to ignore warnings, which is the wrong habit for a check you rely on.

## Option A (recommended): the rule ignores lines about agent coo only
Change deploy/loop1/health-check.py so the "tools policy: profile" rule skips lines that name "agent coo", and still counts lines for any other agent (CHO, CoS, CFO, CLO, solo), so the 2026-10-22 failure is still caught for the chiefs that need write tools. Add a test: a COO line gives no WARN, a CFO line still gives WARN. Live change: the installed health-check.py replaced with the repo copy (backup first, sha256 equal). No config, agent, plugin or crontab change; no gateway restart.

## Option B: accept the WARN
Nothing changes. Health shows PASS 88, WARN 1 for as long as the COO has a read tool. Not recommended.

## Option C: give the COO write and edit tools too
Not recommended. It would remove the read-only limit you approved in APR-0137.

## Question
Reply A, B or C. Approval would be recorded as the next APR in your words; the change is small and goes with the next handover (or a one-step handover of its own).
