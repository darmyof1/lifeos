# Loop 8, step 3: the domain split and the CFO savings case (DRAFT, waits for the CEO)

Why: handover 41 (ops/handover-2026-11-22-claude-code-report-41.md) showed the topic rule works for the normal case, but in all three chiefs the "another chief's domain" test failed: the chief proposed a file instead of naming the right chief (the CLO proposed a sleep file, the CHO a vacation file, the CFO a houseplants file; in scratch the CHO named the wrong chief). Cause: no chief's instructions say who holds what, and the CLO scope is now wide. The CFO also treated a "gift fund" as an investments entry, asked for a balance and never proposed a file.

## Part A. The domain rule (the same wording in the CHO, CFO and CLO; one new last rule each, all other rules kept)
"- Domains (instruction set <version>): who holds what. CHO: sleep, workouts, nutrition, supplements and other health. CFO: budgets, spending, investments, savings and money set aside. CLO: everything else personal: TV shows, travel and trips, hobbies, pets, home projects, vehicles, e-commerce orders. CoS: the calendar. Before you propose a file for a new topic, decide which of these holds it. If it is not yours, answer in one sentence that names the chief (for example: That belongs to the CLO.), propose nothing, create no file and write nothing. If the request has two parts, keep your own part and say which part goes to the other chief through the COO, as today."

Versions: CHO v1.10 becomes v1.11; CFO v1.12 becomes v1.13; CLO v1.2 becomes v1.3. The CoS and COO files do not change. Nothing else in any file changes.

## Part B. The CFO savings case (CFO only, one more sentence inside the same new rule)
"Money the CEO sets aside for a purpose (a gift fund, a trip fund) is a saving, not an investment: treat it as a new topic under the New topics rule (file state/<topic>.md, columns date, what, amount, running balance, run ID, event ID). The investments file is only for invested funds with contributions and growth."

Option A (recommended): add this sentence. A cash saving gets its own file; the investments file stays as it is.
Option B: do not add it; a gift fund then stays in the investments file, and the chief must still propose and create it (the test showed it did neither).

## What this does not change
The approved topic rule, the investments rule, the privacy rules, calendar rules and the roster. The nutrition path is unchanged: a diet or meal plan change still goes through the COO to the CFO for the grocery budget line.

## How it will be installed and tested (handover 43, after approval)
1. Repo: the new rule in the three agent files, the version markers, one upgrade script (same pattern as loop8-topic-rule-upgrade.sh: dry run, refuses on the wrong version, inserts once, gateway stopped, commit of the three AGENTS.md only), health version lines, tests.
2. Scratch gateway first, synthetic topics only: the other-chief test for all three chiefs in both directions (for example the CHO asked for houseplants, the CLO asked for sleep, the CFO asked for a pet), a CFO test-gift-fund, and the earlier normal-case checks again. No instruction is changed to make a run pass.
3. Live, one restart, after a pass in scratch; the same checks live, synthetic only. Then you ask for your real topics (nutrition, dogs, orders, trips) and I score them in ops/real-request-log.md.
4. Rollback by git revert in each workspace.

## What I need from you
"approved as written" (with Option A or B for Part B), or your changes.
