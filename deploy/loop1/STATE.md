# Loop 1 state and handoff (as of 2026-10-25, 02:00 AST)

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
- OpenClaw 2026.10.5, model openai/gpt-6-luna, runtime pinned to openclaw (APR-0060), memory search and dreaming off (APR-0061), cron off, daily session reset at 04:00 (APR-0059).
- Agents COO, CHO, CoS, CFO in ~/loop1/workspaces/<id>. Instruction sets v1.5 (APR-0066, COO) and v1.6 (APR-0067, CoS) are applied on the VM.
- Slack: one app per agent (APR-0062), socket mode, four accounts (default = COO, cho, cos, cfo). Each account has its own channel in its allowlist, with a users list holding only the CEO's Slack ID. That list also lets "@<agent> /new" work (section 7.10). P-29 is closed.
- The CEO may address any agent in its channel; normally he talks to the COO (APR-0063).
- Health check: python3 ~/loop1/health-check.py [--live]. Last run 39 PASS, 0 FAIL, 1 WARN (old /new refusals in the log window). Some of its text is stale (P-31); see "Still to do".

## Start-up on the VM
Terminal 1 (gateway, owned by the CEO unless he says otherwise):

    source ~/loop1/env.sh; set -a; source ~/loop1/slack.env; source ~/loop1/openai.env; set +a; openclaw gateway run

Every other shell starts with: source ~/loop1/env.sh. Check one gateway process before tests:

    pgrep -af "openclaw.*gateway" | grep -v pgrep | wc -l      (expect 1)

## Scenario run from Slack (the current test)
1. Save and reset the state, then compact the main sessions. Use a new run ID for every attempt:

       source ~/loop1/env.sh
       W=~/loop1/workspaces; E=~/loop1/evidence/$(date +%F); mkdir -p $E
       for a in cho cos cfo; do cp -r $W/$a/state $E/<run ID>-$a; git -C $W/$a checkout -- state/; done
       T=$(cat ~/loop1/gateway-token)
       for a in cho cos cfo; do openclaw sessions compact "agent:$a:main" --agent $a --max-lines 1 --token "$T"; done
       tail -n 3 $W/cos/state/calendar-journal.md      (seed lines only)

2. The CEO posts "@COO /new" in the COO channel, then the scenario text from the scenario file with the new run ID.
3. After about 2 minutes:

       git -C $W/cos diff --numstat state/calendar-journal.md      (expect 2 0)
       tail -n 2 $W/cho/state/health-plan.md
       grep -c "SESSION_WORK_START_CHANGED" /tmp/openclaw/openclaw-$(date +%F).log

4. Pass: one COO reply that says the move is done, names the CHO and the CoS and gives the event IDs; one line each in the CHO and CoS channels; no "Late reply", no FAILURE note; numstat 2 0.
5. Cost is not measured for now (CEO decision, 2026-10-24).

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

## Known issues
- Agent memory survives a git state reset and a one-line session compaction. A reused run ID can get an answer from memory instead of the reset state. Use a new run ID for every attempt.
- First-contact miss: fixed by v1.5 (APR-0066); not seen in runs 015 to 019. In run 018 the CoS ran twice (first run took no action); cause not found.
- SESSION_WORK_START_CHANGED: a retryable timing race in OpenClaw's session ingress; no message lost (APR-0068, P-35 closed). The CoS reports it as "delivered; acknowledgement error" (v1.6). Reopen if a session-start-conflict-retry-limit line appears.
- COO SQLite maintenance warning about 2 seconds after each scenario post (runs 018, 019); no visible effect (P-37, Loop 2).
- The COO's answer sometimes names only the CHO (runs 015 and 018), though the CoS wrote the journal line. Run 019 named both. No rule change yet.
- Usage page lag: readings taken within about 20 minutes of a run may miss the charge. Cost is deferred for now.

## Still to do before Loop 1 closes
1. P-35 is closed (APR-0068). P-37 (COO SQLite warning) is for Loop 2.
2. Scenario closure: the CEO approved closing it (to the VM agent, 2026-10-25), pending Claude's log review. Run 019 is a clean pass under v1.6. Record the closure as an APR entry.
3. Daily reset check: P-36, pending. The CEO asked not to raise it for now.
4. SPK-03: CEO decision to close as partial with JavaScript Code Mode and the Docker sandbox deferred, or to test Code Mode first (research/spikes/SPK-03-workspace-isolation.md).
5. Health check update: add Slack checks (four accounts connected, each channel's users list), drop the stale P-29 and P-31 wording, and ignore /new refusals logged before 2026-10-24 19:19.
6. CEO housekeeping on the Mac: delete ~/Downloads/spk04-transfer (it holds old secrets) and old copies of health-check.py and the upgrade scripts.
7. Write the Loop 1 close record: what passed, what was deferred and why (cost, from 2026-10-24), the cost per run where known, and the open items for Loop 2 (P-26, P-28, P-31, P-32).
