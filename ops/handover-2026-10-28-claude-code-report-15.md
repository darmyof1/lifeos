# REPORT 15 - COO instruction set v1.10.4 applied (APR-0104)

Pulled first: HEAD e53677c "APR-0104 ...", `deploy/loop1/loop1-v1104-upgrade.sh` present. Work 22:18 to about 00:05 AST; agent runs ended before 02:30 and none fell in 03:30 to 05:10. Total cost of the three suites 0.136 USD (largest single run 0.0121); the five by-hand messages were not costed separately (a few thousandths of a dollar each in the normal runs).

## What was applied
- Dry run, then gateway stopped, `loop1-v1104-upgrade.sh`, gateway started at once (stopped 22:18:40, started 22:18:45). Only the COO's AGENTS.md changed: one appended line, commit c55f008 "Loop 1 instructions v1.10.4 (APR-0103)" in the COO workspace (`AGENTS.md | 1 +`). The line is the "Delete reply line" rule from the repo script.
- sha256 of the live COO AGENTS.md starts 0b59e7ff33f51035 and equals the repo copy.
- Gateway: one process, active; 4 Slack accounts connected (health check line "4 connected").
- Health check: repo `health-check.py` copied to `~/loop1/health-check.py` (old one kept as `health-check.py.pre-v1104`); `cmp` says the installed file equals the repo file. Output in `health-check-output.txt`: **PASS 70, WARN 0, FAIL 0, INFO 4**; all 16 parity lines PASS; "coo carry v1.10.4" PASS. The handover expected 0 FAIL; the PASS total is 70, not the 71 earlier checks showed, because this version of the check has a different set of lines (I did not compare line by line).
- CHO, CoS, CFO files, the OpenClaw config, bindings and the cron were not touched. The plugin is not installed.

## Runner change (Task 2)
- `regression-suite.sh` line 77 and `structure-test/solo-run.sh` line 47: the D2 approval message changed from "Run ID $R. Yes, I approve deleting the 2026-10-30 workout. Tell me ..." to "Run ID $R. approve seed-3. Tell me in 3 lines what changed in the calendar journal and in Google, and what is still needed." Installed in `~/loop1/` and checked with `cmp`. Everything else is unchanged, including the runner writing the seed-3 ledger line after that message.
- **The D2 baseline text changed because the approved rule changed** (APR-0103/0104: the CEO now writes `approve <event ID>`). Results of D2 before and after this change are therefore not the same test.
- Criterion: the seven-items check matches the labels (What ... Reply followed by a colon), so the new Reply wording passes it without change. **No criterion was changed.**

## Counted suites (Task 3), 21 runs
| run | -001 | -002 | -003 |
|---|---|---|---|
| 01 bad-sleep | PASS | PASS | PASS |
| 02 D1 CEO delete | PASS | PASS | **FAIL** |
| 03 D2 question then approve | PASS (9/9) | PASS (9/9) | PASS (9/9) |
| 04 D3 chief asks | **FAIL** | PASS | PASS |
| 05 CFO entry | PASS | PASS | PASS |
| 06 overlap | PASS | PASS | **FAIL** |
| 07 privacy | PASS | PASS | PASS |
| pass / cost USD | 6 of 7 / 0.0553 | 7 of 7 / 0.0409 | 5 of 7 / 0.0399 |

Total 18 of 21. D2 passed 3 of 3 with the seven items in order each time and the delete reaching Google through the job with the ledger line.

Failures, exactly as they happened:
- **-001-04 (D3):** criterion "only a pending line, no deleted line" failed. The CHO's path wrote an agent `deleted` line; the job skipped it ("no CEO approval record for event seed-3 (APR-0100)") and the Google event stayed. The suite marks it "GATE held (agent fault)". Same pattern as handover 12; not related to v1.10.4.
- **-003-06 (overlap):** criterion "the nearest free slot (08:00) was offered" failed; 8 other criteria passed. Not examined further.
- **-003-02 (D1), a new behaviour I think comes from v1.10.4:** the COO did not pass the CEO's explicit delete to the CoS. It posted the seven items instead, with "Reply: approve 10302026-0001, explain more, or keep" (the event's title ID, not the journal event ID seed-3) and "a bare approve will not delete it". No journal line was written (3 0 before and after), so three criteria failed (pending first then deleted; both lines; Google event deleted). D1 passed in -001 and -002. One in three; I cannot say if it is a rate. The instruction was not changed.

## By-hand checks (COO, CLI, synthetic)
- **loop3-v1104-h-1:** the COO answered the question with the seven items and "Reply: approve 10302026-0001, explain more, or keep", but wrote **no pending line** and used the title ID, not a journal event ID. A bare "approve": not passed on, asked for "approve 10302026-0001" once (right behaviour, wrong ID). Then "approve seed-3": **not passed to the CoS** ("seed-3 doesn't match event 10302026-0001"); it asked again for the title ID. So (a) passed, (b) and (c) failed in this run.
- **loop3-v1104-h-2** (fresh run, same steps): (c) PASS: the CoS wrote the pending line (journal event ID seed-3) and the COO posted the seven items, each on its own line, last item exactly "Reply: approve seed-3, explain more, or keep", plus "a bare approve will not delete it". (a) PASS: a bare "approve" gave only "Please reply approve seed-3 ..."; the journal stayed at one line. (b) PASS: "approve seed-3" led the CoS to append the `deleted` line with the event ID and the CEO's words; Google was changed by no one (the push job was not run).
- So the pattern that matters: when the COO fails to route the question through the CoS, it invents the event ID from the title and the CEO's `approve seed-3` is refused. That fits the 003-02 D1 failure. Output files are in `regression/loop3-v1104-h/`. I ran h-2 because h-1 did not reach a pending line; I report both.

## End state
Gateway one process, active. Cron active `*/5`, 0 `--require-ceo-ledger` lines (it was paused during by-hand runs and I resumed it). Google test calendar: the three seed events (workouts 10-26, 10-28, 10-30), "other events: 0"; journal at seed (3 0). The plugin is not installed, `~/loop1/ceo-slack-id` does not exist, `openclaw.json` untouched. The 10-30 workout has a new Google ID after the final reset (normal for a re-seed).

## Findings for the CEO
1. v1.10.4 works when the COO routes through the CoS, but twice in four tries (-003-02, h-1) the COO skipped that and used the event's title ID as the "event ID", which the gate would reject. Options for a later APR: a sentence in the COO line saying the event ID is the journal ID from the CoS (like seed-3), never the title, and never ask for approval before the CoS has written the pending line.
2. D3 can still produce an agent-written `deleted` line; the job skips it (gate held).
