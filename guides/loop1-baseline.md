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

### 7.6 Not established
- Automatic resume after a restart. Not available: work in flight is drained or refused, and a retry must be sent again.
- Whether the 04:00 daily reset fires on schedule (check the main session token counts the next day).
- Why sessions show the runtime "OpenAI Codex" (P-30).
- The messaging profile's full tool list. Session tools work in practice; the docs list is partial.
- The main agent is excluded from agent-to-agent calls on purpose for Loop 1. Not tested either way.
- Slack display names per agent (Spike 10).

## Troubleshooting
- "Config file not found" from config validate: no patch has been applied. Apply the baseline (step 4).
- Revoked key: a copy of an old key stays revoked. Create a new key in the life-os project.
- A command run from a terminal without the env file reads the default folder. Source ~/loop1/env.sh first.

## What is not established
- Whether team create gives the four Loop 1 agents the right names and roles.
- Whether set-identity names appear in Slack (Spike 10).
- Automatic resume after a restart (not available; see section 7.4).

## Never paste here
Key values, tokens, Slack IDs, VM addresses, or the contents of any env file.

## History
- 2026-10-22: written from the baseline run on the Oracle VM (fix-44).
- 2026-10-22: section 7 rules and results extended with the bad-sleep scenario (fix-46).
- 2026-10-22: restart, duplicate and session results added; daily session reset (fix-47).
