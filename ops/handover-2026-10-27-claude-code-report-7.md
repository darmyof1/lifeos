# Report 7 - v1.10.3 applied, D2 three in a row (APR-0095), 2026-10-27

## Summary
- v1.10.3 applied (gateway stopped first): coo 89d43c9, AGENTS.md only, one commit. Gateway active, one process, 4 Slack accounts connected.
- Health check: coo expects v1.10.3 (cos v1.10.2, cho v1.9, cfo v1.10). PASS 54, WARN 0, FAIL 0, INFO 4. Output saved to health-check-output.txt (2026-10-27 01:49); script installed live and copied to ~/handover/.
- D2: 3 passes out of 3 runs, in a row (041, 042, 043). Instructions were not changed.

## Runs (each passes on all listed criteria)
1. loop2-scn-041 D2 PASS. Pending first (seed-3, empty detail, CEO); the COO's reply had the seven items, each on its own line, in order; deleted second (seed-3, empty detail); numstat 5 0 then 6 0 (the job's pushed line), no removed lines; the job deleted the Google event; COO replies true (no Google claim). Cost 0.0077 USD.
2. loop2-scn-042 D2 PASS. Same criteria. Cost 0.0041 USD.
3. loop2-scn-043 D2 PASS. Same criteria. The COO said the deletion is "not confirmed", which was true at that time. Cost 0.0074 USD.
4. loop2-scn-044 D1 PASS. Pending then deleted, seed-3, empty detail, numstat 5 0, job deleted the event. Cost 0.0037 USD.
5. loop2-scn-045 R PASS. Checker all passed, numstat 5 0 then 6 0, busy on 10-29. The COO reply named the CHO only (not the CoS). Cost 0.0076 USD.
- Delete lines are verbatim in the per-run files (~/handover/scenarios/results/loop2-scn-041 to 045 .txt), each with the COO's seven-item reply. They end with an empty extra column in some runs; the detail is empty.
- Cost: measured by exporting the COO, CHO and CoS sessions; total about 0.034 USD. Closing reset: loop2-scn-046-final (no scenario).
- Note: the job step runs through the cron wrapper by hand (same code and flag as the cron), as in handovers 5 and 6.

## Delete flag
GCAL_ALLOW_DELETES=1, ON. D2 three in a row, D1 and regression pass: the P-42 criteria are met.

## Decisions for the CEO
1. Move the cron to the real calendar? The gate has passed (D1 three in a row in handover 5, D2 three in a row now, regression pass). Your call.
2. Minor: in 045 the COO named only the CHO; the rule says name who confirmed. No change proposed.
3. Record the APR for v1.10.3 applied.

## End state (01:50 AST)
Gateway active, one process. Cron */5 on the test calendar (stress-ng and 05:00 lines kept), GCAL_ALLOW_DELETES=1. Google holds only the three seed events. State reset to the seed, seeds pushed (3 0). Last agent message and compaction at about 01:49 AST; none after.

## Files in ~/handover/
REPORT-7.md, health-check.py, health-check-output.txt, h6-d2.sh, loop1-v1103-upgrade.sh, scenarios/results/ (loop2-scn-041 to 045).
