# LifeOS VM state and handoff (as of 2026-10-27, 11:40 AST)

Loop 1 is closed (APR-0071). Loop 2 is closed (APR-0096, signed 2026-10-27) and APR-0073 has ended. Loop 3 scope is approved (APR-0097, P-43): rebuildable repo, structure test, privacy gate in code, security minimum, identity-access contract, then one real feed after a separate yes.
The Loop 2 setup keeps running on the VM as it is, on synthetic data only, until the CEO records a Loop 3 APR or says to stop (APR-0096).

Written for a Claude Code session on the VM and for the planning chat. Read this first. Nothing here is a decision: decisions live in decisions/APPROVALS.md, open questions in decisions/PENDING.md. The history of how this state was reached (run tables, earlier to-do lists, Loop 1 start-up commands) is in deploy/loop1/STATE-HISTORY-2026-10-27.md.

## Repo access
- The repo on GitHub is public. On the VM, work from the read-only clone ~/lifeos-ro and run git pull before each session.
- The CEO's Mac is the only machine that writes and pushes, through numbered fix scripts. Do not push from the VM.
- Because the repo is public, the rules under "Never" matter even more.

## How findings come back
- Write each finding in ~/handover/REPORT-<n>.md: what you saw (log or journal lines), what you changed and where (repo file, VM file or config), and what needs a decision. Put files meant for the repo in ~/handover/ and list them.
- Any change on the VM that is not in the repo (agent AGENTS.md, config, workspace, cron) must be listed in the report, so a fix script can mirror it.
- Changes to agent behaviour need the CEO's yes, recorded as a new APR entry in his words, before they are applied.

## How to work with the CEO
- Docs first, then the console. When they disagree, the console wins.
- Dry-run every change first. A shell without ~/loop1/env.sh writes to ~/.openclaw instead of ~/loop1/state.
- Ask before anything destructive and before any step the CEO must do by hand.
- Short answers. Approval requests use the seven items, one per line: What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply (approve, explain more, or keep).
- Report only what is confirmed. Say "not confirmed" otherwise.

## Never
- Print, paste or commit a key or token (~/loop1/openai.env, ~/loop1/slack.env, ~/loop1/gateway-token, the gcalcli login).
- Put Slack IDs, the VM address, account names or a calendar ID in the repo.
- Run git add -A in an agent workspace while state/ is dirty (each workspace HEAD holds the seed state; fix-51).
- Edit or remove a journal line (append-only, APR-0054, APR-0057, ADR-0011).
- Reuse a scenario run ID: agent memory survives a state reset (run 014).
- Send any agent message, compact a session or restart the gateway between 03:30 and 05:10 AST (the 05:00 report must see the first natural message; P-36).

## Current setup (verified 2026-10-27 01:49 AST, handover 7)
- OpenClaw 2026.10.5, model openai/gpt-6-luna (cloud), memory search and dreaming off (APR-0061), daily session reset at 04:00 AST, applied lazily at the first message after 04:00 (APR-0059).
- Gateway: systemd user service openclaw-loop1-gateway (APR-0091); restarts after a crash and at boot; log ~/loop1/gateway.log. Control: systemctl --user status|stop|start|restart openclaw-loop1-gateway. Stop it before any AGENTS.md change (a stop can take up to 330 s). Never start a second gateway by hand. Terminal T1 is no longer used.
- Agents COO, CHO, CoS, CFO in ~/loop1/workspaces/<id> (each a git repo). Instruction sets now: COO v1.10.6 (APR-0106, applied 2026-10-29), CoS v1.10.2, CHO v1.9, CFO v1.10. Each set is the Loop 1 baseline (deploy/loop1/loop1-agent-files.sh) plus the appended rules of deploy/loop1/loop1-v13-upgrade.sh to loop1-v1103-upgrade.sh, in order. The CFO may message the COO and the CoS.
- Slack: one app per agent (APR-0062), socket mode, four accounts. The CEO normally talks to the COO (APR-0063).
- Calendar: the CoS journal (state/calendar-journal.md, append-only) is pushed by scripts/gcal/gcal_sync.py through scripts/gcal/gcal_sync_cron.sh every 5 minutes (plain cron under ubuntu) to the Google TEST calendar. GCAL_ALLOW_DELETES=1 is set in ~/loop1/gcal-sync/env (APR-0093): the job deletes only a LifeOS-titled event with a delete-pending-approval line and a deleted line for the same event ID. The cron is not moved to the real calendar (APR-0096).
- 05:00 AST report: ~/loop1/daily-reset-report.sh (copies in deploy/loop2/vm/) posts a read-only session report to the COO channel and appends it to ~/loop1/reset-check/report.log.
- Health check: python3 ~/loop1/health-check.py (copy in deploy/loop1/health-check.py). Last run 2026-10-27 23:03 (handover 9): 70 PASS, 0 WARN, 0 FAIL, 4 INFO, all 16 parity lines PASS (ops/health-check-output-2026-10-27-d.txt); the earlier run of 21:51 had 16 WARN (ops/health-check-output-2026-10-27-c.txt); the 16 WARN are the parity checks (live agent file = repo agent-files/ copy). With the repo copies in place they become PASS (the three AGENTS.md copies hold channel-ID placeholders that the check fills in from ~/loop1/slack-channels.env, APR-0098); the updated check must be installed on the VM (handover 9).
- Cost: a daily alert at 1 USD and a kill at 5 USD, set by the CEO on the OpenAI side (APR-0083 rests on his statement; there is no kill switch in our code yet: scripts/ops/kill-switch.sh is empty, Loop 3 step 4); the 5 USD monthly project limit stays. Scenario runs measured by hand cost 0.0037 to 0.0077 USD each (runs 038 to 045).

## Structure test (Loop 3 step 2, APR-0097)
A second agent, solo, exists in the OpenClaw config (added 2026-10-27 with a backup, ~/loop1/state/openclaw.json.pre-solo-20261027-2257): own workspace ~/loop1/workspaces/solo, CLI only, no Slack binding, empty send list, the same model and tool policy as the CoS. Its instructions are composed from the four agents' files by deploy/loop3/structure-test/compose-solo.py. It is a test agent: the four live agents are unchanged and the cron reads only the CoS journal. solo-run.sh runs it with its own journal and push-job state (~/loop1/gcal-sync-solo) on the test calendar. Design: deploy/loop3/structure-test/design.md.
Counted comparison done 2026-10-28 (handover 10, APR-0099): ops/structure-test/comparison/comparison.md. Shared criteria four-agent 36/42, solo 31/42; cost per run 0.0061 vs 0.0019 USD. No structure change was decided; the four-agent set remains the live design. Solo uses the persistent session agent:solo:main compacted in prep.

## Regression suite (Loop 3, APR-0097)
~/loop1/regression-suite.sh <SUITE> [--only N] [--dry-run] (copy in deploy/loop3/vm/, with reg-criteria.py) runs the seven scenarios (bad-sleep, D1, D2, D3, CFO entry, overlap, privacy request) with measured cost and writes ~/handover/regression/<SUITE>.md. It refuses to start if it would run into 02:30 to 05:10 AST, resumes the cron on exit and ends with a reset to the seed. Baseline loop3-reg-001 (2026-10-27 21:30 to 21:49): 5 of 7 pass, 0.0455 USD (ops/regression/loop3-reg-001.md).

## Running a scenario (CLI route, synthetic data)
1. Prep: ~/loop1/scenario-run.sh prep <RUN> (pauses the cron, saves and resets state, compacts sessions and reads every output, pushes the seed lines, lists Google). Any STOP means wait and retry; the cron stays paused.
2. Send: openclaw agent --agent coo --session-id <RUN>-coo --timeout 300 -m "<scenario text with the run ID>".
3. Check: ~/loop1/scenario-run.sh check <RUN> [--skip-checker] [--cfo] (numstat, journal lines, trajectory checker; runs the job and resumes the cron only when the checker passes).
4. Scenario files: tests/scenario/ (bad-sleep-reschedule.md with the full run log, delete-approval.md, privacy-request.md, cfo-entry.md, overlap-conflict.md). Helpers: deploy/loop2/vm/h4-d1.sh, h6-d2.sh, h4-post.sh (progress lines to the COO channel).

## Open items
- P-36 watch: a reset on the CHO, CoS and CFO channel sessions is still to be seen in a 05:00 report after a first normal message (not /new). The new COO and CFO main IDs of 2026-10-26 20:44 to 20:47 have an unknown cause.
- Deferred: the monthly journal archive job (build near 1,000 lines), P-41 memory, P-26 Slack files:read, P-09 spikes, P-17 dashboard.

## Known issues
- Agent memory survives a git state reset and a one-line compaction: always use a new run ID.
- The CoS sometimes reports an acknowledgement error after delivering (SESSION_WORK_START_CHANGED, P-35 closed, APR-0068). No message is lost.
- The COO sometimes names only the CHO as confirming (runs 015, 018, 045); no rule change decided.
- Baseline loop3-reg-001 (2026-10-27): bad-sleep failed once by the checker (the sessions_send acknowledgement error P-35; the journal held the move once, moved and written, numstat 5 0; the runner did not run the job because the checker failed) and the overlap scenario failed once (the COO did not offer the free 08:00 to 09:00 slot, which it did in run 023). Both involve a hand-off between agents. One run each; no rule change decided. Evidence for the Loop 3 structure test.
