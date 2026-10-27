# Scenario: bad-sleep reschedule (Loop 1)

Rules: APR-0052 (synthetic data), APR-0054 (journal), APR-0056 (cost), APR-0057 (move), APR-0058 (instructions v1.2), ADR-0018.
Runs needed to close: three identical passing runs, plus one run with a gateway restart in the middle.
Status 2026-10-22: both met (runs 3 to 5 passed in a row; run 6 restart and retries passed). First Slack run (loop1-scn-007, 2026-10-24) was partial; instruction set v1.3 (APR-0064) is the fix. Run 009 passed in Slack; run 010 was partial (stale "pending"); instruction set v1.4 (APR-0065) is the fix. Under v1.4: run 011 failed (no task details on first contact), run 012 (CLI to the CHO) passed on content, run 013 passed on content after a COO resend but showed a FAILURE note. Proposed fix: v1.5 (P-34). Under v1.5 and v1.6: runs 015, 016, 017 and 019 passed on content (019 clean: one run per agent); run 018 partial. Closed for Loop 1 on 2026-10-25 (APR-0069); criterion 6 (cost) deferred by the CEO.

Loop 2 (APR-0073): runs loop2-scn-001 and loop2-scn-002 (2026-10-25 and 26, Slack, v1.6) passed on content. The trajectory exports showed that the CHO's sessions_send arguments (notify, watch, resume) start no CoS turn, which explains the CoS running twice. Instruction set v1.7 (APR-0075) fixed it: runs loop2-scn-003 and -004 passed with one CHO call each and no CoS send to the CHO (APR-0076, P-38 closed).

## Setup
- Agents COO, CHO, CoS and CFO with instruction set v1.2 (deploy/loop1/loop1-agent-files.sh).
- Gateway running once: pgrep -af "openclaw.*gateway" | grep -v pgrep | wc -l prints 1.
- Before each run, save the state and reset it to the seed:

      W=~/loop1/workspaces; E=~/loop1/evidence/<date>
      mkdir -p $E
      for a in cho cos cfo; do cp -r $W/$a/state $E/<run ID>-$a; git -C $W/$a checkout -- state/; done

- Use a fresh session id for each run.
- Pause the calendar cron before the reset and resume it after the checks and the export (section "Loop 2 calendar cron (APR-0078)" below). While it runs, it appends pushed lines to the CoS journal, so the numstat check would no longer read 2 0.
- The reset above restores the last commit, so each workspace's HEAD must hold the seed state. Never run git add -A in a workspace while state/ is dirty (the first v1.3 upgrade did; repaired 2026-10-24).
- A run from Slack also needs a fresh COO channel session: an old one remembers earlier runs.
- Between runs, cut the four main sessions to one line (synthetic data only; no backup is kept):

      T=$(cat ~/loop1/gateway-token)
      for a in coo cho cos cfo; do openclaw sessions compact "agent:$a:main" --agent $a --max-lines 1 --token "$T"; done


## Input (to the COO)
    openclaw agent --agent coo --session-id <run ID>-coo --timeout 300 -m "Loop 1 scenario run, run ID <run ID>. Alex Test slept 5 hours last night. Move the Wednesday workout on 2026-10-28 to Thursday 2026-10-29, 07:00 to 08:00. Route this to the CHO, which owns health. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs."

From Slack, the post must start with `@COO ` (the agents answer only when the post starts with their name), followed by the same text. Post `@COO /new` first.

## Checks (after 120 seconds)
    tail -n 4 ~/loop1/workspaces/cos/state/calendar-journal.md
    tail -n 2 ~/loop1/workspaces/cho/state/health-plan.md
    git -C ~/loop1/workspaces/cos diff --numstat state/calendar-journal.md

## Pass criteria
1. The COO routes to the CHO. The CHO sends the move to the CoS and never writes the calendar itself (APR-0030, APR-0044).
2. The CHO logs the sleep fact in state/health-plan.md with its own event ID (APR-0081, instruction set v1.8). The calendar move is recorded in the CoS journal, not in the health plan. (Runs 004 to 006 differed on what to log, see P-39; under v1.7 the setup note did not say.)
3. The CoS journal keeps the 10-28 seed line and appends two lines: 10-28 moved and 10-29 written, both with the run ID and event ID (APR-0054, APR-0057). From instruction set v1.9 (APR-0086) both lines also carry `privacy=high` in the detail column.
4. The numstat check shows no deletions, and the journal header line is unchanged (run 009: the CoS added a column to it; fixed by v1.9.1, APR-0089). Additions: the two CHO lines (2 0). With the calendar job in use there are more: 3 pushed lines when the seed lines were pushed by hand after the reset (5 0), and 1 more when the job has pushed the move (6 0).
5. The COO summary names the CHO and the CoS and gives the event ID (APR-0050).
6. The run costs less than 0.05 USD (APR-0056). First measure: about 0.047 USD for the Slack run loop1-scn-007 (usage page item changes, 2026-10-24). Run 010: at most about 0.020 USD (includes the health check turns after it).

## Still to cover
- Cost per run: 0.047 USD for loop1-scn-007 (Slack, with retries); at most 0.020 USD for loop1-scn-010. Runs 011 to 013 were not measured (the usage page lagged). Not measured from 2026-10-24 on: deferred by the CEO (APR-0069).
- What the CEO sees in Slack: runs 009 and 010 showed one line each in the CHO and CoS channels (APR-0050 works). Run 010's COO reply was wrong ("pending"); v1.4 fixed that. Run 013's COO reply named the CHO and the CoS but carried a FAILURE note after a resend (P-34).

## Loop 2 checks under v1.7 (APR-0075, P-38)
After the run, and before the next reset, export the CHO and CoS sessions and read their sessions_send calls. One export holds the whole session; the checker finds the run by its run ID (add --since <UTC time> only to override). Use a new export name for each run: an existing name fails with EEXIST. Run the last command from the repo clone on the VM:

    source ~/loop1/env.sh
    openclaw sessions export-trajectory --session-key "agent:cho:main" --workspace ~/loop1/evidence/traj --output <run ID>-cho
    openclaw sessions export-trajectory --session-key "agent:cos:main" --workspace ~/loop1/evidence/traj --output <run ID>-cos
    python3 scripts/verify/check_sessions_send.py ~/loop1/evidence/traj/.openclaw/trajectory-exports <run ID>

Pass (APR-0075): the checker ends with "all checks passed": the CHO's first call to the CoS has mode followup, no watch and timeoutSeconds 120 and returns a reply; the CoS sends nothing to the CHO; no SESSION_WORK_START_CHANGED. A WARN for a second CHO call is allowed (v1.7 lets the CHO resend once). The usual criteria 1 to 5 still apply.

## Loop 2 calendar cron (APR-0078)
Since 2026-10-26 a plain cron job under ubuntu runs scripts/gcal/gcal_sync.py every 5 minutes against the Google test calendar (guides/calendar-sync-job.md). It reads the CoS journal and appends pushed lines to it. Every scenario run has two extra steps:

Before a run, delete the leftover events of earlier runs from the test calendar (scripts/gcal/gcal_delete.py with the CEO's approval, APR-0044), or the new move would find its target already there. After the state reset, push the seed lines by hand (bash ~/lifeos-ro/scripts/gcal/gcal_sync_cron.sh), so the run's move is a real move in Google and not a create.

Pause, before the state reset:

    crontab -l | sed 's|^\*/5 .*gcal_sync_cron.sh|#&|' | crontab -
    crontab -l | grep gcal_sync      (expect: the line starts with #)

Resume, after the checker has passed and the export is done (the job then pushes the run's entries to the test calendar; read the last block of ~/loop1/gcal-sync/sync.log):

    crontab -l | sed 's|^#\(\*/5 .*gcal_sync_cron.sh\)|\1|' | crontab -
    crontab -l | grep gcal_sync      (expect: the line starts with */5)

After a gateway start, read every `openclaw sessions compact` output before the run: an error such as "Check the Control UI or run openclaw gateway status" means the session was not compacted and the agent remembers the earlier run (run 010). Wait until the gateway is ready and compact again.

The next reset removes the pushed lines from the journal, so events from earlier runs stay in the test calendar. They are cleaned up only with scripts/gcal/gcal_delete.py and the CEO's approval (APR-0044). Never use --allow-deletes for this.

## Loop 2 privacy checks under v1.9 (APR-0086)
The run is the same. The CHO's entries are high privacy by default, so after the job runs by hand (checks batch):
7. The two CHO journal lines (moved, written) carry `privacy=high`, and the job's pushed line for the move says `google=<id>; privacy=high`.
8. Google (gcal_list.py) shows one event on 2026-10-29 07:00 titled `busy`, and no event titled `CHO - Workout - 10292026-0001` or `CHO - Workout - 10282026-0001` (the seed workout was a normal event; the job turns it into the busy event, `made busy`). The 10-26 and 10-30 seed workouts keep their full titles (the seed lines are not marked).
9. Cleanup before the next run: the leftover busy event is deleted with gcal_delete.py --busy-key <run ID>-cho-02 (CEO approval stated in the batch).

## Run log
| Run | Date | Instructions | Result | Notes |
|---|---|---|---|---|
| loop1-scn-001 | 2026-10-22 | v1 | Fail | The CHO refused: no event ID was given and no rule said who creates one. Led to v1.1. |
| loop1-scn-002 | 2026-10-22 | v1.1 | Partial | Move done. The CoS edited the 10-28 line in place, so the journal was not append-only. The COO summary named only the CHO. Led to APR-0057 and v1.2. |
| loop1-scn-003 | 2026-10-22 | v1.2 | Pass (criteria 1 to 5) | numstat 2 0; event ID loop1-scn-003-cho-01; the summary named the CHO and the CoS. |
| loop1-scn-004 | 2026-10-22 | v1.2 | Pass (criteria 1 to 5) | Summary listed the entry name as an event ID as well; the real event ID was given. |
| loop1-scn-005 | 2026-10-22 | v1.2 | Pass (criteria 1 to 5) | Third pass in a row. |
| loop1-scn-006 | 2026-10-22 | v1.2 | Pass (restart) | Ctrl-C during the run: the gateway drained for about 60 s and refused the CHO's sends; no change was written (numstat 0 0). Retry with the same run ID wrote one pair (2 0). |
| loop1-scn-006 resend | 2026-10-22 | v1.2 | Pass (duplicate check) | Resending the finished run reported the earlier result; no -cho-02, numstat still 2 0. |
| loop1-scn-007 | 2026-10-24 | v1.2 (Slack) | Partial | Run from the COO channel. Criteria 1 to 4 pass (numstat 2 0, event ID loop1-scn-007-cho-01). The COO's first reply said blocked after its wait ended; the CHO's late report woke the COO twice; two duplicate summaries by message tool and two incomplete-turn errors. The CHO and CoS channels showed no post. Cost about 0.047 USD, 80 requests. Led to v1.3 (APR-0064). |
| loop1-scn-008 | 2026-10-24 | v1.3 (Slack) | Invalid | The state was not at the seed (the upgrade commit held the run-007 state), so the move was already done and no change was written. Seen: one COO reply with no "blocked" wait; a "Late reply:" line posted with the message tool and one incomplete-turn error, after the CHO sent a second report to the COO. No post in the CHO or CoS channel, as expected with no change. Cost about 0.009 USD (18 requests). Rerun after the repair. |
| loop1-scn-009 | 2026-10-24 | v1.3 (Slack) | Pass (criteria 1 to 5) | From the COO channel after the state repair. numstat 2 0; event ID loop1-scn-009-cho-01. One COO reply naming the CHO and CoS; one line each in the CHO and CoS channels; no late reply, no error. Cost not measured. |
| loop1-scn-010 | 2026-10-24 | v1.3 (Slack) | Partial | Journal correct (numstat 2 0, loop1-scn-010-cho-01). The CHO reported "pending" while the CoS had already written; the COO told the CEO "pending" and named only the CHO; a stale "Late reply" followed. The CoS confirmation to the CHO failed twice (SESSION_WORK_START_CHANGED). Own-channel lines were posted. Cost at most 0.020 USD. Led to v1.4 (APR-0065). |
| loop1-scn-011 | 2026-10-24 | v1.4 (Slack) | Fail | The CHO found no task details on the COO's first routed message and wrote nothing; the COO reported no change. Not measured. |
| loop1-scn-012 | 2026-10-24 | v1.4 (CLI to the CHO) | Pass on content | Sent straight to the CHO, not through the COO. numstat 2 0, loop1-scn-012-cho-01; CHO and CoS channel lines posted; the CHO reported done once. The CoS reply to the CHO hit SESSION_WORK_START_CHANGED after sending (P-35). |
| loop1-scn-013 | 2026-10-24 | v1.4 (Slack) | Content pass, not clean | The CHO again found no task details on first contact; the COO resent and the move went through (numstat 2 0, loop1-scn-013-cho-01). The COO named the CHO and the CoS, but its answer carried a FAILURE note. Channel lines posted. Not measured. Led to P-34 (v1.5). |
| loop1-scn-014 | 2026-10-24 | v1.5 (Slack) | Not a valid move test | First attempt started during a gateway restart; the COO's wait failed. The run ID was then reused after a state reset. The CHO answered from its own session memory of run 013 ("already handled"), wrote no journal change, and logged an event ID (loop1-scn-014-cho-01) that health-plan.md does not contain. The COO's late reply gave the wrong sleep date (2026-10-23). A git state reset and a one-line session compaction do not clear agent memory. Not measured. |
| loop1-scn-015 | 2026-10-24 | v1.5 (Slack) | Pass on content | Fresh run ID after the reset; the CHO handled the sleep and the move without the 014 memory. One COO reply naming the CHO and CoS, with event IDs loop1-scn-015-cho-01 and -cho-02; one line each in the CHO and CoS channels; no late reply, no FAILURE note; numstat 2 0. The CoS logged a session-start error on its reply to the CHO (P-35); the CHO handled the content anyway. SESSION_WORK_START_CHANGED count unchanged at 2. Cost not measured (deferred by the CEO). |
| loop1-scn-016 | 2026-10-24 | v1.5 (Slack) | Pass on content (VM report REPORT-016) | numstat 2 0; COO reply names CHO and CoS with event IDs loop1-scn-016-cho-01 and -cho-02; no late reply, no FAILURE note; SESSION_WORK_START_CHANGED count unchanged. Cost not measured (deferred by the CEO). |
| loop1-scn-017 | 2026-10-25 | v1.6 (Slack) | Pass on content | numstat 2 0; COO reply names CHO and CoS with event ID loop1-scn-017-cho-01; CHO line in health-cho and CoS line in staff-cos; no FAILURE note. The CoS reported 'logged as delivered, but its acknowledgement failed (P-35)' before the CHO replied; the CHO replied with the content about a minute later. The gateway log has no error line for the acknowledgement. Cost not measured (deferred by the CEO). |
| loop1-scn-018 | 2026-10-25 | v1.6 (Slack) | Partial | numstat 2 0; loop1-scn-018-cho-01 in health-plan; CHO and CoS channel lines posted; no FAILURE note. The COO's reply named only the CHO (the criterion asks for the CHO and the CoS). The CoS ran twice: its first run took no action, its second made the move. The CEO posted once, so the second run came from an agent message; cause not found. No duplicate write. Cost not measured. |
| loop1-scn-019 | 2026-10-25 | v1.6 (Slack) | Pass | numstat 2 0; loop1-scn-019-cho-01 in health-plan; COO reply names the CHO and the CoS with event IDs; one line each in the CHO and CoS channels; one run each for the CHO and the CoS; no late reply, no FAILURE note. The CoS reported the P-35 acknowledgement error in v1.6 wording. The CHO treated the sleep report as context and did not log it (runs 015 and 016 logged it). Cost not measured (deferred by the CEO). |
| loop2-scn-001 | 2026-10-25 | v1.6 (Slack, Loop 2) | Pass on content | First Loop 2 run; post started with @COO. numstat 2 0. CHO trajectory: five sessions_send calls to the CoS (notify with watch: forbidden; notify: queued, no CoS turn; resume twice: rejected; followup: worked). The CHO posted two lines in its channel. One SESSION_WORK_START_CHANGED on the CoS reply to the CHO (sentBeforeError true). P-37: not seen. Per-run cost from the trajectory, CHO only: about 0.01 USD. |
| loop2-scn-002 | 2026-10-26 | v1.6 (Slack, Loop 2) | Pass on content | numstat 2 0. Four sessions_send calls to the CoS: forbidden, queued, a followup without details (the CoS replied it could not act), then a followup with the full details (worked). Three SESSION_WORK_START_CHANGED on CoS replies. The CEO's post lost its first letter ("oop 1 scenario run"); no effect. P-37: not seen. Per-run cost from the trajectory: CHO about 0.006 USD, each CoS run about 0.003 USD. The export loop2-scn-002-cho holds both runs (one session). |
| loop2-scn-003 | 2026-10-26 | v1.7 (Slack, Loop 2) | Pass | First run under v1.7 (applied 01:43 AST). numstat 2 0; COO reply names the CHO and the CoS with event IDs loop2-scn-003-cho-01 and -cho-02; one line in the CoS channel, two in the CHO channel (one per event); no late reply, no FAILURE note. Checker: one CHO sessions_send to the CoS (followup, timeoutSeconds 120, ok), none from the CoS, no SESSION_WORK_START_CHANGED. P-37: one 'SQLite session write failed' on the COO at 01:55:50 AST, at the post. |
| loop2-scn-004 | 2026-10-26 | v1.7 (Slack, Loop 2) | Pass | Second run under v1.7. numstat 2 0; COO reply names the CHO and the CoS with event IDs loop2-scn-004-cho-01 and -cho-02; one line in the CoS channel, two in the CHO channel; no late reply, no FAILURE note. Checker: one CHO call (followup, ok, 06:01:27 UTC), no CoS send, no SESSION_WORK_START_CHANGED. P-37: not seen. The first version of the checker also listed run 003's call from the same export (WARN); fixed in fix-68. |
| loop2-scn-005 | 2026-10-26 | v1.7 (Slack, Loop 2, calendar cron live) | Partial | Calendar path passed: one CHO call to the CoS (followup, ok), no CoS send, no SESSION_WORK_START_CHANGED; COO reply named the CHO and the CoS with event ID loop2-scn-005-cho-01; one line each in the CoS and CHO channels; no late reply, no FAILURE note. numstat 5 0 after the seed push (3 pushed lines + 2 CHO lines), 6 0 after the job pushed the move: no deletions. Criterion 2 failed: the CHO did not write state/health-plan.md (change log empty, no change in the CHO workspace), and logged one event ID where run 004 logged two (sleep note cho-01, move cho-02). The export hides exec code, so the CHO's tool calls cannot be read (P-39). Calendar push, first live use of the cron path: seeds were pushed by hand after the reset (10-28 created, 10-26 and 10-30 already in Google); after the run the job found the old event by the journal's pushed line and moved the same Google event to 10-29 07:00 (title changed to 10292026-0001); Google shows 10-26, 10-29, 10-30 and nothing on 10-28. |
| loop2-scn-006 | 2026-10-26 | v1.7 (Slack, Loop 2, calendar cron live) | Partial | Calendar path passed again. Checker: one CHO call (followup, ok, 20:33 UTC), no CoS send, no SESSION_WORK_START_CHANGED. COO reply named the CHO and the CoS with event IDs loop2-scn-006-cho-01 (sleep) and -cho-02 (move); one line in the CoS channel, two in the CHO channel; no late reply, no FAILURE note. numstat 5 0 after the seed push, 6 0 after the job pushed the move (no deletions). Criterion 2 only half met: state/health-plan.md has the sleep line (cho-01) but not the move line (cho-02). P-39 repeats (run 005: nothing logged; run 004: both). Calendar: seeds pushed by hand (10-28 created), then the job moved the same Google event to 10-29 07:00 (title 10292026-0001). P-37: the day's gateway log holds 1 'SQLite session write failed' (the 01:55 AST one from run 003 is in the same file, so it is not shown to be new) and 0 'maintenance paused'. |
| loop2-scn-007 | 2026-10-26 | v1.8 (Slack, Loop 2, calendar cron live) | Pass | First run under v1.8 (applied 17:17 AST). Checker: one CHO call (followup, ok), no CoS send, no SESSION_WORK_START_CHANGED. COO reply named the CHO and the CoS with event IDs loop2-scn-007-cho-01 (sleep) and -cho-02 (move); one line in the CoS channel, two in the CHO channel; no late reply, no FAILURE note. numstat 5 0 after the seed push, 6 0 after the job pushed the move (no deletions). health-plan.md has the sleep line (cho-01) and the move line (cho-02). Google: the job moved event 248lgvflbmjvitkqmh43rud5v4 to 10-29 at 17:26:15. P-37: the one line is the old line 326 (01:55 AST), none new; 'maintenance paused' 0. |
| loop2-scn-008 | 2026-10-26 | v1.8 (Slack, Loop 2, calendar cron live) | Pass | Second run in a row under v1.8. Checker: one CHO call (followup, ok, 21:31 UTC), no CoS send, no SESSION_WORK_START_CHANGED. COO reply named the CHO and the CoS with event IDs loop2-scn-008-cho-01 and -cho-02; one line in the CoS channel, two in the CHO channel; no late reply, no FAILURE note. numstat 5 0 then 6 0 (no deletions). health-plan.md has the sleep line (cho-01) and the move line (cho-02). Google: the job moved event pnpqmrj012fv2vrj00ho155bgk to 10-29 at 17:33:07. The cron was paused for the reset and resumed after the checker passed. P-37: nothing new; 'maintenance paused' 0. P-39 closed (APR-0082). |
| loop2-scn-009 | 2026-10-26 | v1.9 (Slack, Loop 2, calendar cron live) | Partial | First run under v1.9 (applied 18:47 AST). Checker all passed; COO reply named the CHO and the CoS with both event IDs; health plan had the sleep line; both CoS lines carried privacy=high; the job turned the seed Google event into a busy event (made busy) and the mandated title left Google. numstat 6 1 then 7 1: the CoS edited the journal header (added | detail) because the v1.9 rule describes an 8-column line. Fixed by v1.9.1 (APR-0089). |
| loop2-scn-010 | 2026-10-26 | v1.9.1 (Slack, Loop 2, calendar cron live) | Void | Prep error: the CHO session compaction failed right after the gateway restart and the output was not read; the CHO remembered run 009 and did not call the CoS. Not an instruction fault. |
| loop2-scn-011 | 2026-10-26 | v1.9.1 (Slack, Loop 2, calendar cron live) | Pass | numstat 5 0 then 6 0; checker all passed (one CHO call, followup, ok; no CoS send); both CoS lines carry privacy=high; header untouched; sleep line loop2-scn-011-cho-01; COO summary names the CHO and the CoS with both event IDs; Google has one busy event on 10-29 07:00 and no Workout title for 10-28 or 10-29. |
| loop2-scn-012 | 2026-10-26 | v1.9.1 (Slack, Loop 2, calendar cron live) | Pass | Second pass in a row; same results (event IDs loop2-scn-012-cho-01 and -cho-02). 0 maintenance paused. |
| loop2-scn-013 | 2026-10-26 | v1.9.1 (CLI to the COO) | Fail (delete gate) | Other scenario: tests/scenario/delete-approval.md. A deleted line at once, no pending line; the COO claimed approval and a Google change that did not happen; the job guard held. |
| loop2-scn-014 | 2026-10-26 | v1.9.1 (CLI to the COO) | Pass | Other scenario: tests/scenario/privacy-request.md. |
| loop2-scn-015 | 2026-10-26 | v1.9.1 (CLI to the COO) | Partial | Other scenario: tests/scenario/cfo-entry.md. Right result, but the COO relayed (the CFO cannot message the CoS). |
| loop2-scn-016 | 2026-10-26 | v1.9.1 (CLI to the COO) | Partial | Other scenario: tests/scenario/overlap-conflict.md. The CoS refused the overlap and logged nothing. |
| loop2-scn-017 | 2026-10-26 | v1.9.1 (CLI to the COO) | Fail (delete gate) | Other scenario: tests/scenario/delete-approval.md (question wording). Same as 013; the COO made up an event ID. Fixes: APR-0092, v1.10. |
| loop2-scn-018 | 2026-10-26 | v1.10 (CLI to the COO) | Fail | Other scenario: delete-approval.md, D1 (CEO instruction). The CoS wrote only the deleted line (no pending line); the job guard held, Google unchanged. The COO had told the CoS "CEO's exact words approving this deletion". |
| loop2-scn-019 | 2026-10-26 | v1.10 (CLI to the COO) | Pass | D1 repeat: pending then deleted, same event ID (the entry title was used as the event ID on both lines); the job by hand with --allow-deletes deleted the Google event. |
| loop2-scn-020 | 2026-10-26 | v1.10 (CLI to the COO) | Pass | D2 (CEO question "can you remove"): only the pending line; the COO posted the seven-item approval request (on one line); after the approval the CoS appended deleted with the same event ID; the job deleted the event. |
| loop2-scn-021 | 2026-10-26 | v1.10 (CLI to the CHO) | Pass | D3 (a chief asks): only a pending line, requested by CHO; the CHO told the CEO it waits for his approval. No Google change. |
| loop2-scn-022 | 2026-10-26 | v1.10 (CLI to the COO) | Pass | CFO entry: the CFO called the CoS itself (followup, ok); event ID loop2-scn-022-cfo-01; requested by CFO; privacy=high; busy event created. |
| loop2-scn-023 | 2026-10-26 | v1.10 (CLI to the COO) | Pass | Overlap: conflict line (reason=overlaps ...), nearest slot 08:00 to 09:00 offered, the COO sent a short notice; after the CEO accepted, a written line at the new time and a busy event. |
| loop2-scn-024 | 2026-10-26 | v1.10 (CLI to the COO) | Pass | Regression bad-sleep-reschedule: checker all passed, numstat 5 0 then 6 0, busy on 10-29, sleep fact with its own event ID. |
| loop2-scn-025 | 2026-10-26 | v1.10 (CLI to the COO) | Pass | D1 with GCAL_ALLOW_DELETES=1 in the cron: pending and deleted lines with the same event ID (loop2-scn-025-coo-01, chosen by the COO or CoS); the 5-minute cron itself deleted the Google event at 23:15. |
| loop2-scn-027 | 2026-10-26 | v1.10.1 (CLI to the COO) | Pass | Other scenario: delete-approval.md, D1 (1 of 3). Pending line then deleted line, event ID seed-3, requested by CEO; numstat 5 0; the COO made no Google claim; the cron deleted the Google event. |
| loop2-scn-028 | 2026-10-26 | v1.10.1 (CLI to the COO) | Pass | D1 (2 of 3): same result. |
| loop2-scn-029 | 2026-10-26 | v1.10.1 (CLI to the COO) | Pass | D1 (3 of 3): same result; the COO also printed the request ID 10302026-0001 next to seed-3. |
| loop2-scn-030 | 2026-10-26 | v1.10.1 (CLI to the COO) | Partial | D2 (CEO question): pending only, approval request one item per line, deleted after the approval with seed-3. But the CoS added privacy=high to both delete lines; the job treated the entry as a busy event, found a plain event and wrote a conflict line (nothing changed in Google; the guard held). |
| loop2-scn-031 | 2026-10-26 | v1.10.1 (CLI to the COO) | Pass | Regression bad-sleep-reschedule: checker all passed, numstat 5 0 then 6 0, busy on 10-29. |
| loop2-scn-032 | 2026-10-26 | v1.10.1 (CLI to the COO) | Pass | D2 repeat: pending only, then deleted with seed-3 and no privacy mark; the job deleted the event. |

Evidence copies stay on the VM in ~/loop1/evidence/ (synthetic data, not in the repo).
