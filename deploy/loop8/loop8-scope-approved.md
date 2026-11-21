# Loop 8: make growth cheap (scope APPROVED by the CEO, APR-0140, "approved as written")

Why: your question on 2026-11-20 was whether every new topic (dogs, trips, orders, nutrition) and every new chief needs its own design. The advice in research/project-status-and-next-steps-2026-11-20.md was: keep the multi-agent design, but make topics cheap inside each chief and write down what "done" means. Since then P-51 closed the status-question problem in code (send log, COO read tool). Loop 8 is the growth loop. It does not touch routing, the calendar push, the delete gate, the send log or the plugins.

## What Loop 8 delivers
1. A definition of done (a one-page document you approve). Proposed contents: which chiefs must be live (the five today: COO, CoS, CHO, CFO, CLO); a real-request pass rate (proposed 18 of the last 20, Fable's number; today 9 of 12 pass, 1 partial, 2 fail); the privacy conditions for real data (the gate wired in and blocking, kill switch drilled, full restore drilled, identity-access contract accepted: the four preconditions of ops/success-metrics.md, none met yet); and "a new topic needs no handover". Your approval records it as an APR. It tells us when to stop building and start using.
2. One generic topic rule for the three chiefs that keep personal logs (CHO, CFO, CLO), one wording approved once (like the COO status rule): when the CEO starts tracking something new, the chief proposes a simple log (name, columns, one example line) and asks him to confirm; after the confirmation it creates one file for that topic in its own state folder, appends only, gives each entry its run ID and event ID, posts the usual Slack audit line, and never writes to the calendar unless the CEO asked; it keeps the topic list in one index file so it can say what it tracks. The CoS and COO do not get it (the COO routes; the CoS owns the calendar). Health data stays marked high privacy. Each chief's instruction version goes up one step (CHO, CFO, CLO).
3. Proof with synthetic topics first (a test topic in each chief, checked for the file, the columns, append-only, no calendar entry, no existing line changed), then with your real ones: nutrition in the CHO, your dogs in the CLO, e-commerce orders in the CLO or CFO (we decide which chief owns it when you ask), vacations in the CLO. You make those requests in Slack yourself, and I score them in ops/real-request-log.md. No handover or design document per topic: that is the test of the loop.
4. A written chief recipe (design/agent-lifecycle.md, empty today), made from what we did to add the CFO and CLO: Slack app, config, allow-list entry, COO routing rule, health lines, tests. It is a document, not a new chief; a new chief (Family, Career) is built from it when you ask for one, in one handover.
5. A review point. When the real-request log has 20 scored requests, we compare it with the definition of done and revisit P-49 (Fable's single-agent option) with numbers, as you said on 2026-11-14.

## What Loop 8 does not do
- No new chief, no helper bots, no roster trim (the five system chiefs as code is Loop 9).
- No privacy gate wiring (Loop 9), no real Google calendar, no single-agent migration.
- No change to routing, the delete gate, the send log or the plugins.
- P-50 item 2 (thread replies without mention) is decided separately, in parallel; it is small.

## Order and approvals (each live change is its own handover, own APR where an instruction or config changes)
1. Definition of done: I draft, you approve (one APR). No VM work.
2. Topic rule wording: I draft one wording for CHO, CFO and CLO, you approve it (one APR). Scratch test with synthetic topics, then live install (one handover, instruction files and health-check version lines only, one gateway restart).
3. Real topics: you ask in Slack; I score them; any failure becomes a small wording fix.
4. Chief recipe document (repo only).
5. Review at 20 requests.
Expected size: about four handovers, with the same real-data rules as before (no reset, no regression suite, synthetic first, never copy real entries).

## Risks and how they are covered
- Agents inventing inconsistent files: one wording, one index file per chief, a health check line that counts topic files against the index.
- Health data: nutrition would be real health data in a chief whose privacy gate is still only watching. The definition of done lists the gate as a precondition for health data at scale, and you decide whether to start nutrition before it is met.
- Instruction growth: each chief's file gets one rule, written once; the rule replaces narrow wording ("starting with the TV shows") in place.

## Answer (APR-0140)
The CEO approved the scope as written. Step 1 (the definition of done) is drafted in deploy/loop8/definition-of-done-draft.md and waits for his approval.
