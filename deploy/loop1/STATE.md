# Loop 1 state and handoff (as of 2026-10-26, 02:20 AST)

Loop 1 is closed (APR-0071). Loop 2 runs cloud-only on synthetic data under APR-0073, until Loop 2 closes or 2026-12-31. The CEO starts the gateway from the main account; the sandbox account and its agent do not.

Written for a Claude Code session running on the Loop 1 VM, picking up from the planning chat. Read this first, then the files it points to. Nothing here is a decision; decisions live in decisions/APPROVALS.md, open questions in decisions/PENDING.md.

## Repo access
- The repo on GitHub is public. On the VM, work from a read-only clone and run git pull before each session, so the guides, approvals and this file are current.
- The CEO's Mac is the only machine that writes and pushes, through numbered fix scripts. Do not push from the VM unless the CEO sets that up.
- Because the repo is public, the rules under "Never" matter even more.

## How findings come back
- Write each finding in a report file on the VM: what you saw (log or journal lines), what you changed and where (repo file, VM file or config), and what needs a decision.
- Do not push. The CEO pastes the report into the planning chat, and a numbered fix script records it in the repo.
- Any change you make on the VM that is not in the repo (agent AGENTS.md, config, workspace) must be listed in the report, so it can be mirrored by a fix script.
- Changes to agent behaviour need the CEO's yes, recorded as a new APR entry in his words, before you apply them.

## Read in this order
1. guides/loop1-baseline.md, section 7 (7.1 to 7.12): how the VM, agents, config and Slack are set up, with every lesson learned.
2. tests/scenario/bad-sleep-reschedule.md: the scenario, its pass criteria and the run log (runs 001 to 019).
3. decisions/APPROVALS.md from APR-0052 on, and decisions/PENDING.md.
4. decisions/adr/ADR-0018: Loop 1 is a cloud-only exception on synthetic data. It expires at Loop 1 close or on 2026-11-15 (APR-0052).

## How to work with the CEO
- Docs first, then the console. When the docs and the console disagree, the console wins. When the plugin code decides the question, read the code (section 7.10 is the example).
- Dry-run every config patch before applying it, and check that the dry run names ~/loop1/state/openclaw.json. A shell without ~/loop1/env.sh writes to ~/.openclaw instead.
- Any change to agent instructions or approved behaviour needs the CEO's yes, recorded as a new APR entry in his own words. Present it as a short numbered proposal and wait.
- Ask before stopping the gateway, before anything destructive, and before any step the CEO has to do by hand (Slack posts, the OpenAI usage page).
- Keep answers short when the CEO asks for that. Give commands in batches of a few steps.

## Never
- Print, paste or commit a key or token. The values live in ~/loop1/openai.env, ~/loop1/slack.env and ~/loop1/gateway-token (mode 600).
- Put Slack IDs, the VM address or account names in the repo. Slack channel IDs live in ~/loop1/slack-channels.env on the VM.
- Run git add -A in an agent workspace while state/ is dirty. Each workspace HEAD must hold the seed state, because the scenario reset restores HEAD (fix-51).
- Edit or remove a journal line. The calendar journal is append-only (APR-0054, APR-0057).
- Reuse a scenario run ID. Every attempt gets a new ID, even after a reset or a failed attempt (run 014).

## Current setup (verified 2026-10-24)
- OpenClaw 2026.10.5, model openai/gpt-6-luna, runtime pinned to openclaw (APR-0060), memory search and dreaming off (APR-0061), OpenClaw cron off, daily session reset at 04:00 (APR-0059). A plain cron line under ubuntu runs the calendar push job every 5 minutes against a Google test calendar (APR-0078, since 2026-10-26); pause it around scenario resets.
- Agents COO, CHO, CoS, CFO in ~/loop1/workspaces/<id>. Instruction sets v1.5 (APR-0066, COO) and v1.6 (APR-0067, CoS) are applied on the VM. Instruction set v1.7 (APR-0075, CHO and CoS) was applied on the VM at 01:43 AST on 2026-10-26 with deploy/loop1/loop1-v17-upgrade.sh and verified in runs loop2-scn-003 and -004 (APR-0076). Instruction set v1.8 (APR-0081, CHO only) was applied on the VM at 17:17 AST on 2026-10-26 with deploy/loop1/loop1-v18-upgrade.sh and verified in runs loop2-scn-007 and -008 (APR-0082). Instruction set v1.10 (APR-0092: CoS delete gate and overlaps, COO confirmed reports and approval requests, CFO handoff to the CoS) was applied at about 22:40 AST on 2026-10-26 with deploy/loop1/loop1-v110-upgrade.sh and the CFO send list now includes the CoS. Instruction set v1.9 (APR-0086, CHO, CoS and CFO: the privacy mark) was applied at 18:47 AST with deploy/loop1/loop1-v19-upgrade.sh; v1.9.1 (APR-0089, CoS: never edit the journal header) was applied after run 009 with deploy/loop1/loop1-v191-upgrade.sh. Both verified in runs loop2-scn-011 and -012.
- Slack: one app per agent (APR-0062), socket mode, four accounts (default = COO, cho, cos, cfo). Each account has its own channel in its allowlist, with a users list holding only the CEO's Slack ID. That list also lets "@<agent> /new" work (section 7.10). P-29 is closed.
- The CEO may address any agent in its channel; normally he talks to the COO (APR-0063).
- Health check: python3 ~/loop1/health-check.py [--live]. Last run 39 PASS, 0 FAIL, 1 WARN (old /new refusals in the log window). Some of its text is stale (P-31); see "Still to do".

## Start-up on the VM
Since 2026-10-26 (APR-0091) the gateway is a systemd user service and terminal T1 is not used: systemctl --user status|stop|start|restart openclaw-loop1-gateway (stop it before changing any AGENTS.md). The T1 command below is the manual fallback; never run it while the service runs.
Terminal 1 (gateway, owned by the CEO unless he says otherwise):

    source ~/loop1/env.sh; set -a; source ~/loop1/slack.env; source ~/loop1/openai.env; set +a; openclaw gateway run

Every other shell starts with: source ~/loop1/env.sh. Check one gateway process before tests:

    pgrep -af "openclaw.*gateway" | grep -v pgrep | wc -l      (expect 1)

## Scenario run from Slack (the current test)
1. Pause the calendar cron, save and reset the state, then compact the main sessions. Use a new run ID for every attempt:

       crontab -l | sed 's|^\*/5 .*gcal_sync_cron.sh|#&|' | crontab -
       crontab -l | grep gcal_sync      (expect: the line starts with #)
       source ~/loop1/env.sh
       W=~/loop1/workspaces; E=~/loop1/evidence/$(date +%F); mkdir -p $E
       for a in cho cos cfo; do cp -r $W/$a/state $E/<run ID>-$a; git -C $W/$a checkout -- state/; done
       T=$(cat ~/loop1/gateway-token)
       for a in cho cos cfo; do openclaw sessions compact "agent:$a:main" --agent $a --max-lines 1 --token "$T"; done
       tail -n 3 $W/cos/state/calendar-journal.md      (seed lines only)
       bash ~/lifeos-ro/scripts/gcal/gcal_sync_cron.sh; tail -n 8 ~/loop1/gcal-sync/sync.log      (pushes the seed lines to the test calendar by hand, so the run's move is a real move; expect: created, exit 0)

2. The CEO posts "@COO /new" in the COO channel, then the scenario text from the scenario file with the new run ID. The post must start with "@COO " (the agents answer only when the post starts with their name).
3. After about 2 minutes:

       git -C $W/cos diff --numstat state/calendar-journal.md      (expect no deletions: 2 0, or 5 0 when the seed lines were pushed by hand; 6 0 after the job has pushed the move)
       tail -n 2 $W/cho/state/health-plan.md
       grep -c "SESSION_WORK_START_CHANGED" /tmp/openclaw/openclaw-$(date +%F).log      (shows 0 even when the error happened: it is in the tool result, not in the log)

4. Pass: one COO reply that says the move is done, names the CHO and the CoS and gives the event IDs; one line each in the CHO and CoS channels; no "Late reply", no FAILURE note; no deletions in the numstat (criterion 4 in the scenario file); the health plan change log has the sleep fact with its own event ID (criterion 2; the move is in the journal).
5. Cost is not measured for now (CEO decision, 2026-10-24).
6. Before the next reset, export the CHO and CoS sessions and run scripts/verify/check_sessions_send.py (commands in tests/scenario/bad-sleep-reschedule.md, "Loop 2 checks under v1.7"). The checker finds the run by its run ID. Export names cannot be reused: a second export with the same name fails with EEXIST.
7. Resume the calendar cron after the checker has passed:

       crontab -l | sed 's|^#\(\*/5 .*gcal_sync_cron.sh\)|\1|' | crontab -
       crontab -l | grep gcal_sync      (expect: the line starts with */5)

## Where the runs stand
| Run | Path | Result |
|---|---|---|
| 007 | Slack, v1.2 | Partial: premature answer, duplicates; 0.047 USD |
| 008 | Slack, v1.3 | Invalid: state not at seed (upgrade commit bug, fixed) |
| 009 | Slack, v1.3 | Pass |
| 010 | Slack, v1.3 | Partial: stale "pending"; at most 0.020 USD |
| 011 | Slack, v1.4 | Fail: the CHO could not find the task on first contact; nothing written |
| 012 | CLI to the CHO, v1.4 | Pass on content (v1.4 chain works) |
| 013 | Slack, v1.4 | Content pass after a COO resend; FAILURE note shown to the CEO |
| 014 | Slack, v1.5 | Not a valid move test: run ID reused; the CHO answered from its own memory; no journal change |
| 015 | Slack, v1.5 | Pass on content: numstat 2 0, one COO reply, no late reply, no FAILURE note; cost not measured |
| 016 | Slack, v1.5 | Pass on content (VM report) |
| 017 | Slack, v1.6 | Pass on content; the CoS used the v1.6 wording |
| 018 | Slack, v1.6 | Partial: the COO named only the CHO; the CoS ran twice (no duplicate write) |
| 019 | Slack, v1.6 | Pass: one run each, COO named the CHO and the CoS, numstat 2 0; cost not measured |
| loop2-scn-001 | Slack, v1.6 (Loop 2) | Pass on content, numstat 2 0. The CHO made five sessions_send calls to the CoS (notify with watch, notify, resume twice, then followup); the CHO posted two lines in its channel; one SESSION_WORK_START_CHANGED on the CoS reply |
| loop2-scn-002 | Slack, v1.6 (Loop 2) | Pass on content, numstat 2 0. Four sessions_send calls to the CoS (the third had no details, so the CoS ran twice); three SESSION_WORK_START_CHANGED on CoS replies. The post lost its first letter ("oop 1 scenario run"); no effect |
| loop2-scn-003 | Slack, v1.7 (Loop 2) | Pass: numstat 2 0, COO named the CHO and the CoS, one CHO call to the CoS (followup), no CoS send, no SESSION_WORK_START_CHANGED; one P-37 line at the post |
| loop2-scn-004 | Slack, v1.7 (Loop 2) | Pass: same as 003, no P-37 line |
| loop2-scn-005 | Slack, v1.7 (Loop 2, cron live) | Partial: calendar path passed, and the job moved the Google event in place; the CHO did not write health-plan.md (P-39) |
| loop2-scn-006 | Slack, v1.7 (Loop 2, cron live) | Partial: calendar path passed again (the job moved the Google event in place); the CHO logged the sleep line but not the move line in health-plan.md (P-39 repeats) |
| loop2-scn-007 | Slack, v1.8 (Loop 2, cron live) | Pass: checker all passed, numstat 5 0 then 6 0, health plan has the sleep line and the move line, the job moved the Google event |
| loop2-scn-008 | Slack, v1.8 (Loop 2, cron live) | Pass: same as 007 (second in a row); P-39 closed (APR-0082) |
| loop2-scn-009 | Slack, v1.9 (Loop 2, cron live) | Partial: all passed except numstat 6 1; the CoS edited the journal header (v1.9.1, APR-0089) |
| loop2-scn-010 | Slack, v1.9.1 | Void: the CHO compaction failed after a gateway restart (prep error) |
| loop2-scn-011 | Slack, v1.9.1 (Loop 2, cron live) | Pass: numstat 5 0 then 6 0, privacy=high on both CoS lines, busy event in Google |
| loop2-scn-012 | Slack, v1.9.1 (Loop 2, cron live) | Pass: same as 011 (second in a row) |

## Known issues
- Agent memory survives a git state reset and a one-line session compaction. A reused run ID can get an answer from memory instead of the reset state. Use a new run ID for every attempt.
- First-contact miss: fixed by v1.5 (APR-0066); not seen in runs 015 to 019. In run 018 the CoS ran twice (first run took no action); cause not found at the time. Loop 2 runs 001 and 002 show the likely cause: the CHO's sessions_send arguments (notify, watch, resume) start no CoS turn. Fixed by v1.7 (APR-0075): runs 003 and 004 had one CHO call each and no CoS send (APR-0076, P-38 closed).
- SESSION_WORK_START_CHANGED: a retryable timing race in OpenClaw's session ingress; no message lost (APR-0068, P-35 closed). The CoS reports it as "delivered; acknowledgement error" (v1.6). Reopen if a session-start-conflict-retry-limit line appears. The error is in the sessions_send tool result, not in the gateway log, so a log count shows 0 even when it happened (Loop 2: 1 in run 001 and 3 in run 002, all on the CoS reply to the waiting CHO, all with sentBeforeError true). Read it with scripts/verify/check_sessions_send.py.
- COO SQLite maintenance warning about 2 seconds after each scenario post (runs 018, 019); no visible effect. P-37 closed for Loop 2 (APR-0084): one occurrence in runs 001 to 008. Reopen on a 'maintenance paused' line.
- The COO's answer sometimes names only the CHO (runs 015 and 018), though the CoS wrote the journal line. Run 019 named both. No rule change yet.
- Usage page lag: readings taken within about 20 minutes of a run may miss the charge. Cost is deferred for now.

## Still to do before Loop 1 closes
1. P-35 is closed (APR-0068). P-37 (COO SQLite warning) is for Loop 2.
2. Scenario closed (APR-0069). Loop 1 closed (APR-0071). Loop 2 allowed under APR-0073.
3. Daily reset check: P-36 is in progress (APR-0090): Claude Code reads past nights and builds a 05:00 AST Slack report. Gateway keep-alive and the real-calendar test are in the same handover. The Loop 2 close record is a draft: deploy/loop2/LOOP2-CLOSE-RECORD.md.
4. SPK-03: deferred by the CEO (APR-0070). Code Mode and the Docker sandbox were not tested.
5. Health check: updated on the VM by the VM agent (it reported 41 PASS). The repo copy, deploy/loop1/health-check.py, is not updated yet; bring the VM patch in through a fix script.
6. CEO housekeeping on the Mac: delete ~/Downloads/spk04-transfer (it holds old secrets) and old copies of health-check.py and the upgrade scripts.
7. Loop 1 close record: deploy/loop1/LOOP1-CLOSE-RECORD.md, signed off (APR-0071).
8. P-38 is closed (APR-0076) and P-28 is closed (APR-0080): the calendar push job is built, tested on the VM and running by cron every 5 minutes against the Google test calendar (guides/calendar-sync-job.md; pause it around scenario resets). P-39 is closed (APR-0082): v1.8 was verified by runs 007 and 008. P-31 (APR-0083), P-37 (APR-0084) and P-32 (APR-0085) are closed for Loop 2. Privacy rule decided (APR-0086): the chief marks it, health and finance default to high; it is built, applied and verified (v1.9, v1.9.1; APR-0088, APR-0089; runs 011 and 012). Still open: P-40 (real calendar, archive job), P-41 (memory beyond the state files, deferred).
9. Gateway ownership: the gateway is the systemd user service openclaw-loop1-gateway (APR-0091); it restarts after a crash and at boot, logs to ~/loop1/gateway.log, and survives the CEO closing his laptop. The batches that check for exactly one gateway process still work. A 05:00 AST cron posts the daily reset report to the COO channel (P-36).
10. Note from the handover: the COO's wording to the CHO sometimes includes "avoid duplicating an already-handled event"; with a stale CHO session (not compacted) the CHO can skip the move. It did not appear in runs 011 and 012. Compact every session and read the output (see the scenario file).
11. Handover 3 (2026-10-26 evening): health check now 53 checks (deploy/loop1/health-check.py, 53 PASS on the VM); one-command runner ~/loop1/scenario-run.sh prep|check <RUN> (copy in deploy/loop2/vm/); scenarios 013 to 017 (delete gate failed, privacy passed, CFO and overlap partial). Decisions APR-0092; instruction set v1.10 built, not yet applied (P-42).
12. Handover 4 (2026-10-26 night): v1.10 applied, CFO send list coo+cos, runs 018 to 025 (7 pass, 1 fail), GCAL_ALLOW_DELETES=1 on in the cron (test calendar only; see P-42). Health check 54 checks reported. Runner note: ~/loop1/scenario-run.sh and deploy/loop2/vm/h4-post.sh (posts progress lines to the COO channel, stops after 02:30 AST).
13. APR-0093 (2026-10-26): instruction set v1.10.1 built (deploy/loop1/loop1-v1101-upgrade.sh), not yet applied. Delete flag stays ON on the test calendar; no move to the real calendar until D1 passes three times in a row.
14. Handover 5 (2026-10-26 night): v1.10.1 applied (cos bd4b8cd, coo 8cae25a), D1 passed three in a row, D2 one partial (privacy=high on delete lines, P-42). Delete flag ON on the test calendar. Last agent message 23:56 AST.
