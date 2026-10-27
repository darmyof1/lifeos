# Report 5 - v1.10.1 applied and re-runs (APR-0093), 2026-10-26

## Summary
- v1.10.1 applied with the gateway stopped: cos bd4b8cd, coo 8cae25a; AGENTS.md only. CFO unchanged.
- Gateway active, one process; health check PASS 54, WARN 0, FAIL 0.
- D1 three in a row: PASS (loop2-scn-027, 028, 029). Each wrote delete-pending-approval then deleted, event ID seed-3 (the entry's journal ID), requested by CEO, numstat 5 0; the COO replies made no Google claim; the job (via the cron wrapper with GCAL_ALLOW_DELETES=1) deleted the Google event. In 029 the COO also printed the request ID 10302026-0001 next to seed-3 (a title-style ID, not invented).
- D2: run 030 PARTIAL, run 032 PASS.
  - 030: question gave only the pending line (seed-3), approval request one item per line, approval gave deleted with the same ID. But the CoS added "privacy=high" to both delete lines; the job then treated the entry as a busy event, found a plain event in Google and refused: a conflict line, reason "that event is not a LifeOS busy event; nothing was changed". Google unchanged (guard held). Cleaned with gcal_delete.py --title (approval note "CEO handover 4, 2026-10-26") before the next run.
  - 032: same scenario, no privacy=high; pending only, then deleted, seed-3; the job deleted the event.
- R regression loop2-scn-031: PASS. Checker all passed, numstat 5 0 then 6 0, busy on 10-29.
- Cost: not measured per run (COO turns not exported); estimated under 0.015 USD per run, under 0.1 USD in total.
- Runs in all: 7 (027 to 032 and 031), 6 pass, 1 partial (030).

## For the CEO
1. The v1.10.1 wording works for order and event ID. New gap: the CoS sometimes adds privacy=high to delete lines for a plain entry (030). The job refuses safely, but the delete does not reach Google. Proposed smallest wording (not applied): in the CoS delete rule add "On delete lines copy only the event ID and requested by; do not add privacy=high or any detail." Or let the job ignore the detail on delete lines; your choice.
2. P-42 criterion "three D1 runs in a row" is met. D2 passed on the repeat but failed once on the job step. Whether that blocks the move to the real calendar is your call.
3. Record the APR for the repo state: v1.10.1 applied.

## End state (23:57 AST)
Gateway active, one process. Cron */5 active on the test calendar (stress-ng and 05:00 lines kept), GCAL_ALLOW_DELETES=1 ON. Google holds only the three seed events. State reset to the seed, seeds pushed (3 0). Last agent message and compaction at 23:56 AST; none after.

## Files in ~/handover/
REPORT-5.md, loop1-v1101-upgrade.sh, h4-d1.sh, h4-post.sh.
