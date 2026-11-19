# Real-request log (informal scoring, from 2026-11-14)

Status: a working note. NOT a decision and NOT the adopted metrics (those stay in ops/success-metrics.md, synthetic regression suites). It keeps the scores of the CEO's real Slack requests so the P-49 question (keep five agents or test a single-agent version) can be answered with real results later. Request text is described in general terms only: no personal details, amounts, vehicle or account details, no IDs (the repo is public, APR-0114).

## How a request is scored
- pass: the right agent got it and the right state exists afterwards, with no CEO action beyond the request itself.
- partial: the work was done but something was wrong or missing (wrong detail, a follow-up needed).
- fail: wrong agent, nothing written, or a wrong answer.
- "reported" means the agents said it; "checked" means a read-only look at the files or calendar confirmed it.

## Log
| # | Date, time (AST) | Request (general) | Kind | Route | Result | Note |
|---|---|---|---|---|---|---|
| 1 | 2026-11-14 05:50 | Log a TV show he started | log | COO to CLO | pass (reported) | Run ID was a stray word (fixed by handover 32) |
| 2 | 2026-11-14 10:28 | Log a show start for today and ask where the log can be seen | log + question | COO to CLO | pass (reported) | Run ID was an odd word (fixed by handover 32); the answer named a workspace path the CEO cannot open |
| 3 | 2026-11-14 17:38 | Lifestyle request, no run ID | log | COO to CLO | pass (checked) | Run ID coo-20261114-1738 matched the time |
| 4 | 2026-11-15 14:11 | Start a vehicle maintenance log; show the file, path and process | log + explain | CLO direct | pass (reported) | One CSV log created |
| 5 | 2026-11-15 14:14 | Why CSV and not Markdown | question | CLO direct | pass | |
| 6 | 2026-11-15 15:10 | Review a richer column list and update the log | change | CLO direct | pass (reported) | CLO split it into a services file, a parts file and a schema note; earlier entry kept; one column left blank until its meaning is clear |
| 7 | 2026-11-15 15:19 | Log a second maintenance item; have the CFO log the purchase; a calendar reminder for a 45-day credit | compound | CLO to COO to CFO, CoS | pass (checked 2026-11-16) | The CFO purchase entry exists (its own date field is the purchase date, written 2026-11-15 15:21); the all-day event exists on the TEST calendar on the right date; routing and date arithmetic correct. Open: the CLO left the currency blank; the reminder is on the TEST calendar |
| 8 | 2026-11-15 15:24 | Ask the COO what the CEO last told the CLO | question | COO | fail | Cause found (read-only check 2026-11-16): the CLO's purchase reached the COO's main session (agent:coo:main) and was relayed to the CFO there, but the CEO's question was answered in the COO's Slack channel session, which had not seen it. Two sessions, no shared memory between them |
| 9 | 2026-11-17 17:12 | Ask the COO what the CEO last told the CFO (after COO v1.10.10) | question | COO, CFO | fail | The COO asked the CFO, named it and gave a run ID, no path, but the CFO answered from its main session, which does not hold what the CEO typed in the CFO's own Slack channel; the answer was wrong for the CEO. Same two-session problem one layer down (handover 33) |
| 10 | 2026-11-19 15:56 | Ask the COO what the CEO last told the CFO (after COO v1.10.11) | question | COO, CFO | pass (limited) | The COO asked the CFO, named it, gave a run ID, no path or file name, and named the last entry of the CFO file. That entry was a synthetic test item by then, so the older real item was not tested. A synthetic item typed directly to the CFO was found in a fresh COO session (handover 34, test 5) |

## Count so far
10 requests: pass 8 (rows 1 to 7 and 10), fail 2 (rows 8 and 9). About 20 requests would be a fair read.

## Follow-ups seen
- Row 10: v1.10.11 is live and the direct-to-agent case passes in a synthetic test. Ask the question again about a real item the CEO typed in an agent's own channel to settle it.
- WirePusher: the CEO confirmed on 2026-11-19 that the phone notification works.
- Row 9: a second wording (COO v1.10.11, ask the agent to read its own state files) is drafted in deploy/after-loop7/coo-status-wording-v11011-draft.md and waits for the CEO. The code-written routing log (P-51) is the deterministic fix.
- Row 7: the CEO tells the CLO and CFO the currency once (not yet given).
- Row 8: the failure is a design effect, not a one-off: a request that comes in through an agent-to-agent route lands in the COO's main session, while the CEO talks to the COO in a Slack channel session. Options for the CEO to weigh later (each agent-behavior change needs its own APR with the exact wording): leave it and ask the CLO, CFO or CoS directly; or give the COO a small shared note of routed items that it reads before it answers "what did I tell X". This is the kind of boundary problem the architecture review (P-49) describes. No decision.
- Backup check: the weekly backup ran on 2026-11-15 at 06:15 AST (archive of 312 files, 4 of at most 4 kept in the folder).
- Precondition note: ops/success-metrics.md lists four preconditions before real data (gate wired into every model call, kill switch drilled, full restore drilled, identity-access contract accepted). The gate is not wired yet, so real data is outside that rule today; the CEO knows.
