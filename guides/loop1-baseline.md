# Loop 1 baseline on the Oracle VM, and OpenClaw CLI reference

Status: partial
Last verified: 2026-10-22 on the Oracle VM (Ubuntu, user ubuntu), OpenClaw 2026.10.5 (1b58cb9)
Tool version: OpenClaw 2026.10.5 (1b58cb9)
Owner: CEO

## What this is for
The clean starting point for Loop 1 (ADR-0018): an empty state folder with the model and tool profile set, and nothing else. Steps 1 to 5 were run on 2026-10-22. Step 6 lists agent commands whose help text was read but not yet run.

## Before you start (HUMAN)
- The old spk04 gateway must stay off. Step 1 checks this.
- Never use the default ~/.openclaw folder. Every command below loads ~/loop1/env.sh first.
- Secrets: the OpenAI key lives in ~/loop1/openai.env, edited with nano. Never cat it, paste it, or put it in a repo file. Use cut -d= -f1 to see variable names only.
- The key must belong to the life-os project, so the budget alert and monthly cap apply to it.

## 1. Check the starting state
    openclaw --version
    systemctl --user is-active openclaw-gateway
    systemctl --user is-enabled openclaw-gateway
    pgrep -af openclaw | grep -v pgrep

Expect: 2026.10.5; inactive; disabled; no pgrep output. (Verified 2026-10-22.)

## 2. Create the state folder and env file
    mkdir -p ~/loop1/state
    printf 'export OPENCLAW_STATE_DIR=~/loop1/state\nexport OPENCLAW_CONFIG_PATH=~/loop1/state/openclaw.json\n' > ~/loop1/env.sh
    source ~/loop1/env.sh
    openclaw config file

Expect: ~/loop1/state/openclaw.json. Run source ~/loop1/env.sh in every terminal you use for loop1. A terminal without it reads the default folder.

## 3. Add the key file, checking names only
    nano ~/loop1/openai.env          # one line: OPENAI_API_KEY=<new key>
    chmod 600 ~/loop1/openai.env
    cut -d= -f1 ~/loop1/openai.env

Expect: OPENAI_API_KEY. Do not copy a key from an older folder. The key in ~/spk04/openai.env was revoked on 2026-10-19 and must not be reused.

## 4. Write the baseline patch, dry-run it, apply it
Save this as ~/loop1/baseline.json (no secrets in it):

    {
      "agents": {
        "defaults": {
          "model": { "primary": "openai/gpt-6-luna" },
          "utilityModel": "openai/gpt-6-luna"
        }
      },
      "tools": { "profile": "messaging" }
    }

Then:

    source ~/loop1/env.sh
    openclaw config patch --file ~/loop1/baseline.json --dry-run
    openclaw config patch --file ~/loop1/baseline.json
    openclaw config get agents.defaults.model
    openclaw config get agents.defaults.utilityModel
    openclaw config get tools

Expect: dry run "3 update(s) validated"; apply "Applied 3 config update(s)"; model {"primary": "openai/gpt-6-luna"}; utility model openai/gpt-6-luna; tools {"profile": "messaging"}. (Verified 2026-10-22.)

The patch creates the file when it is missing. Before the patch, openclaw config validate reported "Config file not found".

## 5. Validate, and check for secrets
    openclaw config validate
    grep -c "sk-" ~/loop1/state/openclaw.json

Expect: "Config valid" and 0. OpenClaw adds two plugin entries on its own (anthropic and codex, with session cataloging off). That is expected. (Verified 2026-10-22.)

## 6. Agent commands (help read on 2026-10-22; not run yet)
    openclaw agents --help

Subcommands: list, add, bind, bindings, delete, set-identity, team, unbind.

- add [name]: options --workspace <dir>, --agent-dir <dir>, --model <id>, --bind <channel[:accountId]> (repeatable), --role coordinator|researcher|writer|reviewer, --non-interactive (needs --workspace unless --role is set), --json.
- set-identity: options --agent <id>, --name, --emoji, --avatar (workspace path, http(s) URL, or data URI), --theme, --from-identity, --identity-file, --workspace, --json. This is the candidate for per-agent display names in Spike 10 (APR-0053). Not tested in Slack.
- team create: "Create a coordinator and specialists from a bundled preset". Its options were not read yet.

Not verified: the bind syntax, the team create options, and whether set-identity names reach Slack.

## 7. Agents, tool policy and agent-to-agent (tested 2026-10-22)

Tested on OpenClaw 2026.10.5 with the gateway running. Order for every change: read the tool-policy docs, read the schema, dry-run the patch, then run a live test.

### 7.1 Add an agent and remove its first-run file
    source ~/loop1/env.sh
    openclaw agents add <id> --non-interactive --workspace ~/loop1/workspaces/<id> --model openai/gpt-6-luna --json
    rm -f ~/loop1/workspaces/<id>/BOOTSTRAP.md

Expect agentId and workspace in the output. BOOTSTRAP.md is a first-run identity interview; delete it so the agent does not start one. Add agents with the gateway stopped, because the add writes config.

### 7.2 Change config only with a patch file
Write the change as JSON, then:

    openclaw config patch --file <file> --dry-run
    openclaw config patch --file <file>
    openclaw config validate

Check the result with openclaw config get. Do not hand-edit openclaw.json.

### 7.3 Keys that worked on 2026-10-22
- tools.agentToAgent: enabled true, and allow lists the agent ids that may take part.
- agents.entries.<id>.tools.agentToAgent.send: the ids this agent may message. A missing entry is refused with: "Agent-to-agent messaging denied by the requester agent tools.agentToAgent.send allowlist."
- tools.sessions.visibility: agent. Sessions can only be targeted within the same agent, so one agent cannot read another agent's session. Explicit send destinations still work.
- agents.defaults.subagents: maxSpawnDepth 1, maxChildrenPerAgent 2, runTimeoutSeconds 120.
- agents.entries.<id>.tools.alsoAllow: ["read", "write", "edit"] for agents that keep state files, with agents.entries.<id>.tools.fs.workspaceOnly set to true.

### 7.4 Rules learned the hard way
- Docs first. The tool-policy page (docs.openclaw.ai/gateway/config-tools/tool-policy) lists the profile contents and tool groups. group:fs means read, write, edit and apply_patch. Then the schema, then the console. The docs lag the console, so the console wins when they disagree.
- allow and alsoAllow cannot both be set in the same scope. allow replaces the profile baseline. alsoAllow adds to it. On the messaging profile, use alsoAllow.
- The warning "tools policy: profile messaging ... Add alsoAllow" means file tools are missing. The agent then answers that it has no file tool.
- The gateway log line "code-mode: cataloged N tools" is a quick check. 4 meant the allow list had cut the agent down. 23 was the working count after the fix.
- Scratch files for file tools go under .openclaw/tmp/ inside the agent workspace. A path outside it fails with "Path escapes sandbox root".
- A gateway restart loads config changes. Stop it with Ctrl-C before a patch and start it again after.
- Before any test, check one gateway process: pgrep -af "openclaw.*gateway" | grep -v pgrep | wc -l should print 1.
- After a terminal disconnect, check for a gateway process with pgrep before using pkill.
- Use a fresh --session-id for each test. An old session can keep earlier tool results.
- Reset state to the seed before every scenario run: git -C ~/loop1/workspaces/<id> checkout -- state/. Copy the state to ~/loop1/evidence/<date>/ first.
- Set a git identity in each workspace once: git -C <workspace> config user.name loop1, and the same for user.email. Without it a commit fails with "Author identity unknown".
- An instruction change is appended to AGENTS.md and committed in the workspace, then the same change goes into deploy/loop1/loop1-agent-files.sh in the repo, so the repo and the VM match.
- Ctrl-C drains work in flight before the gateway stops (budget 315 s; about 60 s on 2026-10-22). While it drains, cross-agent sends are refused. Nothing resumes after a restart; resend the same run ID. A resend is safe: the event ID stops a second write.
- Main sessions (agent:<id>:main) cannot be deleted or archived. Cut one to its last line with: openclaw sessions compact "agent:<id>:main" --agent <id> --max-lines 1 --token "$(cat ~/loop1/gateway-token)". This is permanent and keeps no backup, so use it on synthetic data only.
- session.reset is daily at 04:00 gateway local time (APR-0059). Check the VM time zone with timedatectl before setting atHour.
- Commands that go through the gateway (sessions delete, compact, automations) need --token. Read it from ~/loop1/gateway-token; never print it.
- The OpenAI project spend limit shows "Limit not enforced": it alerts but does not stop calls (P-31).

### 7.5 Results (2026-10-22)
| Test | Expected | Result |
|---|---|---|
| COO identity | names itself and lists its send targets | Pass |
| CHO isolation | sees only its own session | Pass |
| CFO sends to CHO (not on its list) | refused by the allowlist | Pass |
| CHO sends calendar request to CoS | CoS writes a journal line and replies | Pass (loop1-test-002) |
| CoS reads its journal | returns the last line | Pass after alsoAllow |
| CoS reads a file outside its workspace | refused | Pass |
| CHO diet change, COO forwards to CFO | CFO adjusts the grocery budget | Pass (loop1-diet-001, 150 to 125 USD) |
| Bad-sleep reschedule, run 1 (v1) | CHO sends the move to the CoS | Fail: no rule for creating an event ID |
| Bad-sleep reschedule, run 2 (v1.1) | append-only journal, summary names every agent | Partial |
| Bad-sleep reschedule, run 3 (v1.2) | all five criteria | Pass (tests/scenario/bad-sleep-reschedule.md) |
| Bad-sleep reschedule, runs 4 and 5 (v1.2) | same result as run 3 | Pass (three in a row) |
| Restart mid-flow (run 6) | clean stop, safe retry | Pass: no change after the restart; the retry wrote one pair |
| Resend of a finished run | no duplicate | Pass: earlier result reported; journal unchanged |
| Compact main sessions | one line kept | Pass: all four compacted |
| Health check, offline and live | no FAIL | Pass (2026-10-23) |

### 7.6 Not established
- Automatic resume after a restart. Not available: work in flight is drained or refused, and a retry must be sent again.
- The exact moment of the 04:00 reset. On 2026-10-23 the CoS main session got a new session ID at the first message after 04:00; the reset is applied when the next message arrives, so a switch at 04:00 itself was not observed.
- Which OpenClaw file adds the exit listeners behind the startup warning (stack trace not captured).
- The messaging profile's full tool list. Session tools work in practice; the docs list is partial.
- The main agent is excluded from agent-to-agent calls on purpose for Loop 1. Not tested either way.
- Whether JavaScript Code Mode can reach files outside an agent's workspace or the network (SPK-03).

### 7.7 Runtime, memory and health check (2026-10-23)
- Runtime pinned for openai/gpt-6-luna (APR-0060): agents.defaults.models["openai/gpt-6-luna"].agentRuntime.id = "openclaw". The patch needs a gateway restart. Check with openclaw sessions --agent cos --json: agentRuntime.id should read openclaw.
- Memory search and dreaming off (APR-0061): memory.search.enabled false and plugins.entries.memory-core.config.dreaming.enabled false. With the defaults, memory sync sent embeddings to OpenAI and dreaming runs a nightly sweep at 03:00. Heartbeats are a separate thing and were already off (cron.enabled false).
- Health check: deploy/loop1/health-check.py, copied to ~/loop1/ on the VM:

      python3 ~/loop1/health-check.py          (offline: no model calls)
      python3 ~/loop1/health-check.py --live   (adds one CoS turn and one refused CFO-to-CHO send)

  It prints PASS, WARN, FAIL or INFO per check, names the incident each check would have caught, and exits 1 on any FAIL. It never reads the key or the gateway token. Run it before tests, and after a scenario run but before the state reset, because the reset removes what the append-only check reads.
- First VM run, 2026-10-23: offline 38 PASS and 0 FAIL; live 40 PASS and 0 FAIL. The one WARN was the startup listener warning below, now reported as INFO.
- MaxListenersExceededWarning ("11 exit listeners added to [process]") appears once per gateway start, right after the per-agent session-store maintenance (5 stores). It never came from a CLI run and never repeated inside one gateway process. The health check reports INFO while warnings do not outnumber gateway starts, and WARN if they do.

### 7.8 Slack: one app per agent (2026-10-24, APR-0062)
- Why: with one Slack app, only replies to a routed message carried the agent's name and icon. A post an agent made with its message tool after a handoff showed the app name. The Slack plugin sets the identity for replies only.
- Shape: four apps (COO, CHO, CoS, CFO). Tokens in ~/loop1/slack.env, mode 600, names SLACK_BOT_TOKEN_<AGENT> and SLACK_APP_TOKEN_<AGENT>. Never print or paste them.
- Each app needs: bot scopes app_mentions:read, chat:write, chat:write.customize, channels:history, channels:read, groups:history, groups:read (the last two for private channels); the app_mention bot event; socket mode with an app-level token (connections:write); an invite into its channel. After a scope or event change, reinstall the app.
- Config (patch file, then dry run): channels.slack.accounts with four accounts: default (COO), cho, cos, cfo. Each has enabled, mode socket, botToken and appToken as env references {source env, provider default, id <NAME>}. Keep the name default for the first account; a config without it gave an unresolved-account error in SPK-04.
- Each account needs its own channel in its allowlist: channels.slack.accounts.<id>.channels.<channel ID>.enabled true. Without it the bot answers: "This OpenClaw bot can't reply here because this channel isn't in its OpenClaw channel allowlist."
- Bindings: one per channel (peer kind channel, id) to the agent, and one route per account (match channel slack, accountId) to the agent. openclaw agents bind --agent <id> --bind slack:<account> adds the route.
- Identity: openclaw agents set-identity --agent <id> --name <name> --emoji ":name:". Slack needs the :name: form; a raw emoji did not show.
- Start the gateway with slack.env and openai.env sourced. Check: openclaw channels status --probe shows four Slack lines ending in works.
- What the CEO sees: replies show the agent's name and emoji. A post an agent makes with its message tool shows the app's name and the app's own Slack image, not the emoji. Set each app's image in Slack to match.
- Results are in research/spikes/SPK-10-slack-one-app-display-names.md.

### 7.9 Slack-driven runs: waiting, late replies, own-channel posts (2026-10-24)
- A scenario run from the COO channel (loop1-scn-007) wrote the right journal lines and passed criteria 1 to 4. In Slack it was not clean: the COO answered "blocked" when its wait ended, the CHO's report arrived late, and the late report woke the COO twice. Each wake-up posted a summary with the message tool and then ended with no final text ("reasoning-only" retries, then "Agent couldn't generate a response").
- Docs (concepts/session-tool): with sessions_send, a positive timeoutSeconds waits for the reply and returns it inline. The wait limits the sender only, and a late reply is not discarded: it reaches the requester later as an inter-session input. timeoutSeconds 0 returns without waiting.
- Replies carry the agent's name and emoji. Message-tool posts show the app's name and the app's own Slack image. Set each Slack app's image to match its emoji.
- The log line "[slack] delivered reply" appears only for replies, not for message-tool posts.
- Cost: loop1-scn-007 cost about 0.047 USD (80 requests, about 1.5 million tokens, mostly cached), the sum of the item changes on the OpenAI usage page. The cache read dropped from about 29,000 tokens to 0 when the message tool was added and an earlier message's envelope changed; cache writes were the largest item. The COO's prompt on that turn was about 35,000 tokens.
- The fix is instruction set v1.3 (APR-0064): wait 240 s and treat the reply as the result, one final answer, a one-line own-channel post by the CHO, CoS and CFO, failures through the COO. Apply with deploy/loop1/loop1-v13-upgrade.sh (gateway stopped). It reads the channel IDs from ~/loop1/slack-channels.env.
- First v1.3 upgrade, 2026-10-24: the script committed with git add -A while state/ held the run-007 journal and plan lines, so HEAD held that state and the reset (git checkout -- state/) restored it instead of the seed. Run loop1-scn-008 then found the move already done and changed nothing. The script now commits AGENTS.md only. Repair on the VM: in each workspace with state (cho, cos, cfo) git reset --soft HEAD~1, git reset -- state/, git checkout -- state/, then commit again.
- Rule: in a workspace, never run git add -A while state/ is dirty. HEAD must hold the seed state, because the scenario reset restores HEAD.

### 7.10 Slack control commands: /new needs a channel users list (2026-10-24)
- "@COO /new" in a channel was refused for most of a day: one inbound log line, no reply, and a control-command-unauthorized entry in the gateway log file. It works once the channel has an explicit users list: channels.slack.accounts.<id>.channels.<CHANNEL ID>.users set to the CEO's Slack user ID. The patch hot-reloaded, and Slack answered "New session started."
- From the Slack plugin code: for a message in a channel, the command decision uses the channel's users list and the account's allowFrom. With neither, the channel is open, and open does not authorize control commands. commands.allowFrom is read only for button actions. It was tried in four ID forms and removed.
- Side effect: only the listed user can trigger an agent in that channel. All four Loop 1 channels have the list.
- Use "@<agent> /new" to start each Slack run with a fresh session for that channel.
- A terminal without ~/loop1/env.sh reads the default folder: one patch landed in ~/.openclaw/openclaw.json and sessions delete said Unknown agent id. The stray key was removed with openclaw config unset.

### 7.11 Instruction set v1.4: wait for the result, answer once (APR-0065)
- Run loop1-scn-010 (Slack): the CHO reported "pending" while the CoS had already written the move, and the CoS's confirmation to the CHO failed twice with SESSION_WORK_START_CHANGED (likely because the CHO's run was still active; not confirmed). The COO then told the CEO "pending".
- v1.4: the CHO waits (timeoutSeconds 120) for the CoS reply; the CHO, CoS and CFO answer a request with their reply and send no separate message back. Apply with deploy/loop1/loop1-v14-upgrade.sh (gateway stopped; AGENTS.md only; skips agents already on v1.4).
- Cost of run 010: at most 0.020 USD. The usage page lags, and the figure includes the health check turns after the run.

## Troubleshooting
- "Config file not found" from config validate: no patch has been applied. Apply the baseline (step 4).
- Revoked key: a copy of an old key stays revoked. Create a new key in the life-os project.
- A command run from a terminal without the env file reads the default folder. Source ~/loop1/env.sh first.

## What is not established
- Whether team create gives the four Loop 1 agents the right names and roles.
- Whether the CHO, CoS and CFO should answer the CEO directly in their channels (P-33).
- Automatic resume after a restart (not available; see section 7.4).

## Never paste here
Key values, tokens, Slack IDs, VM addresses, or the contents of any env file.

## History
- 2026-10-22: written from the baseline run on the Oracle VM (fix-44).
- 2026-10-22: section 7 rules and results extended with the bad-sleep scenario (fix-46).
- 2026-10-22: restart, duplicate and session results added; daily session reset (fix-47).
- 2026-10-23: runtime pinned, memory off, health check added (fix-48).
- 2026-10-24: Slack one app per agent (APR-0062), section 7.8 added (fix-49).
- 2026-10-24: section 7.9 and instruction set v1.3 approved (fix-50).
- 2026-10-24: v1.3 upgrade commit bug and run 008 recorded (fix-51).
- 2026-10-24: /new solved (7.10), instruction set v1.4 approved (7.11) (fix-52).
