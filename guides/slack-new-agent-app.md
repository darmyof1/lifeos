# Add a new agent with its own Slack app (OpenClaw) - guide

Status: working (the CLO was added this way and answered a real message in its own channel; 5 of 5 Slack accounts connected)
Last verified: 2026-11-10 on Oracle VM, Ubuntu 24.04 arm64 (handover 30, evidence in ops/loop7-h30-2026-11-10/)
Tool version: OpenClaw 2026.10.5
Owner: CEO

## What this is for
Every agent in LifeOS has its own Slack app (APR-0062), its own channel, its own workspace folder and its own config entry. This guide is the whole recipe for adding the next one. Replace the placeholders: AGENT = the short lowercase agent id (for example clo), APPNAME = the name people see in Slack (for example CLO), NAME = the id in capitals (CLO) used in the token names.

The manifest to paste into Slack is in guides/slack-app-manifest-clo.json (one line, no secrets). It is the standard OpenClaw manifest with the name CLO: socket mode on, the same message and file scopes the other apps use. Change only the two "CLO" display names and the description for a new agent.

## Before you start (HUMAN)
- A Slack workspace where you can create apps (the LifeOS workspace).
- The agent's instruction files written and approved: agent-files/department/AGENT/ (IDENTITY.md, SOUL.md, USER.md, AGENTS.md). A change to any agent wording needs the CEO's yes recorded as an APR first.
- A quiet time for the gateway restart: never between 03:30 and 05:10 AST, and never two gateways at once.
- Tokens are secrets. Best practice: put them on the VM yourself (see step 6). In Loop 7 the CEO accepted pasting them into the Claude Code chat on the VM (APR-0127); a token pasted in a chat stays in that chat's history. If that is not acceptable, rotate the tokens (see Troubleshooting).

## 1. Create the app from the manifest (HUMAN, in a browser on the Mac)
1. Open https://api.slack.com/apps and click Create New App, then From a manifest.
2. Pick the LifeOS workspace and click Next.
3. Choose the JSON tab, delete what is in the box, paste the whole content of guides/slack-app-manifest-clo.json (copy it from the file, not from a terminal: a terminal wraps long lines and breaks names such as messages_tab_enabled), and click Next.
4. Click Create. Expected: the new app's settings page, titled APPNAME.
Do not use the AI agent template or a Starter or Blank app: they make a different kind of identity (see guides/slack-multi-identity.md).

## 2. Install the app and copy the bot token (HUMAN)
1. In the app: Install App, then Install to Workspace, then Allow.
2. Open OAuth & Permissions and copy the Bot User OAuth Token. It starts with xoxb-. (The User OAuth Token, xoxp-, is the wrong one.)

## 3. Create the app-level token (HUMAN)
1. In the app: Basic Information, scroll to App-Level Tokens, Generate Token and Scopes.
2. Name it anything, add the scope connections:write, click Generate. Copy the token. It starts with xapp-.

## 4. Create the channel and invite the app (HUMAN)
1. In Slack create a channel for the agent (for example lifestyle-clo).
2. In the channel type /invite @APPNAME and send. Expected: Slack says the app joined.
3. Copy the channel ID: open the channel name at the top, View channel details, the ID is at the bottom (starts with C). It is a Slack ID: it goes only in the VM file in step 6, never in the repo, a handover or this guide.

## 5. Prepare the agent on the VM (Claude Code does this from a handover)
1. The workspace folder ~/loop1/workspaces/AGENT is its own git repo holding the four instruction files (the channel placeholder in AGENTS.md is filled from the VM file in step 6) and the agent's state file (for example state/lifestyle.md), committed.
2. The config entry is added by a small script that adds only new keys, backs the config up first (CONFIG.pre-AGENT), shows a diff of the new keys only and refuses if any other key would change. The model for it is deploy/loop7/clo-config-patch.py (+ tests). The new keys are: agents.entries.AGENT (workspace, agentDir, identity, model, tools with fs.workspaceOnly true, the allowed-send list), the id in tools.agentToAgent.allow, the Slack account channels.slack.accounts.AGENT (mode socket, token references SLACK_BOT_TOKEN_NAME and SLACK_APP_TOKEN_NAME, a channel allowlist with the CEO as the only user) and two bindings.
3. Run it first on a scratch state folder and port (no Slack), then live: stop the gateway (systemctl --user stop openclaw-loop1-gateway), run the script, start the gateway (systemctl --user start openclaw-loop1-gateway), confirm exactly one gateway process.
4. fs.workspaceOnly must be true from day one (APR-0125): it is what keeps the agent out of the other agents' folders, and the health check fails if it changes.

## 6. Put the secrets on the VM (HUMAN decides how; the values are never printed or committed)
1. ~/loop1/slack.env (mode 600): two lines, SLACK_BOT_TOKEN_NAME=... and SLACK_APP_TOKEN_NAME=... .
2. ~/loop1/slack-channels.env: one line, for example lifestyle-clo=<channel ID>.
3. Check the mode: ls -l ~/loop1/slack.env must show -rw-------.
Do this before step 5.3, so the gateway finds them at start.

## 7. Verify
1. Run the Slack probe: it must list one more account connected than before (five of five with the CLO). A new account can take about 40 seconds to show connected.
2. In the agent's channel send a message that mentions the app, for example @APPNAME hello. Expected: an answer from the agent. A new top-level message without the @mention is ignored (all agents work this way). A reply in a thread under the agent's own answer needs no mention once section 8 is done (APR-0143).
3. The health check (python3 ~/loop1/health-check.py) shows the agent's version, parity, confined and send-list lines as PASS, and WARN 0 FAIL 0. The parity lines compare the live files with the repo copy, so the instruction files must be pushed and pulled to ~/lifeos-ro first.
4. Run a scenario per duty with synthetic data and new run IDs; keep the raw replies (ops/ evidence folder).

## 8. Thread replies without a mention (APR-0143; HUMAN for the Slack part, Claude Code for the config)
This replaces the mention rule of APR-0063 only for threads whose first message the bot sent: the CEO can reply in the thread under the agent's answer without typing the @mention. A new top-level message still needs the mention; DMs are unchanged; a thread the CEO starts under his own message keeps the normal rule (a mention is needed).
1. Slack app (HUMAN): Event Subscriptions, Subscribe to bot events: add message.channels (and message.groups for a private channel) in addition to app_mention. OAuth and Permissions must hold the matching history scopes (channels:history, and groups:history for a private channel). Then Install App, Reinstall to Workspace. Without these events Slack never sends an unmentioned thread reply to the gateway; the manifest in guides/slack-app-manifest-clo.json already has them.
2. Config (Claude Code, from a handover): the account entry carries requireMentionInBotThreads false (channels.slack.accounts.<id>.requireMentionInBotThreads). deploy/after-loop7/bot-thread-mention-patch.py sets it for the five accounts and refuses any other change; deploy/loop7/clo-config-patch.py writes it for a new account. It is not read live: stop the gateway and start it again, then run the Slack probe (all accounts connected).
3. Test: the CEO types @APPNAME ping as a new message, then replies in the thread under the answer without a mention: the agent answers in the thread. A new top-level message without a mention gets no answer (the gateway log has a missing-mention rejection).
4. If the thread reply is ignored, check in this order: the Slack app lacks the history scope; the event arrived without a thread timestamp; the thread's first message was not the bot's (then the normal rule applies).

## Rollback (remove the agent)
1. Stop the gateway. Copy the config backup back (cp ~/loop1/state/openclaw.json.pre-AGENT ~/loop1/state/openclaw.json).
2. Delete the two token lines in ~/loop1/slack.env and the channel line in ~/loop1/slack-channels.env. Move ~/loop1/workspaces/AGENT and ~/loop1/state/agents/AGENT aside. Start the gateway.
3. In Slack uninstall the app (Basic Information, Delete App if it will not be used again). Revert the repo change that added the agent (the health check expects the agents it knows).

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| Slack says the manifest is not valid JSON | The paste was taken from a wrapped terminal and a word was split | Copy from guides/slack-app-manifest-clo.json |
| The probe shows the new account not connected | The app was just installed, or a token is wrong | Wait about 40 seconds; then check the xoxb- and xapp- values and the env names |
| The agent does not answer in its channel | No @mention, or the app was not invited | Mention the app; /invite @APPNAME |
| The agent ignores a thread reply without a mention | The app lacks message.channels or the history scope, or the thread was not started by the bot, or requireMentionInBotThreads is not false | Section 8 |
| Probe connected but the agent never replies | The channel ID in the allowlist is wrong or the CEO is not in the users list | Check slack-channels.env and the diff of new keys |
| Health check parity lines WARN or FAIL after the install | The instruction files are live but the repo copy on the VM is old | Push the Mac repo, then git pull on the VM |
| A token was pasted in a chat | It stays in that chat's history | Slack: Install App, Reinstall (new bot token) and Basic Information, regenerate the app-level token; then change the two lines in slack.env and restart the gateway outside 03:30 to 05:10 AST |
| The agent's calendar request stays "queued" | The agent has no handoff-call rule like the CFO's (calls sessions_send with sessionKey agent:cos:main) | Needs an instruction change approved by the CEO (see PENDING P-48) |

## Never paste here
Tokens (xoxb-, xapp-, xoxp-), channel IDs, user IDs, the gateway token, the VM address.

## History
- 2026-11-10 handover 30: first use (CLO). Manifest from OpenClaw's Slack docs; not compared with the four older apps.
