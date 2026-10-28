# Handover 10 to Claude Code on the LifeOS VM (Loop 3 step 2: counted structure comparison)

Same Claude Code as handovers 1 to 9. The CEO approved the counted comparison (APR-0099). Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0099 ..." at the top, with the handover 9 commit below it). If it is missing, stop and tell the CEO.

## Read first
APR-0097 and APR-0099 in decisions/APPROVALS.md, P-43 in decisions/PENDING.md, deploy/loop3/structure-test/design.md, deploy/loop3/vm/regression-suite.sh and reg-criteria.py, ops/handover-2026-10-27-claude-code-report-9.md.

## Hard limits (as before)
1. No change to the COO, CHO, CoS or CFO files, config, state, bindings or cron. The solo agent files may change only as Task 1 says and only with the CEO's APR-0099 wording.
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, calendar ID or VM address in anything you put in ~/handover/.
3. TIME WINDOW: no agent message, no `sessions compact`, no gateway restart between 03:30 and 05:10 AST. Finish all runs by 02:30 AST. Never start a run that cannot finish before 02:30. Run in sessions of about an hour; stop cleanly and say where you stopped.
4. Cost under 0.05 USD per run, under 1 USD per night.
5. Journals and git history append-only. Never reuse a run ID. Never change an instruction to make a run pass; report failures as they are.
6. Solo runs and four-agent runs never run at the same moment.

## Task 1. Three tooling changes (no agent instruction changes except the solo session setting)
1. P-35 treatment (APR-0099 item 1). In reg-criteria.py and regression-suite.sh: a sessions_send acknowledgement error (SESSION_WORK_START_CHANGED or similar) is reported as the informational line "ack error seen" and does NOT fail the run. The runner runs the job whenever the journal checks pass. A missing write or a duplicate write stays a failure. Re-score the three existing baseline runs (loop3-reg-001, -002, -003) with the new rule and save both scores side by side (old rule, new rule) in ~/handover/regression/rescore.md. Do not edit the old result files.
2. Solo session (APR-0099 item 2). The solo agent uses one persistent main session like the other agents, compacted in prep the way scenario-run.sh does it for the four agents (same command, same window rule), instead of a new session id per run. Change solo-run.sh accordingly. Report the exact command lines you changed.
3. A solo criteria checker: reg-criteria.py gets a solo mode that applies the "solo" column of the table in design.md section 4 and lists the dropped criteria separately as "4-set only". Dry-run it on the two smoke runs of handover 9.

Show the CEO the diff of each of the three before Task 2 (put them in the report). Then run the unit tests for what exists in the repo copies and `regression-suite.sh --dry-run`.

## Task 2. The counted comparison
Per scenario (seven: bad-sleep, D1, D2, D3, CFO entry, overlap, privacy) six runs per variant:
- 4-set: the three baseline runs already done (loop3-reg-001 to -003) plus three new full suites: `regression-suite.sh loop3-cmp-001`, `loop3-cmp-002`, `loop3-cmp-003`.
- solo: six runs per scenario with run IDs loop3-cmp-s-001 and up, same message text as the suite apart from the routing words, through solo-run.sh. Alternate variants within a session (a 4-set suite, then a block of solo runs) so a time-of-day effect hits both.
- About 63 runs in total, about 0.30 USD. If a session ends early, resume next time without repeating a run ID.

For every run save: pass or fail per criterion, input and output tokens, cost (run-cost.py), turns and tool calls, wall time, prompt size (bytes of the four instruction files and the first-turn token count of every agent that ran; for the 4-set the sum over COO, CHO, CoS, CFO). Results go to ~/handover/structure-test/comparison/ (one file per run) and a summary comparison.md.

## Task 3. Report (~/handover/REPORT-10.md)
1. Per scenario pass counts x/6 per variant, shared criteria first, then the "4-set only" faults separately. Do not mix them.
2. Cost, tokens, turns and prompt size per variant.
3. What the test cannot show: it measures reliability only, not data-scope isolation (ADR-0016, APR-0086). Say so in the report.
4. Failures exactly as they happened. No recommendation to change the agent structure: that is the CEO's separate decision.
5. State at the end: gateway one process, cron unchanged, calendar back to the three seed events, anything stopped early.

Package: `tar czf ~/handover-10.tar.gz -C ~ handover` after checking for secrets (no ID, token, calendar ID, address). Return the file; confirm by checksum that anything you say is installed or updated really is.
