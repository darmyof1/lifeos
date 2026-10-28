# Install and change log (sanitized)

Append-only. One dated entry for each change on any host. Secrets, tokens, authorization codes, and personal values never go in this file. Raw transcripts stay in your private seed folder.

## 2026-10-15 — Oracle VM — gcalcli (calendar)
Host: Oracle VM, Ubuntu 24.04 arm64 (hostname not recorded here).
- Removed the apt package gcalcli 4.3.0 (it has no `init` command).
- Installed pipx and python3-venv. Ran `pipx ensurepath`. Added `~/.local/bin` to PATH in `~/.bashrc`.
- `pipx install gcalcli` gave version 4.5.1.
- Created the Google Cloud OAuth client (Desktop app). Values kept in the password manager.
- Authenticated with `gcalcli --client-id=... init` through an SSH tunnel to the redirect port.
- Read test: `gcalcli list` and `gcalcli agenda` passed.
- Write test: added "LifeOS write test" to the primary calendar at 17:00. Visible in agenda. Deletion from the web app still to confirm.
- ACTION (owner: CEO): the client secret appeared in a chat transcript. Reset it in Google Cloud Console and update the password manager. Status: open until reset is confirmed.
Guide: guides/calendar-gcalcli.md

## 2026-10-15 — CEO Mac — AI command-line tools
Host: CEO Mac (macOS, zsh).
- `claude -p "<prompt>" --dangerously-skip-permissions`: returned and created a file. Permission flag was required for the write.
- `codex exec "<prompt>" --sandbox danger-full-access`: returned and created a file. The `--full-auto` flag is not accepted by Codex v0.162.1.
- `agy`: not run. Account usage limit. Deferred.
- Both file writes left `test123.txt` in the repo folder. It is untracked. Delete it before the next commit.
Evidence: research/spikes/SPK-05-cli-adapters.md

## 2026-10-16 — CEO Mac — test corrections
- test123.txt had been committed by fix-9 (the stray file was in the repo folder during `git add -A`). Removed in this fix. Blocked by the validator from now on.
- Two timing methods were tested. The `PIPESTATUS` method gives an empty exit code in zsh. The `$?` method works. See guides/measure-a-cli-call.md.
- SPK-05 corrected: Codex writes files by default, so the earlier conclusion was wrong for Codex.
- Delete-by-ID steps added to guides/calendar-gcalcli.md.

## 2026-10-16 — repo — fix-11
- The fix-10 that ran on the Mac was an older version. It did not include validator check 12 or guide rule 6. fix-11 adds them.
- The registry generators (fix-4 to fix-10) listed files from the disk, so local git-ignored files such as execution.log appeared in the registry. The validator then failed on any clean clone. fix-11 generates the registry from git's tracked-file list. Use this method in all future scripts.
- Local test output stays outside the repo or in ignored paths.

## 2026-10-16 - decisions and tests
- APR-0032: calendar content in Google is titles only for now (changeable by a new APR entry). contracts/policy/calendar.yaml added as a draft.
- APR-0033: ADR-0003 accepted.
- Test logs moved from the AI workbench to ~/lifeos-ops/logs (outside the repo). Create it once with mkdir -p.
- Calendar guide: search and delete commands added, with <calendar-email> placeholder.
- SPK-06 done: 3.68 tokens per second. Triage latency opened as P-14.

## 2026-10-16 - naming mandate
- APR-0034: calendar event names follow "<DOMAIN> - <Title> - <MMDDYYYY>-<NNNN>". Interpretation open in P-15.
- P-14 rewritten in plain language.

## 2026-10-16 - calendar command tests (fix-14)
- Tested on the Oracle VM with gcalcli 4.5.1: create two events, search by full title, search with a date range, agenda, delete by title with --iamaexpert. Delete printed "Deleted!". Calendar email kept out of the repo.
- End dates are excluded in search and agenda. 2026-10-18 is needed to include 2026-10-17.
- Delete by event ID: rejected. The delete command takes search text, and --noprompt is not valid for delete ("unrecognized arguments: --noprompt"). The event IDs are Google's own IDs (gcalcli reads them from the Google API), but delete does not accept them. The guide now uses the full title.
- Not yet confirmed on the VM: the --details id --tsv column layout. The add command prints nothing on success; success was confirmed by search (the Google Calendar web app check is still to be done).
- APR-0035: P-15 approved (date order, counter per date, domain codes). APR-0037: meanings of the codes (CFA Family, CFO Finance, CSO Social). APR-0036: P-14 accepted for now (about 20 seconds triage). P-14 and P-15 closed.

## 2026-10-16 - model probe and token path (fix-17)
- SPK-09: claude-haiku-5-5 accepted by the API (HTTP 200) and by the CLI. Account identifiers removed. Exit codes of the CLI runs were not captured (zsh PIPESTATUS issue).
- Calendar token path corrected: gcalcli 4.5.1 stores the OAuth token at ~/.local/share/gcalcli/oauth. The guide used ~/.gcalcli_oauth. A test host showed no file at the old path. Confirmation on the VM is pending (P-13).

## 2026-10-16 - token check on the VM (fix-18)
- Token file found at ~/.local/share/gcalcli/oauth, owner ubuntu. Mode was 664, changed to 600 and confirmed with stat. P-13 awaits CEO yes.
- P-08 approved (APR-0040).

## 2026-10-16 - P-13 approved (fix-19)
- APR-0041: calendar token location confirmed on the VM. P-13 closed.

## 2026-10-16 - P-18 approved (fix-21)
- APR-0042: ADR-0002 accepted, including the tie-break. P-19 (scenario catalogue) still open.

## 2026-10-16 - P-19 approved (fix-22)
- APR-0043: scenario catalogue approved. S-06 (5-minute retry, COO escalation at attempt 5) and S-07 (CIO Slack alert) changed by the CEO. P-19 closed.

## 2026-10-16 - Slack exemption (fix-24)
- APR-0045: private data may be posted in private Slack channels until the in-house app exists. Model calls still pass the gate. privacy.yaml header corrected (not yet enforced in code).

## 2026-10-16 - P-20, P-21, P-22 approved (fix-25)
- APR-0046: instruction drafts from approved rules (CSTO). APR-0047: LLM call log approved, CISO leak check added. APR-0048: Slack model, one app and one channel per agent.
- New pending: P-23 (agent-to-agent visibility), P-24 (leak check detail).

## 2026-10-16 - P-24 approved (fix-26)
- APR-0049: CISO leak check scans all sources weekly and reports directly to the CEO. P-24 closed.

## 2026-10-16 - P-23 approved (fix-27)
- APR-0050: cross-agent visibility approved. Real-world changes and failures are posted to Slack; routine traffic stays in the call log. P-23 closed.

## 2026-10-16 - CHO scenarios drafted (fix-28)
- design/cho-scenarios.md: C-01 to C-06 (draft). P-25 pending with six questions.

## 2026-10-16 - P-25 approved (fix-29)
- APR-0051: CHO owns therapies (CSP proposes); therapy titles show the name; CIO owns alarms and needs an alarm skill; supplement timing free; meal plans local for now. P-25 closed.

## 2026-10-17 - VM spike runbook added (fix-30)
- guides/vm-spike-runbook.md: steps for SPK-07, SPK-01, SPK-02, SPK-03, SPK-04. No spike run yet.

## 2026-10-18 - SPK-07 Part A run (fix-31)
- Part A: passphrase cache found and cleared before decrypt. Wrong passphrase fails (Bad session key, exit 2). MATCH line pending rerun. Part B (asymmetric) added to the runbook, not run.

## 2026-10-18 - SPK-07 done (fix-32)
- Part A (passphrase) and Part B (public key on the VM, CEO restores) passed. Runbook Part B corrected (encryption subkey). Decision on archive encryption left to the CEO (APR-0010 / ADR-0012).

## 2026-10-18 - SPK-01 done (fix-33)
- Per-user outbound block works: test user blocked from the internet, loopback open, ordinary user unaffected. Limits: not tested on an OpenClaw process; rule not persistent.

## 2026-10-18 - SPK-02 partial (fix-34)
- OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH move setup's state; the default state is unchanged. Gateway check open.

## 2026-10-18 - SPK-02 done (fix-35)
- OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH move state for setup, status and the gateway. Logs go to /tmp. Gateway auth none at runtime; default model is cloud.

## 2026-10-18 - SPK-03 partial (fix-36)
- Two test agents with separate workspaces; sandbox mode off by default; Docker not installed (deferred to deploy).
- Isolation-off canary not obtained: local model turns did not complete on this VM. Plain Ollama answers in seconds; OpenClaw turns with the tool catalog did not.
- Added guides/local-model-setup.md.

## 2026-10-19 - SPK-04 Part A done (fix-37)
- Two Slack apps (From a manifest), two accounts in one Gateway on port 19001, two agents bound to their accounts.
- Each agent posted as its own identity (spk04-b APP, spk04-a APP). Runs: 14.7 s and 22.1 s with a hosted model.
- Leakage check limited: the account argument of a send is not in the stored transcript. Part B not run.
- Added guides/slack-multi-identity.md and research/spikes/SPK-04-slack-multi-identity.md.

## 2026-10-19 - SPK-04 cleanup verified (fix-38)
- Top-level Slack tokens removed; gateway auth token saved; both accounts connect; spk04-b direct send posted as spk04-b APP.
- Incident: a gateway stop run without the state variables stopped the default openclaw-gateway.service. Restarted with systemctl --user start. Variables now set per terminal (env.sh).
- Incident: a second gateway run on the same state folder caused a stall and a Slack socket error. Stopped; the first gateway reconnected.

## 2026-10-19 - SPK-04 model verified (fix-39)
- Utility model set explicitly to openai/gpt-6-luna (it had been the provider default gpt-5.6-luna).
- Old OpenAI keys revoked; one project key (life-os) remains in the spk04 env file.
- Billing re-check pending for the next day.

## 2026-10-20 - SPK-04 binding, channel and owner checks (fix-40)
- spk04-b binding verified by a mention. Event subscription and app_mentions:read added in the Slack app settings. Channel allowlist entry added.
- /new still refused (control-command-unauthorized). commands.ownerAllowFrom tried, not effective.
- A thread turn was served by openai/gpt-6-luna. Part B paused.

## 2026-10-20 - SPK-04 billing re-check (fix-41)
- gpt-6-luna is the only billed model in the test. gpt-5_6-luna shows $0. Billing confirmed.

## 2026-10-21 - SPK-04 close-out on AWS (fix-42)
- New guide: guides/openclaw-and-ollama-install.md.
- guides/local-model-setup.md updated: tool calling settings and proof, troubleshooting rows, open items.
- Instance terminated. Transfer copies on the Mac must be deleted by hand.

## 2026-10-22 - Loop 1 decisions recorded (fix-43)
- APR-0052 to APR-0056 and ADR-0018: time-boxed cloud-only exception, Slack test, local calendar journal, instruction approval, cost limits.
- PENDING P-26 to P-29 added. SPK-10 planned.

## 2026-10-22 - Loop 1 baseline on the Oracle VM (fix-44)
- State folder ~/loop1/state created; config written by patch (model gpt-6-luna, utility model, messaging profile). Validated; no secrets in the file.
- Old key copy removed; a new key stored in ~/loop1/openai.env (names checked only).
- Agent commands read from help text; not run. See guides/loop1-baseline.md.

## 2026-10-22 - Agent tests on the Oracle VM (fix-45)
- Four agents added (COO, CHO, CoS, CFO) with the gateway stopped; first-run files removed.
- Agent-to-agent allow lists, sessions visibility (agent) and sub-agent limits set by patch.
- File tools enabled for CoS, CHO and CFO with workspaceOnly. A handoff from CHO to CoS and a diet change from CHO to CFO both passed.
- Details and results: guides/loop1-baseline.md, section 7.

## 2026-10-22 - Bad-sleep scenario runs on the Oracle VM (fix-46)
- Run 1 failed (no event ID rule), run 2 partial (journal edited in place), run 3 passed criteria 1 to 5.
- CEO ruling on moves recorded as APR-0057; instruction set v1.1 and v1.2 recorded as APR-0058.
- Approved instruction script copied to deploy/loop1/loop1-agent-files.sh. P-28 updated with the journal size and status points.

## 2026-10-22 - Repeatability, restart and session tests on the Oracle VM (fix-47)
- Bad-sleep runs 3 to 5 passed in a row. Run 6: restart mid-flow failed cleanly; the retry wrote once; a resend of the finished run wrote nothing.
- Daily session reset at 04:00 AST set by patch (APR-0059). Main sessions compacted to one line.
- Open: runtime label OpenAI Codex (P-30); the OpenAI spend limit is not enforced (P-31).

## 2026-10-23 - Runtime pin, memory off and health check on the Oracle VM (fix-48)
- Runtime for openai/gpt-6-luna pinned to openclaw (APR-0060); P-30 closed.
- Memory search and dreaming turned off (APR-0061); memory design opened as P-32.
- Health check added (deploy/loop1/health-check.py). First VM run: offline and live, no FAIL.
- Daily reset seen: the CoS main session got a new session ID at the first message after 04:00.

## 2026-10-24 - Slack apps per agent and isolation tests on the Oracle VM (fix-49)
- Spike 10: one app failed for handoff posts; one app per agent passed (APR-0062, changes APR-0048). P-27 closed.
- Four Slack accounts, bindings, per-account channel allowlists and identities set by patch. Probe: four accounts connected.
- SPK-03 on Loop 1: canary, shell and transcript checks refused as expected; Code Mode and sandbox not tested.
- P-31 updated: OpenAI limit enforced. P-33 opened: do the other agents answer the CEO directly.

## 2026-10-24 - First Slack-driven scenario run and instruction set v1.3 (fix-50)
- loop1-scn-007 from the COO channel: journal correct, Slack view not (premature answer, late report, duplicates). Cost about 0.047 USD.
- APR-0063: any agent may be addressed, the COO is the normal door (P-33 closed). APR-0064: instruction set v1.3.
- deploy/loop1/loop1-v13-upgrade.sh added; not yet applied on the VM.
- P-29 and P-32 updated.

## 2026-10-24 - v1.3 upgrade commit bug and run 008 (fix-51)
- The first loop1-v13-upgrade.sh committed the dirty state/ files with git add -A; the seed reset then restored the run-007 state. Run 008 was invalid.
- Script corrected (commits AGENTS.md only); the VM workspaces are repaired by hand (steps in guides/loop1-baseline.md section 7.9).

## 2026-10-24 - /new solved, runs 009 and 010, instruction set v1.4 (fix-52)
- /new in Slack works once each channel has a users list (CEO Slack ID); P-29 closed by that finding.
- loop1-scn-009 passed in Slack. loop1-scn-010 was partial (stale pending report); cost at most 0.020 USD.
- APR-0065: instruction set v1.4; deploy/loop1/loop1-v14-upgrade.sh added, not yet applied on the VM.

## 2026-10-24 - Runs 011 to 013, v1.5 proposed, VM handoff (fix-53)
- v1.4 applied on the VM. Run 011 failed, run 012 (CLI) passed on content, run 013 passed on content after a resend.
- P-34 (v1.5, COO handoff rule) and P-35 (SESSION_WORK_START_CHANGED) opened. deploy/loop1/loop1-v15-upgrade.sh added, not applied.
- deploy/loop1/STATE.md added: the handoff for a Claude Code session on the VM.

## 2026-10-24 - v1.5 approved (fix-54)
- APR-0066: instruction set v1.5 approved; P-34 closed. Not yet applied on the VM when this was written.
- deploy/loop1/STATE.md: v1.5 status and a repo-access note (read-only clone on the VM; the Mac writes).

## 2026-10-24 - Runs 014 and 015 recorded (fix-55)
- Run 014: not a valid move test. Its run ID was reused after an attempt that got partway; the CHO answered from its own memory. Rule: never reuse a run ID.
- Run 015 (v1.5): pass on content, no late reply, no FAILURE note, journal numstat 2 0. Cost deferred by the CEO.
- P-35 updated: the CoS logged a session-start error on its reply to the CHO; content still delivered.

## 2026-10-24 - Handoff rewritten after runs 014 and 015 (fix-56)
- deploy/loop1/STATE.md rewritten: v1.5 applied on the VM, runs 014 and 015 recorded, rule against reusing run IDs, and how findings from the VM come back to the repo (paste the report; fix script; no push from the VM).

## 2026-10-25 - P-35 kept open; CoS wording changed (fix-57)
- APR-0067: CEO said keep P-35 open and change the CoS's wording. v1.6 script added (deploy/loop1/loop1-v16-upgrade.sh), not yet run on the VM.
- P-35: the session-start wording appears only in agent replies; nearest gateway lines are SQLite session messages. Cause still open.

## 2026-10-25 - Runs 016 and 017 recorded; P-35 log finding; P-36 pending (fix-59)
- Run 016 (VM report): pass on content under v1.5. Run 017: pass on content under v1.6; the CoS used the new wording; no raw gateway error line for the acknowledgement.
- P-35 stays open; one more run with a wider capture is planned.
- P-36 (04:00 reset check) is pending and not raised for now, as the CEO asked.

## 2026-10-25 - P-35 closed; runs 018 and 019 recorded (fix-60)
- APR-0068: P-35 closed. SESSION_WORK_START_CHANGED is a retryable race in OpenClaw's session ingress; no dropped message in the logs; v1.6 wording stays.
- Run 018: partial (COO named only the CHO; CoS ran twice, no duplicate write). Run 019: pass.
- P-37 opened: COO SQLite maintenance warning at scenario start (Loop 2).
- deploy/loop1/STATE.md updated for runs 016 to 019, v1.6, P-35 closed, P-36 pending.

## 2026-10-25 - Scenario closed; SPK-03 deferred; Loop 1 close record drafted (fix-61)
- APR-0069: scenario bad-sleep-reschedule closed after Claude's log review (run 019 clean under v1.6); cost deferred.
- APR-0070: SPK-03 deferred by the CEO.
- deploy/loop1/LOOP1-CLOSE-RECORD.md added. Loop 1 is not closed yet: that needs the CEO's sign-off and ends the APR-0052 exception.

## 2026-10-25 - Loop 1 closed (fix-62)
- APR-0071: the CEO closed Loop 1. APR-0052 and ADR-0018 expire; the suspended entries apply again.
- The Loop 1 gateway stays stopped unless a new APR entry allows it. Close record signed off.

## 2026-10-25 - Sandbox drafts imported; CEO answers recorded (fix-63)
- research/sandbox/2026-10-25-agy/: overnight drafts by a sandboxed VM agent (research input, not decisions).
- deploy/loop1/health-check.py: VM version with Slack account, channel users list and connection checks.
- APR-0072: calendar journal 14-day active window and monthly archive. P-26 deferred. P-31 kill switch can wait. P-37 kept open.

## 2026-10-25 - Loop 2 approved (fix-64)
- APR-0073: Loop 2 runs cloud-only on synthetic data until Loop 2 closes or 2026-12-31. The CEO runs the gateway from the main account.
- Synthetic events may go to the CEO's Google Calendar; deletes need his approval (APR-0044). Loop 2 cost limits deferred (P-31).

## 2026-10-25 - Calendar login renewed; REST scripts added (fix-65)
- The gcalcli login expired (invalid_grant). The OAuth app was in Testing mode. The CEO published it (In production), made a new client secret and logged in again. gcalcli add, list, agenda and delete by title work again.
- Test on the VM: gcalcli has no ID option for edit or delete. REST create, move, read and delete by event ID passed with an ad hoc script.
- APR-0074: moves and deletes by event ID use REST scripts in scripts/gcal/. gcalcli and its guide stay. Added guides/calendar-rest-api.md and tests/unit/test_gcal_scripts.py (unit tests, no network).
- To do on the VM: pull, run the unit tests, run the round-trip test from the repo scripts, record the google-api-python-client version.

## 2026-10-25 - Calendar REST scripts run on the VM (fix-66)
- Pulled the repo on the VM. Unit tests: 59 OK with the gcalcli Python. google-api-python-client 2.201.0.
- The scripts refused the new login file because gcalcli init left it open to others; fixed with chmod 600 (mode checked: 600, owner ubuntu).
- scripts/gcal/gcal_list.py listed the two events of the day with their IDs. gcal_roundtrip_test.py created, moved, read by ID and deleted one test event (title counter 9001); gcal_find.py then found 0 matches and gcalcli agenda showed no test event.
- guides/calendar-rest-api.md is now marked working. Not yet run alone on the VM: the create, move, get and delete scripts (run only inside the round trip).

## 2026-10-26 - Loop 2 runs 001 and 002 read from the trajectory; instruction set v1.7 (fix-67)
- Runs loop2-scn-001 and loop2-scn-002 recorded (scenario file, STATE.md). Both passed on content.
- The trajectory exports showed why the CoS sometimes runs twice: the CHO's sessions_send set mode notify and watch true, which start no CoS turn. APR-0075: instruction set v1.7 (the CHO's exact call; the CoS replies by answering).
- Added deploy/loop1/loop1-v17-upgrade.sh (run with --dry-run first), scripts/verify/check_sessions_send.py and unit tests for both. P-38 tracks the check in two runs.
- P-37: 0 occurrences in the two runs; stays open.
- STATE.md: the post must start with @COO; a gateway-log count cannot show SESSION_WORK_START_CHANGED.
- To do on the VM: pull, stop the gateway, run the upgrade script with --dry-run and then for real, start the gateway, run the scenario twice and run the checker.

## 2026-10-26 - Instruction set v1.7 applied and verified (fix-68)
- v1.7 applied on the VM at 01:43 AST (dry run first, gateway stopped, health check 43 PASS). Runs loop2-scn-003 and loop2-scn-004 passed: one CHO sessions_send each, no CoS send to the CHO, no SESSION_WORK_START_CHANGED, journal numstat 2 0.
- APR-0076: P-38 closed. The config option (CoS send list without cho) is not needed.
- P-37: one occurrence at the run 003 post (01:55:50 AST), none in run 004; stays open.
- scripts/verify/check_sessions_send.py now finds the run by its run ID (no --since needed); 6 more unit tests.
- Runs 003 and 004 recorded in the scenario file and STATE.md.

## 2026-10-26 - P-28 status set and push job approved (fix-69)
- APR-0077: the Loop 2 calendar status set (requested, written, pushed, failed, conflict, moved, delete-pending-approval) and the code push job (5-minute retry, search by unique name first, COO told after 5 failures, writes pause if the token is revoked) approved as proposed. The sandbox draft is not approved as a whole.
- P-28 stays open: the job is not built, and six points are listed in PENDING (alert target without a CIO, status of an approved delete, high-privacy busy title, what starts the job, create tool, journal line format).

## 2026-10-26 - P-28 push job built (fix-70)
- APR-0078: alerts in the COO channel, delete status "deleted", high-privacy busy deferred until before real data, plain cron under ubuntu every 5 minutes.
- Added scripts/gcal/gcal_sync.py, scripts/gcal/gcal_sync_cron.sh, tests/unit/test_gcal_sync.py, tests/unit/test_gcal_sync_cron.py and guides/calendar-sync-job.md. Unit tests only; nothing was run on the VM and no cron line was added.
- P-28 stays open until the job has run on the VM.

## 2026-10-26 - P-28 push job tested on the VM (fix-71)
- On the VM as ubuntu, from ~/lifeos-ro at 17bb327, against a separate Google test calendar and a test journal in ~/loop1/gcal-sync-test: dry run, create, rerun with no change, move with a new title, conflict, delete gate (three cases), alert in the COO channel, and the cron wrapper by hand in dry-run mode. All as expected.
- Created on the VM (not in the repo): ~/loop1/gcal-sync/env (mode 600, holds the calendar ID and the alert target), ~/loop1/gcal-sync/sync.log, ~/loop1/gcal-sync-test/. No cron line installed. The test event was deleted through the job's delete gate.

## 2026-10-26 - P-28 push job cron installed (fix-72)
- CEO: "cron on the test calendar". On the VM as ubuntu: one line added to the ubuntu crontab, "*/5 * * * * bash $HOME/lifeos-ro/scripts/gcal/gcal_sync_cron.sh", next to the existing stress-ng line. The settings file ~/loop1/gcal-sync/env points at the Google test calendar and the COO channel.
- Dry run first against the real CoS journal: three entries to create, as expected. First cron run 13:35 AST: three events created; run 13:40: pushed 0.
- Scenario runs now pause and resume this cron line (tests/scenario/bad-sleep-reschedule.md, deploy/loop1/STATE.md, guides/calendar-sync-job.md).

## 2026-10-26 - P-28 failure paths tested; high-privacy busy built (fix-73)
- On the VM, test calendar, throwaway folders ~/loop1/gcal-sync-fail and ~/loop1/gcal-sync-revoke: five failed attempts counted correctly; a revoked login (broken copy of the login file) paused all writes with one alert. The alert reached the COO channel once the gateway (T1) was running. Cleanup of one stray test event with the CEO's approval.
- APR-0079: high-privacy events show as busy, built now and tested with fake data. Added scripts/gcal/gcal_busy.py and 14 tests; scripts/gcal/gcal_sync_cron.sh now loads ~/loop1/env.sh first.

## 2026-10-26 - P-28 high-privacy busy events tested on the VM (fix-74)
- On the VM, T2, test calendar, fake data in ~/loop1/gcal-sync-hp: create as busy, no mandated title in Google, rerun with no change, move without a mark on the new line (privacy followed the move), delete gate with and without --allow-deletes. 116 unit tests OK on the VM. Both fake events were deleted by the test (CEO approval in the batch).
- The scenario procedure now pushes the seed lines by hand after the state reset, and the test calendar is cleaned of leftover events before a run.

## 2026-10-26 - Scenario run loop2-scn-005 with the calendar cron (fix-75)
- Cron paused, leftover test event deleted, state reset, sessions compacted, seed lines pushed by hand; run loop2-scn-005 posted in Slack; checker passed; job run by hand after the run (moved the Google event in place); cron resumed.
- The CHO did not write state/health-plan.md in this run (P-39 opened). Scenario criterion 4 now allows the lines the job appends.

## 2026-10-26 - P-28 closed (fix-76)
- CEO: "close p28" (APR-0080). The calendar push job, cron wrapper, tests and guide stay as built. The leftovers for real data are in P-40.

## 2026-10-26 - Scenario run loop2-scn-006 with the calendar cron (fix-77)
- Same procedure as run 005 (cron paused, leftover event deleted with the CEO's approval, state reset, sessions compacted, seeds pushed by hand; post; checks; job by hand; cron resumed only after the checker passed). Checker passed; the job moved the Google event in place. numstat 5 0, then 6 0.
- P-39 repeats in part: the CHO logged the sleep line but not the move line in health-plan.md. A CHO rule (v1.8) is proposed in P-39 and waits for the CEO.

## 2026-10-26 - P-39 root cause found (fix-78)
- Read-only look at the CHO trajectory exports of runs 005 and 006 on the VM: the CHO read the health plan, wrote the sleep line in run 006 and treated the move as recorded by the CoS in the journal; the COO's message to the CHO differed between the runs (sleep as background in 005, as a task in 006). P-39 rewritten with the causes and three options (A, B, C); nothing changed in the agents.

## 2026-10-26 - P-39 option A decided; v1.8 script built (fix-79)
- CEO: "lets go with A as recommended." (APR-0081). Added deploy/loop1/loop1-v18-upgrade.sh (CHO only, AGENTS.md only, gateway stopped) and tests/unit/test_loop1_v18_upgrade.py (7 tests). Not applied on the VM yet.
- Scenario criterion 2 reworded (sleep fact with its own event ID; the move is in the journal).

## 2026-10-26 - v1.8 applied and verified; P-39 closed (fix-80)
- v1.8 applied on the VM at 17:17 AST with deploy/loop1/loop1-v18-upgrade.sh (CHO AGENTS.md only; commit d26a5e8 in the CHO workspace).
- Runs loop2-scn-007 and loop2-scn-008 passed in a row (cron live on the test calendar, paused for each reset and resumed after the checker). CEO: "yes close p39" (APR-0082).

## 2026-10-26 - P-31, P-37, P-32 closed; privacy rule decided (fix-81)
- CEO closed P-31 (APR-0083), P-37 (APR-0084) and P-32 with the narrow version (APR-0085); ADR-0011 written; new item P-41 holds the deferred memory questions.
- CEO approved "the chief marks it, health and finance default to high" (APR-0086) and confirmed the busy block in the Google Calendar app (APR-0087). The v1.9 instruction script is not built yet.

## 2026-10-26 - v1.9 script and privacy job change built (fix-82)
- deploy/loop1/loop1-v19-upgrade.sh (CHO, CoS, CFO; AGENTS.md only) and tests/unit/test_loop1_v19_upgrade.py (8 tests). Not applied on the VM.
- gcal_busy.make_busy and its use in gcal_sync.py (a normal event becomes busy when its entry is marked high); gcal_delete.py --busy-key. Unit-tested; to be tested on the VM. APR-0088.

## 2026-10-26 - v1.9 applied; v1.9.1 after run 009 (Claude Code handover, fix-83)
- v1.9 applied on the VM at 18:47 AST. Run 009: the CoS edited the journal header (numstat 6 1). Claude Code (CEO handover) found the cause in the CoS trajectory and applied v1.9.1 (CoS AGENTS.md, commit 78b71ff). Runs 011 and 012 passed; 010 is void (prep error).
- Added deploy/loop1/loop1-v191-upgrade.sh, tests/unit/test_loop1_v191_upgrade.py (7 tests) and ops/handover-2026-10-26-claude-code-report.md. APR-0089. The gateway now runs from Claude Code's shell, not T1.

## 2026-10-26 - Loop 2 next steps decided; close record drafted (fix-84)
- APR-0090: P-36 becomes a 05:00 AST Slack report (history of past nights first); the gateway must keep running without a terminal; a real-calendar test is authorized (test events only, cron stays on the test calendar); the archive job is deferred.
- deploy/loop2/LOOP2-CLOSE-RECORD.md drafted (not signed). Handover prompt 2 given to Claude Code on the VM.

## 2026-10-26 - Handover 2 recorded (fix-85)
- Claude Code (CEO handover, APR-0090): gateway now a systemd user service; 05:00 AST reset report cron; P-36 history read; real-calendar test passed. APR-0091.
- Added deploy/loop2/vm/ (openclaw-loop1-gateway.service, daily-reset-report.sh, daily-reset-report.py), tests/unit/test_daily_reset_report.py (5 tests), ops/handover-2026-10-26-claude-code-report-2.md and ops/realcal-test-journal-2026-10-26.md.

## 2026-10-26 - Handover 3 recorded; instruction set v1.10 built (fix-86)
- Claude Code: health check with 12 Loop 2 checks (53 PASS), scenario runner, run-cost estimate, four new scenario files; runs 013 to 017 (about 0.03 USD in total, estimate).
- CEO "yes to all, proceed" (APR-0092): delete gate, cron deletes behind GCAL_ALLOW_DELETES=1, approval request format, CFO to CoS, overlap log, confirmed reports. deploy/loop1/loop1-v110-upgrade.sh and 8 tests; 2 cron tests. Not applied on the VM (P-42).

## 2026-10-26 - Handover 4 recorded (fix-87)
- Claude Code applied v1.10 (coo 52e4ac9, cos c867da5, cfo c5dd57e), added the CoS to the CFO's send list, ran loop2-scn-018 to 025 (7 pass, 1 fail) and turned GCAL_ALLOW_DELETES=1 on in the cron (the cron deleted the test event at 23:15). Health check reported 54 PASS.
- Repo: updated health-check.py and scenario-run.sh, added h4-post.sh, the report and the CFO diff. Decisions pending in P-42.

## 2026-10-26 - APR-0093 and v1.10.1 built (fix-88)
- Built deploy/loop1/loop1-v1101-upgrade.sh (CoS delete order and event ID; COO delete requests and approval layout). Not applied; Claude Code applies it in handover 5.

## 2026-10-27 - Handover 5 recorded (fix-89)
- Claude Code applied v1.10.1 (cos bd4b8cd, coo 8cae25a), ran 027 to 032 (D1 x3 pass, D2 partial then pass, regression pass). Repo: report 5 and h4-d1.sh added. No new decision recorded.

## 2026-10-27 - APR-0094 and v1.10.2 built (fix-90)
- Built deploy/loop1/loop1-v1102-upgrade.sh (CoS: no privacy mark or detail on delete lines). Not applied; Claude Code applies it in handover 6.

## 2026-10-27 - Handover 6 recorded (fix-91)
- Claude Code applied v1.10.2 (cos 918b843), updated the live health check (54 PASS), ran 033 to 039 (D2 4 of 5, D1 and regression pass). Repo: health-check.py, h6-d2.sh, report 6, health-check output, per-run results. No new decision recorded.

## 2026-10-27 - APR-0095 and v1.10.3 built (fix-92)
- CEO approved the COO seven-item rule. Built deploy/loop1/loop1-v1103-upgrade.sh (COO only). Not applied; Claude Code applies it in handover 7.

## 2026-10-27 - Handover 7 recorded (fix-93)
- Claude Code applied v1.10.3 (coo 89d43c9), updated the live health check (54 PASS), ran 041 to 045 (D2 three in a row, D1 and regression pass). Repo: report 7, health-check output, per-run results. No new decision recorded.

## 2026-10-27 - Loop 2 signed off (fix-94)
- APR-0096 recorded: Loop 2 closed, APR-0073 ends, P-42 and P-40 item 2 closed, P-36 stays a watch item. Close record signed.
- Repo fix for the "up unknown" uptime in the 05:00 report (cron has no user systemd bus: XDG_RUNTIME_DIR in the wrapper plus a pgrep fallback). The VM copies in ~/loop1/ are not changed by this script; Claude Code copies them from the repo.

## 2026-10-27 - Documentation reconciled after the external reviews (fix-95)
- deploy/loop1/STATE.md rewritten as the current state; its earlier text kept unchanged in deploy/loop1/STATE-HISTORY-2026-10-27.md.
- LOOP2-CLOSE-RECORD.md: errata section (coverage to APR-0096, v1.10 to v1.10.3, measured costs); signed sections unchanged.
- PENDING.md: P-09 summary line matches its detail; P-42 added to the closed list.
- README.md written (status and where to start). .gitignore already ignores Python and pytest caches; no change needed.
- No decision recorded; no VM change.

## 2026-10-27 - Loop 3 scope recorded (fix-96)
- APR-0097 and P-43. STATE.md and README updated; the cost line in STATE.md now says the kill is an OpenAI-side setting, not our code. No VM change.
