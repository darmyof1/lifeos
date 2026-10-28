# Report 9 - Loop 3: parity install, baseline repeats, structure-test design and solo smoke (APR-0097, APR-0098), 2026-10-27

## 1. Parity (Task 1)
- Pulled 4a337a1 (APR-0098). Installed deploy/loop1/health-check.py as ~/loop1/health-check.py (old copy kept as .pre-h9). Output saved to health-check-output.txt (2026-10-27 23:03): PASS 70, WARN 0, FAIL 0, INFO 4. All 16 parity lines PASS (13 plain, 3 with the channel ID filled in).
- Independent check of cos AGENTS.md: repo copy rendered with the staff-cos value, sha256 against the live file: equal. No ID printed.

## 2. Baseline repeats (Task 2), run with ~/loop1/regression-suite.sh, no instruction changed
- loop3-reg-001 (handover 8): 5 pass, 2 fail (bad-sleep -01 checker error P-35 and a duplicate write; overlap -06 no slot offered), 0.0455 USD.
- loop3-reg-002 (22:17 to 22:36): 5 pass, 2 fail, 0.0424 USD.
  1. -01 bad-sleep FAIL: the sessions_send checker failed on SESSION_WORK_START_CHANGED (3 results, P-35); the runner did not run the job (so numstat after, busy event and checker criteria failed).
  2. -03 D2 FAIL (8 of 9): the first line (delete-pending-approval) says requested by COO, not CEO. The deleted line, the seven items, numstat 5 0 and the Google delete all passed.
  3. -02 D1, -04 D3, -05 CFO entry, -06 overlap, -07 privacy: PASS.
- loop3-reg-003 (22:37 to 22:56): 7 of 7 PASS, 0.0428 USD.
- Across three runs: D1, D3, CFO, privacy 3 of 3; bad-sleep 1 of 3 (both failures are the P-35 checker error); D2 2 of 3 (requested by COO once); overlap 2 of 3 (no slot offered once). Per run cost between 0.0014 and 0.0116 USD.
- The busy-event cleanup between runs works (it uses the approval note "CEO handover 9, 2026-10-27" from 003 on; during 002 it still said handover 8, which was my own text).

## 3. Structure test (Task 3)
- Design: ~/handover/structure-test/design.md (six parts: solo agent, state, push job, criteria table, metrics, counted comparison plan with 42 runs, about 0.15 to 0.25 USD).
- Solo agent files: structure-test/solo-agent-files/ (AGENTS.md 8413 bytes, SOUL.md, IDENTITY.md, USER.md), built by compose-solo.py from the repo copies; no Slack ID in them. Sentences I wrote myself: 2 new, 9 adapted live rules (all listed and marked in AGENTS.md with an HTML comment): the "only agent" role sentence; the one-line conflict notice; the CFO grocery rule; "tell the CEO after a calendar entry"; writing-an-entry step 4; the privacy rule keyed on domain; deletes and overlaps (hand-off clauses replaced by the CEO); confirmed reports; the approval request; the final summary. Also IDENTITY.md (new) and SOUL.md (three live sentences joined).
- Criteria dropped for solo (hand-off only): sessions_send checker (bad-sleep, overlap, privacy), "COO names the CHO and the CoS", "the CFO called the CoS itself", requested-by CHO/CFO and the -cho/-cfo event ID names. Each could only make solo look better; the design says to report them separately.
- Config: agent `solo` added to ~/loop1/state/openclaw.json (backup ~/loop1/state/openclaw.json.pre-solo-20261027-2257). Diff of the new entry only: structure-test/config-diff-solo.txt; the other entries and the rest of the config are unchanged. Same model and tool policy as the CoS, send list empty, no binding. Gateway stopped, config applied, gateway started: one process, 4 Slack accounts connected, health check PASS 70.
- Workspace ~/loop1/workspaces/solo (git, seed committed 77bf133); solo push job by hand with --journal and --state-dir ~/loop1/gcal-sync-solo (solo-run.sh).
- Smoke runs (not counted), CLI route to solo:
  1. loop3-solo-smoke-01 bad-sleep: worked in 27 s. health-plan line with loop3-solo-smoke-01-solo-01; journal moved (10-28) and written (10-29), both with privacy=high, requested by CEO, event ID ...-solo-02; numstat 5 0 then 6 0; the job made the 10-29 event busy. Cost 0.0023 USD (8 tool calls, 3 assistant messages, 69 input and 1246 output tokens).
  2. loop3-solo-smoke-02 D1: worked in 29 s. delete-pending-approval then deleted, seed-3, requested by CEO, empty detail (an empty trailing column), numstat 5 0 then 6 0, the job deleted the Google event. Cost 0.0027 USD. The solo reply made no false Google claim.
- Plumbing problems: none stopped a run. Notes: (a) the CoS-style seed text "Only the CoS writes here" stays in the solo journal; (b) the delete lines end with an empty trailing column ("| "), as in some multi-agent runs; (c) solo event IDs read ...-solo-NN.

## For the CEO to decide
1. P-35 keeps failing the bad-sleep checker (2 of 3 baseline runs hit it). Whether it counts as a scenario failure or as a checker rule to relax is yours; the solo variant cannot have it.
2. The D2 "requested by COO" on the pending line (002-03) and the missing slot offer (001-06): two more instruction gaps in the four-agent set. Proposed text only on request.
3. Go for the counted comparison (42 runs, outside 02:30 to 05:10 AST), and an APR for the solo agent entry and the structure-test files.

## End state (23:05 AST)
Gateway active, one process. Cron */5 on the test calendar, GCAL_ALLOW_DELETES=1. Google holds only the three seed events. CoS state at its seed (3 0, seeds pushed); solo workspace at its seed (seeds pushed). The four existing agents are unchanged. Last agent message about 23:03 AST.

## Files in ~/handover/
REPORT-9.md, health-check-output.txt, health-check.py (unchanged since the repo version), regression/ (loop3-reg-001, -002, -003 with the summaries), regression-suite.sh (approval note updated), structure-test/ (design.md, compose-solo.py, solo-agent-files/, add-solo-agent.py, config-diff-solo.txt, solo-run.sh, solo-runs/).
