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
| 7 | 2026-11-15 15:19 | Log a second maintenance item; have the CFO log the purchase; a calendar reminder for a 45-day credit | compound | CLO to COO to CFO, CoS | partial (reported) | Routing and date arithmetic correct; currency left blank by the CLO; the CFO log and the calendar entry not yet checked; the reminder is on the TEST calendar |
| 8 | 2026-11-15 15:24 | Ask the COO what the CEO last told the CLO | question | COO | fail | The COO did not mention the item the CLO said it routed through the COO and quoted an older entry; the COO cannot see direct messages by design |

## Count so far
8 requests: pass 6 (rows 1 to 6), partial 1 (row 7), fail 1 (row 8). About 20 requests would be a fair read.

## Follow-ups seen
- Row 7: read-only check that the CFO entry and the calendar entry exist (counts only, no values); the CEO tells the CLO and CFO the currency once.
- Row 8: ask Claude Code to read the COO trace and say whether the routed item reached the COO channel session or only an agent-to-agent session.
- Precondition note: ops/success-metrics.md lists four preconditions before real data (gate wired into every model call, kill switch drilled, full restore drilled, identity-access contract accepted). The gate is not wired yet, so real data is outside that rule today; the CEO knows.
