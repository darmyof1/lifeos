# REPORT 10 - Loop 3 step 2: counted structure comparison (APR-0099)

Date: 2026-10-27 night to 2026-10-28 01:50 AST. All runs finished before 02:30 AST. No agent message, compaction or gateway restart in 03:30 to 05:10.

## 1. Tooling changes (Task 1)
Full diffs: `structure-test/task1-diffs.txt`.
1. P-35 ack error is informational. `reg-criteria.py` prints "INFO ack error seen"; `regression-suite.sh` runs the push job whenever the journal checks pass and counts only `^FAIL`.
2. Solo agent uses one persistent main session, `agent:solo:main`, compacted in prep with `openclaw sessions compact "agent:solo:main" --agent solo --max-lines 1`. Runs send with `openclaw agent --agent solo --session-key agent:solo:main`.
3. `reg-criteria.py --solo` lists the dropped criteria as "4-SET-ONLY". Dry-run on the two smoke runs and 200 unit tests passed; `regression-suite.sh --dry-run` passed.
4. Added to solo prep (after run s-008): the seed push is retried up to 3 times if numstat is not 3 0. Added metrics (`run-metrics.py`) and wall time.

Baseline re-score (`regression/rescore.md`): loop3-reg-001 old 5/7, new 6/7; 002 old 5/7, new 6/7; 003 7/7 both. Still FAIL under the new rule: 001-06 (08:00 slot not offered) and 002-03 (pending line requested by COO).

## 2. Method
- 4-set: suites loop3-reg-001/2/3 (baseline) and loop3-cmp-001/2/3, 6 runs per scenario. Solo: loop3-cmp-s-002 to -043, 6 per scenario, alternating with the other scenarios in rounds. Solo and 4-set never ran at the same moment.
- Void run: loop3-cmp-s-001 (prep stopped, main session did not exist yet; not counted, ID not reused).
- Data: `structure-test/comparison/` (one .txt and .metrics.json per solo run, suite files for 4-set), summary `comparison.md`, `driver.log`.
- Shared criteria are scored first. "4-set only" faults (sessions_send checker, naming CHO/CoS, CFO calling the CoS, requested by CHO) are separate and never mixed in.

## 3. Pass counts, shared criteria (runs with no failed shared criterion)
| scenario | 4-set | solo |
|---|---|---|
| bad-sleep | 6/6 | 5/6 |
| D1 delete (CEO instruction) | 6/6 | 6/6 |
| D2 delete (CEO question, approval) | 4/6 | 4/6 |
| D3 delete asked by a chief | 4/6 | 0/6 |
| CFO entry | 6/6 | 6/6 |
| overlap | 4/6 | 6/6 |
| privacy request | 6/6 | 4/6 |
| all | 36/42 | 31/42 |

D3 is not comparable. The solo is addressed by the CEO and cannot tell a chief's request from the CEO's, so it wrote pending and deleted (the CEO's request is the approval). The 4-set criterion "only a pending line" cannot be met by a design without a chief. Excluding D3: 4-set 32/36, solo 31/36.

## 4. 4-set only faults (separate)
- Runs with a 4-set-only fault: bad-sleep 1/6 (loop3-cmp-001-01: the COO reply did not name the CHO and the CoS with the event ID); all other scenarios 0/6.
- Acknowledgement errors (P-35) seen: 2 in bad-sleep baseline runs (loop3-reg-001-01, 002-01); those runs' job-dependent criteria could not be scored under the old runner and are not counted either way.

## 5. Cost, tokens, turns, prompt size (means per run, 42 runs per variant)
| | 4-set | solo |
|---|---|---|
| cost USD | 0.0061 (total 0.2576) | 0.0019 (total 0.0809) |
| input tokens | 1053 | 115 |
| output tokens | 4058 | 1596 |
| cache read tokens | 140876 | 54246 |
| turns | 12.8 | 5.0 |
| tool calls | 29.0 | 11.5 |
| wall seconds (new runs only) | 71 | 31 |
| first-turn tokens, summed over agents that ran | 24252 | 9688 |
| instruction bytes, agents that ran | 19665 | 9072 |

Per-scenario means are in `comparison.md` section 5. No run exceeded 0.05 USD; the night's new spend was about 0.30 USD (limit 1 USD).

## 6. What this test does and does not measure
It measures reliability on these seven scenarios only. It does not measure data-scope isolation between the four domains (ADR-0016, APR-0086): the solo agent can read and write every domain's state by design.

## 7. Failures exactly as they happened
4-set:
- loop3-reg-001-06 (O): the nearest free slot (08:00) was not offered.
- loop3-reg-002-03 (D2): the pending line was requested by COO instead of CEO (both delete lines: seed-3, requested by CEO, empty detail was not met).
- loop3-cmp-001-04 (D3): only a pending line, no deleted line was expected; the reply told the CEO it waits for approval; Google event still there. Counted as FAIL under the stored criteria; see the D3 note above (this is the 4-set's own D3 run, so it is a real miss of the criterion text).
- loop3-cmp-001-06 (O): the nearest free slot (08:00) was not offered.
- loop3-cmp-003-03 (D2): heuristic "no false Google claim" fired on the sentence "calendar journal: cos appended a deleted line for the oct 30 workout ..." (a journal statement). I did not change the criterion; counted as FAIL per the rule.
- loop3-cmp-003-04 (D3): same text as cmp-001-04.
- loop3-cmp-001-01 (4-set only, R): the COO reply did not name the CHO and the CoS with the event ID.

Solo:
- loop3-cmp-s-002 (bad-sleep): numstat 5 0 then 6 0 (a stray sleep-fact line in the journal; the run's duplicate-write check failed).
- loop3-cmp-s-004 (D2): same heuristic as cmp-003-03, on "Calendar journal: Solo appended `deleted` ... in `state/calendar-journal.md`". Counted FAIL per the rule.
- loop3-cmp-s-005, -012, -019, -026, -033, -040 (D3): pending and deleted both written (see D3 note); Google event removed.
- loop3-cmp-s-008 (privacy): the agent wrote status `updated` instead of `written`, no busy event pushed; a transient Google error in the seed push also occurred in prep (numstat 1 0 at start). The prep retry was added after this run.
- loop3-cmp-s-011 (D2): the first message returned "Ask User failed" after 297 s (the one wall-time outlier); the second reply had no seven-item list ("got 0"); the journal and Google steps passed.
- loop3-cmp-s-022 (privacy): the agent replied "Recorded the workout as private in state/calendar-journal.md; no Google Calendar write was made." No privacy=high line was written, so Google had no busy event.

Correction to REPORT-8: I wrote that a move was "written twice". The journal for that run held only 2 lines. That statement was wrong.

## 8. Notes
- The 4-set cleanup approval note in `regression-suite.sh` still says "CEO handover 9"; the solo one says "handover 10".
- I make no recommendation on agent structure. The data above is what happened.

## 9. End state (verified 01:50 AST)
- Gateway active, one process. Cron `*/5` on the test calendar, `GCAL_ALLOW_DELETES=1`.
- Google test calendar: only the three seed workouts (10-26, 10-28, 10-30).
- CoS journal numstat 3 0; solo journal numstat 3 0 (seed).
- COO, CHO, CFO workspaces clean; the CoS workspace shows only its seed state. No change to the COO, CHO, CoS or CFO files, config, bindings or cron.
- Health check: PASS 71, WARN 0, FAIL 0 (`health-check-output.txt`).

## 10. Installed copies (sha256 prefix, `cmp` against `~/loop1/` equal)
- regression-suite.sh ef6c29fdc185e5de
- reg-criteria.py 75df1a29573ca6a7
- run-metrics.py a84a7fefe482609d
- structure-test/solo-run.sh 7ef897b9e1845439
- structure-test/comparison-driver.sh 951879290dc0f03a
