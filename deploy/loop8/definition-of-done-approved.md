# Loop 8, step 1: definition of done (APPROVED by the CEO, APR-0141, "approved as written")

Purpose: say in advance what "the build is complete" means, so we know when to stop building and start using. When every line below is true, LifeOS is done; later work is ordinary use and tuning, not a new loop. Today's value is shown for each line so the gap is visible. Where a line needs a number, it is a proposal for you to change.

## A. Scope: which agents must work
- The five live chiefs (COO, CoS, CHO, CFO, CLO) answer in their own Slack channels and route correctly through the COO. Today: true.
- A new topic inside a chief needs no handover (the Loop 8 topic rule). Today: not true yet.
- A new chief takes one handover, from the written recipe. Today: about two handovers and no recipe.

## B. Quality: real use
- At least 18 of the last 20 real requests (typed by you in Slack, scored in ops/real-request-log.md) pass. Today: 12 scored, 9 pass, 1 partial, 2 fail (the 2 failures are fixed since; the log keeps them).
- Every failure in those 20 has a recorded cause and a fix or an accepted limit. Today: true for all scored so far.
- Zero wrong deletes (a calendar event removed without your approval), always. Today: 0 since the delete gate (APR-0101).
- Status questions ("what did I last tell the X?") answer correctly for items typed directly in an agent's channel. Today: true since COO v1.10.12 and the send log (row 12 of the log).

## C. Safety: before real data is treated as protected
These are the four preconditions already written in ops/success-metrics.md. You already use real data, knowing they are not met; "done" means they are.
1. The privacy gate is wired into the path of every model call and blocks, not only watches. Today: wired in shadow mode only (it logs, it blocks nothing).
2. The kill switch has been drilled. Today: drilled once, on 2026-11-01; a second drill after the plugins added since is proposed.
3. A full-state restore has been drilled, not only config and workspaces. Today: not recorded as done in the repo log (weekly encrypted backups run; the last full-restore drill I can find was config and workspaces only).
4. You have accepted the identity-and-access contract (design/identity-and-access.md). Today: draft, not accepted.

## D. Operations
- The health check shows no FAIL and no unexplained WARN. Today: PASS 89, WARN 0, FAIL 0.
- A weekly encrypted backup ran in the last 7 days and the last four are kept. Today: true (last verified 2026-11-15; the check is in the health report).
- Cost stays under 0.05 USD per run and 1 USD per day. Today: about 0.003 to 0.01 USD per run.
- All changes to instructions, config and code are recorded as an APR and a numbered handover. Today: true.

## E. When done
- We stop opening loops. You use LifeOS daily.
- A short monthly review reads the health report, the request log (pass rate over the last 20) and the pending list, and decides what, if anything, to change. Any change is its own APR.
- P-49 (Fable's single-agent option) is reviewed once, at the first review after 20 scored requests, with the numbers from the log, as you decided on 2026-11-14.

## What is not in this definition (on purpose)
New chiefs you have not asked for, the 17 helper bots, a real Google calendar, and trimming the five system chiefs into code. They are separate decisions, not part of "done".

## Answer (APR-0141)
The CEO approved the definition of done as written.
