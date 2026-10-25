# Loop 1 state and handoff (as of 2026-10-24, 20:30 AST)

Written for a Claude Code session running on the Loop 1 VM, picking up from the planning chat. Read this first, then the files it points to. Nothing here is a decision; decisions live in decisions/APPROVALS.md, open questions in decisions/PENDING.md.

## Read in this order
1. guides/loop1-baseline.md, section 7 (7.1 to 7.11): how the VM, agents, config and Slack are set up, with every lesson learned.
2. tests/scenario/bad-sleep-reschedule.md: the scenario, its pass criteria and the run log (runs 001 to 013).
3. decisions/APPROVALS.md from APR-0052 on, and decisions/PENDING.md.
4. decisions/adr/ADR-0018: Loop 1 is a cloud-only exception on synthetic data. It expires at Loop 1 close or on 2026-11-15 (APR-0052).

## How to work with the CEO
- Docs first, then the console. When the docs and the console disagree, the console wins; when the plugin code is the deciding factor, read the code (section 7.10 is the example).
- Dry-run every config patch before applying it, and check the dry run names ~/loop1/state/openclaw.json. A shell without ~/loop1/env.sh writes to ~/.openclaw instead.
- Any change to agent instructions or to approved behaviour needs the CEO's yes, recorded as a new APR entry in his own words. Present it as a short numbered proposal and wait.
- Ask before stopping the gateway, before anything destructive, and before any step the CEO has to do by hand (Slack posts, the OpenAI usage page).
- Keep answers short when the CEO asks for that. Give commands in batches of a few steps.
- Repo changes have so far been made as numbered fix scripts (fix-44 to fix-53) run by the CEO on his Mac, which holds the repo and pushes it. Ask the CEO before changing that flow (for example, cloning the repo on the VM with push access).

## Repo access
- The repo on GitHub is public. On the VM, read it from a read-only clone and run git pull before each session, so the guides, approvals and this file are current.
- The CEO's Mac is the only machine that writes and pushes, through numbered fix scripts. Do not push from the VM unless the CEO sets that up.
- Because the repo is public, everything under "Never" matters even more.

## Never
- Print, paste or commit a key or token. The values live in ~/loop1/openai.env, ~/loop1/slack.env and ~/loop1/gateway-token (mode 600).
- Put Slack IDs, the VM address or account names in the repo. Slack channel IDs live in ~/loop1/slack-channels.env on the VM.
- Run git add -A in an agent workspace while state/ is dirty. Each workspace HEAD must hold the seed state, because the scenario reset restores HEAD (fix-51).
- Edit or remove a journal line. The calendar journal is append-only (APR-0054, APR-0057).

## Current setup (verified 2026-10-24)
- OpenClaw 2026.10.5, model openai/gpt-6-luna, runtime pinned to openclaw (APR-0060), memory search and dreaming off (APR-0061), cron off, daily session reset at 04:00 (APR-0059).
- Agents COO, CHO, CoS, CFO in ~/loop1/workspaces/<id>. Instruction set v1.4 is applied on the VM (APR-0065). v1.5 is approved (APR-0066); check the COO AGENTS.md for an "instruction set v1.5" line to see whether it has been applied.
- Slack: one app per agent (APR-0062), socket mode, four accounts (default = COO, cho, cos, cfo). Each account has its own channel in its allowlist with a users list holding only the CEO's Slack ID. That list is also what lets "@<agent> /new" work (section 7.10). P-29 is closed.
- The CEO may address any agent in its channel; normally he talks to the COO (APR-0063).
- Health check: python3 ~/loop1/health-check.py [--live]. Last run 39 PASS, 0 FAIL. Its one WARN counts old /new refusals still in the log window, and some of its text is stale (P-29, P-31); see "Still to do".

## Start-up on the VM
Terminal 1 (gateway, owned by the CEO unless he says otherwise):

    source ~/loop1/env.sh; set -a; source ~/loop1/slack.env; source ~/loop1/openai.env; set +a; openclaw gateway run

Every other shell starts with: source ~/loop1/env.sh. Check one gateway process before tests:

    pgrep -af "openclaw.*gateway" | grep -v pgrep | wc -l      (expect 1)

## Scenario run from Slack (the current test)
1. Save and reset the state, then compact the main sessions:

       source ~/loop1/env.sh
       W=~/loop1/workspaces; E=~/loop1/evidence/$(date +%F); mkdir -p $E
       for a in cho cos cfo; do cp -r $W/$a/state $E/<run ID>-$a; git -C $W/$a checkout -- state/; done
       T=$(cat ~/loop1/gateway-token)
       for a in cho cos cfo; do openclaw sessions compact "agent:$a:main" --agent $a --max-lines 1 --token "$T"; done
       tail -n 3 $W/cos/state/calendar-journal.md      (seed lines only)

2. The CEO notes the OpenAI usage page items, posts "@COO /new" in the COO channel, then the scenario text from the scenario file with the new run ID.
3. After about 2 minutes:

       git -C $W/cos diff --numstat state/calendar-journal.md      (expect 2 0)
       tail -n 2 $W/cho/state/health-plan.md
       grep -c "SESSION_WORK_START_CHANGED" /tmp/openclaw/openclaw-$(date +%F).log

4. Pass: one COO reply that says the move is done, names the CHO and the CoS and gives the event ID; one line each in the CHO and CoS channels; no "Late reply", no FAILURE note; numstat 2 0.
5. Cost: the CEO reads the usage page again at least 20 minutes later, with no model calls in between. The page lags. Ceiling 0.05 USD per run (APR-0056).

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

## Known issues
- First-contact miss: when the COO routes to the CHO, the CHO sometimes finds no task details (runs 011, 013). The COO's resend worked in 013. Fix: v1.5 (APR-0066), one COO rule to carry the whole task inline and resend once.
- SESSION_WORK_START_CHANGED: the CoS's reply to a waiting CHO is delivered, but its acknowledgement errors. Seen in runs 010, 012 and 013. The content arrived each time. Open as P-35.
- Usage page lag: readings taken within about 5 minutes of a run miss it.

## Still to do before Loop 1 closes
1. v1.5 is approved (APR-0066). If the COO AGENTS.md has no v1.5 line yet: stop the gateway (ask), run deploy/loop1/loop1-v15-upgrade.sh on the VM (copy it to ~/loop1/; check the hash in fix-53), restart. Then run the scenario from Slack until one run passes cleanly, and measure its cost.
2. P-35: decide whether the ack error is ignored (benign) or needs an instruction.
3. SPK-03: CEO decision to close as partial with JavaScript Code Mode and the Docker sandbox deferred, or to test Code Mode first (research/spikes/SPK-03-workspace-isolation.md).
4. Daily reset check: after 04:00 on 2026-10-25, confirm the main sessions got a new session ID at their first message (method in section 7.7).
5. Health check update: add Slack checks (four accounts connected, each channel's users list), drop the stale P-29 and P-31 wording, and stop counting /new refusals logged before 2026-10-24 19:19.
6. CEO housekeeping on the Mac: delete ~/Downloads/spk04-transfer (it holds old secrets) and old copies of health-check.py and the upgrade scripts.
7. Write the Loop 1 close record: what passed, what was deferred and why, the cost per run, and the open items handed to Loop 2 (P-26, P-28, P-31, P-32).
