# Slack with two bot identities in OpenClaw — guide

Status: working (two identities; each agent posts as its bound account). Leakage check and local-model posting not done.
Last verified: 2026-10-19 on Oracle VM, Ubuntu 24.04 arm64
Tool version: OpenClaw 2026.10.5 (1b58cb9)
Owner: CEO

## What this is for
One OpenClaw Gateway, two Slack accounts, two agents. A message from agent spk04-b shows "spk04-b" with the APP badge. A message from agent main shows "spk04-a". The test uses the test state folder ~/spk04. Use the same steps with your own folder and names.

The agent turns use a hosted model (openai/gpt-6-luna in config). Local model turns did not complete on this VM. See guides/local-model-setup.md.

## Before you start (HUMAN)
- Every terminal needs the state variables before any openclaw command. Create this file once:

    printf 'export OPENCLAW_STATE_DIR=~/spk04/state OPENCLAW_CONFIG_PATH=~/spk04/state/openclaw.json\n' > ~/spk04/env.sh

  Then run source ~/spk04/env.sh in each terminal. Without it, openclaw uses the default state folder (~/.openclaw) and the default gateway service. In the test, a gateway stop without the variables stopped the default service that the Mac tunnel uses.
- Two Slack apps in the test workspace. Create each one From a manifest.
  - Do not use the AI agent template: it makes an AGENT identity, not APP.
  - Do not use Starter or Blank apps.
- Tokens for each app. Never paste them in chat.
  - Bot User OAuth Token, starts with xoxb-. Find it under OAuth & Permissions, after Install to Workspace. Name in the env file: SLACK_BOT_TOKEN (app A) and SLACK_BOT_TOKEN_B (app B).
  - App-Level Token, starts with xapp-. Find it under Basic Information, App-Level Tokens, Generate Token and Scopes, scope connections:write. Name: SLACK_APP_TOKEN and SLACK_APP_TOKEN_B.
  - Do not use the User OAuth Token (starts with xoxp-). It acts as a person, not as the bot.
- An OpenAI API key, kept in ~/spk04/openai.env as OPENAI_API_KEY.
- The test channel ID. Open the channel, click its name, and copy the ID from the bottom of the About tab. It starts with C. Use the ID, not the name.
- Invite each bot to the test channel. In the channel, type /invite @spk04-a and /invite @spk04-b.

## Install
1. Save the two manifests. Both must have different names.

Manifest for app A, saved as ~/spk04/spk04-slack-manifest.json:

    {
      "display_information": { "name": "spk04-a", "description": "SPK-04 test bot. Test workspace only." },
      "features": { "bot_user": { "display_name": "spk04-a", "always_online": true } },
      "oauth_config": { "scopes": { "bot": ["chat:write", "chat:write.customize", "channels:read", "channels:history"] } },
      "settings": { "socket_mode_enabled": true }
    }

Manifest for app B, saved as ~/spk04/spk04-b-slack-manifest.json: the same, with spk04-b in place of spk04-a in every name field.

Paste each into Slack: Create New App, From a manifest, pick the workspace, paste the JSON, Create. Then Install to Workspace.

2. Install the Slack plugin.

    openclaw plugins install @openclaw/slack

Expected: "Installed plugin: slack" and "Saved for the next Gateway start." Check it:

    openclaw plugins list | grep -i slack

Expected: one line that shows slack.

## Configure and authenticate
1. Create the token file. Mode 600, so only your user can read it.

    touch ~/spk04/slack.env && chmod 600 ~/spk04/slack.env

Open it with nano and add four lines: SLACK_BOT_TOKEN=, SLACK_APP_TOKEN=, SLACK_BOT_TOKEN_B=, SLACK_APP_TOKEN_B=, each followed by the value. Check the spelling. In the test, the name was typed as LACK_BOT_TOKEN_B (missing S) and the Gateway could not find it.

2. Check the names and prefixes without printing values.

    awk -F= '/^SLACK_/{print $1, substr($2,1,5)}' ~/spk04/slack.env

Expected: four lines. SLACK_BOT_TOKEN xoxb-, SLACK_APP_TOKEN xapp-, SLACK_BOT_TOKEN_B xoxb-, SLACK_APP_TOKEN_B xapp-.

If a name is wrong, fix only that name. Example for the typo above:

    sed -i 's/^LACK_BOT_TOKEN_B=/SLACK_BOT_TOKEN_B=/' ~/spk04/slack.env

Run the awk check again.

3. Stop any Gateway you started for this state folder (Ctrl-C in its terminal). The config commands below need the Gateway stopped.

Set the state folder in every terminal you use:

    export OPENCLAW_STATE_DIR=~/spk04/state OPENCLAW_CONFIG_PATH=~/spk04/state/openclaw.json
    openclaw setup --baseline
    openclaw config set gateway.mode local
    openclaw config set gateway.port 19001

Expected: each command prints "Updated config". gateway.mode local is required, or the Gateway refuses to start. Port 19001 avoids the default openclaw-gateway.service on 18789. Do not stop the default service.

4. Write the Slack config. The patch file holds only references to environment variables, never the values. Save as ~/spk04/slack.accounts.json5:

    {
      channels: {
        slack: {
          enabled: true,
          mode: "socket",
          accounts: {
            default: {
              enabled: true,
              mode: "socket",
              botToken: { source: "env", provider: "default", id: "SLACK_BOT_TOKEN" },
              appToken: { source: "env", provider: "default", id: "SLACK_APP_TOKEN" },
            },
            "spk04-b": {
              enabled: true,
              mode: "socket",
              botToken: { source: "env", provider: "default", id: "SLACK_BOT_TOKEN_B" },
              appToken: { source: "env", provider: "default", id: "SLACK_APP_TOKEN_B" },
            },
          },
        },
      },
    }

Do not put botToken or appToken at the top level of channels.slack. They are ignored when accounts exist (see the cleanup item below).

5. Load the variables in the same shell, then dry-run the patch. The dry run needs the variables set, or it stops with "env ... missing or empty".

    set -a; source ~/spk04/slack.env; set +a
    openclaw config patch --file ~/spk04/slack.accounts.json5 --dry-run

Expected: the list of changes, with no error. Then apply it:

    openclaw config patch --file ~/spk04/slack.accounts.json5

Expected: "Updated config" and a backup line (the backup file ends in .bak). If the patch is refused for a list that already exists, read the message. --replace-path was needed for a model list in the Ollama test; it was not needed for Slack.

6. Create the second agent and bind both agents. --bind needs the Gateway stopped.

    openclaw agents add spk04-b --workspace ~/spk04/ws-b --non-interactive
    openclaw agents bind --agent main --bind slack:default
    openclaw agents bind --agent spk04-b --bind slack:spk04-b
    openclaw agents list --bindings

Expected: the add prints "Agent: spk04-b". The binds print "Added bindings" with slack accountId=default and slack accountId=spk04-b. The list shows main routing Slack default, and spk04-b routing Slack spk04-b.

Note: main also has a catch-all rule, slack accountId=*, from setup. A send on an account with no binding goes to main. Review this before any real deployment.

7. Set the model and the tool profile (Gateway still stopped).

    openclaw models set openai/gpt-6-luna
    openclaw config set agents.defaults.utilityModel openai/gpt-6-luna
    openclaw config set tools.profile messaging
    openclaw config get tools.profile

Expected: messaging. The docs list the profiles as minimal, coding, messaging and full. They do not confirm which tools each profile includes, but in testing the messaging profile let both agents send.

Check the key is seen by the Gateway:

    set -a; source ~/spk04/openai.env; set +a
    openclaw models status 2>&1 | grep -i openai

Expected: a line that says source env: OPENAI_API_KEY.

8. Start the Gateway with all the variables loaded in the same shell. Use a full start after any change to the env files. A reload inside a running Gateway keeps the old environment.

    set -a; source ~/spk04/slack.env; source ~/spk04/openai.env; set +a
    openclaw gateway run

Leave it running in its own terminal. Startup took about 30 to 50 seconds on this VM. Wait for these lines:
- "http server listening"
- "ready"
- "[slack] [default] starting provider" and "[slack] [spk04-b] starting provider"
- "slack socket mode connected", twice

9. Verify, from a second terminal with the same OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH:

    openclaw channels status --probe

Expected: both accounts show "enabled, configured, running, connected, bot:config, app:config, works".

## Test the identities
Get the channel ID (see Before you start). Replace <CHANNEL_ID> in each command before you press Enter. A run with the placeholder left in was cancelled and wasted a run.

Agent spk04-b, expect the message from spk04-b:

    time openclaw agent --agent spk04-b --session-id spk04-bind-b1 --timeout 300 --message "Use the message tool to send this exact text to Slack channel <CHANNEL_ID>: spk04-b identity test 1. Then reply DONE only." 2>&1 | tee ~/spk04/bind-b1.txt

Expected: DONE, and a message in the channel from spk04-b with the APP badge. Our run: 14.7 s.

Agent main, expect the message from spk04-a:

    time openclaw agent --agent main --session-id spk04-bind-a1 --timeout 300 --message "Use the message tool to send this exact text to Slack channel <CHANNEL_ID>: spk04-a identity test 1. Then reply DONE only." 2>&1 | tee ~/spk04/bind-a1.txt

Expected: DONE, and a message from spk04-a with the APP badge. Our run: 22.1 s.

Use a new --session-id for every attempt. Do not pipe the run through tail, or nothing shows until it ends.

## Verify
| Check | Command | Expected |
|---|---|---|
| Both accounts live | openclaw channels status --probe | both connected, works |
| Bindings | openclaw agents list --bindings | main to default, spk04-b to spk04-b |
| Identity, agent b | the spk04-b turn above | DONE, and spk04-b APP in the channel |
| Identity, agent a | the main turn above | DONE, and spk04-a APP in the channel |

## What this does not prove
- The stored session transcript records the account argument of the send as [Truncated]. The Gateway log does not record the outbound account for a successful send. So which account a send used is shown by the binding and by the Slack display name, not by a recorded argument.
- A test that would fail if an agent used the wrong account is not done.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| channels add fails with "The CLI command failed." and no reason | Slack plugin not installed | openclaw plugins install @openclaw/slack, then use the config patch route in this guide |
| Gateway refuses to start: "existing config is missing gateway.mode" | gateway.mode not set | openclaw config set gateway.mode local |
| Port 18789 in use | default openclaw-gateway.service holds it | set gateway.port 19001 for the test state; leave the default service running |
| "secret reference not found" for the second account | Gateway started before the SLACK_*_B variables were added; a reload keeps the old environment | Stop the Gateway and start it again with the env files loaded |
| "unresolved" for accounts.default | accounts map present but the default account missing | Add accounts.default with the same references (step 4) |
| "env ... missing or empty" on the dry run | variables not set in this shell | set -a; source ~/spk04/slack.env; set +a, then run again |
| Variable name typo (LACK_BOT_TOKEN_B) | missing S in the name | sed fix in step 2, then the awk check |
| SECRETS_REF_IGNORED_INACTIVE_SURFACE for top-level botToken or appToken | top-level tokens unused when accounts exist | Remove the top-level tokens (cleanup item below) |
| config set or patch refused while the Gateway runs | docs: these need the Gateway stopped | Stop the Gateway, run the command, start the Gateway again |
| "A Gateway is running for this state directory" with --local | the Gateway owns the state folder | Run without --local, or stop the Gateway with openclaw gateway stop |
| "Gateway auth token was missing. Generated a runtime token" | no gateway token is saved; it changes on each start | Open item below |
| Message shows the AGENT badge, not APP | app created with the AI agent template | Create the app again From a manifest |
| Agent says DONE, nothing in the channel | wrong channel ID, or the bot is not in the channel | Check the ID; /invite @spk04-b in the channel |
| No reply in Slack. Log shows "Inbound app_mention", then reason "control-command-unauthorized" | /new is an owner-only command and the sender is not in commands.ownerAllowFrom | Set commands.ownerAllowFrom. In the test, neither the plain user ID nor the slack-prefixed ID authorized /new. Still open |
| Slack reply says "This OpenClaw bot can't reply here because this channel isn't in its OpenClaw channel allowlist" | the channel is not listed under the account (groupPolicy is allowlist) | Add channels.slack.accounts.spk04-b.channels.<CHANNEL_ID>.enabled true (see Config reference) |
| Mention in Slack, no "Inbound app_mention" line in the log at all | the Slack app has no event subscription for app_mention | Event Subscriptions: enable, add app_mention under bot events, add scope app_mentions:read, Reinstall to Workspace (see the section above) |
| Gateway terminal prints "Another gateway (pid N) already owns this state directory; refusing..." | a second gateway run on the same state folder | Do not run openclaw gateway stop. Ctrl-C the refused terminal. The running gateway is not affected |
| config patch prints "Refusing to replace models.providers.ollama.models" | the patch would remove existing model entries | Only if the replacement is intended: add --replace-path models.providers.ollama.models, after a dry run |
| Local model turn fails: "the input length exceeds the context length" and "Auto-compaction failed" | the plain llama3.1:8b model runs with Ollama's small default context; OpenClaw sends about 34 KB of prompt | Use llama3.1-32k:latest. ollama show must print num_ctx 32768 under Parameters |
| Thread reply served by openai/gpt-6-luna although the agent is set to ollama | new sessions take the default model; not explained | Open item. Before any local test, check the model-fetch line in the log shows provider=ollama |
| Log line "MaxListenersExceededWarning: Possible EventEmitter memory leak" at gateway start | a known warning in this build | Not an error. Record it and move on |
| "event loop degraded" in channels status --probe | VM CPU saturated during a turn | Expected on this VM; it slows turns. It is not a Slack fault |
| Turn aborted with "caller_signal_aborted" | Ctrl-C, or the terminal was closed | Run again with a new --session-id |
| "openclaw gateway stop" reports "Stopped systemd service: openclaw-gateway.service" | the command ran without the state variables, so it stopped the default service | source ~/spk04/env.sh first. Restart the default service with systemctl --user start openclaw-gateway.service (this is what the Mac tunnel uses) |
| Gateway terminal shows "waiting for Gateway state ownership held by another OpenClaw process" | a second gateway run on the same state folder | Ctrl-C the second terminal. Only one gateway run per state folder |
| "liveness warning: event_loop_utilization=1" and a Slack "SMWebsocketError" shortly after | the duplicate gateway competing for the same database | Stop the duplicate. Check channels status --probe; the socket reconnects on its own in the test |
| Gateway log shows "agent model: ollama/..." after a start | the gateway ran on the default state folder, not spk04 | Check the terminal had the state variables; the spk04 start shows "agent model: openai/gpt-6-luna" |


## Never paste here
- Slack tokens (xoxb-, xapp-, xoxp-), the OpenAI key, the gateway auth token, and any value from slack.env or openai.env.
- Real workspace IDs and the VM address. Use <CHANNEL_ID> and the placeholder names.

## Cleanup verified 2026-10-19
- Top-level channels.slack botToken and appToken removed with openclaw config unset. The log shows "Removed channels.slack.botToken" and "Removed channels.slack.appToken".
- Slack still starts and connects with accounts only. The 22:02 start printed "[slack] [default] starting provider", "[slack] [spk04-b] starting provider" and "slack socket mode connected" twice. No SECRETS_REF_IGNORED lines.
- Gateway auth token saved: gateway.auth.mode token and gateway.auth.token set from ~/spk04/gateway-token (mode 600). The 22:02 start printed no "auth token was missing" line.
- The token is a plain value in the test config. The docs read on 2026-10-19 did not confirm that gateway.auth.token accepts a SecretRef.
- A direct send from spk04-b (openclaw message send --channel slack --account spk04-b -t channel:<CHANNEL_ID>) posted as spk04-b APP after the cleanup.
- The cleanup script is not in the repo. Its steps are above.

## Model in use (verified 2026-10-19)
- Main agent: openai/gpt-6-luna. Utility model (titles, recaps, narration): set explicitly to openai/gpt-6-luna. Before this change the utility model was unset, so OpenClaw used the provider's built-in small model, gpt-5.6-luna. That is where the gpt-5.6-luna requests came from.
- Check what is served: the gateway log line model-fetch ... model= shows the model on each response. After the change, the test turn showed model=gpt-6-luna and no gpt-5.6-luna.
- Check what is billed: OpenAI usage dashboard, life-os project, 7-day range, Spend categories. Billing lags, so check again later. On 2026-10-19 this view showed gpt-6-luna cache writes ($0.006) and no gpt-5_6-luna rows.
- Billing re-check 2026-10-20 (life-os chip set, 1-day view, Spend categories):
    - gpt-6-luna: cache writes $0.02, cached input $0.014, input $0.004, output $0.002. Total about $0.04 for the day.
    - gpt-5_6-luna: $0 on every line (input, output, cache writes, cached input, cache writes 12hr).
    - text-embedding-3-small: $0.
    - Personal October total moved from $1.17 (2026-10-19) to $1.21. The $0.04 increase matches the gpt-6-luna spend.
    - Conclusion: the configured model (gpt-6-luna) is the one billed. The old model shows no spend since the switch. Billing is confirmed for the test.

- Check the config: openclaw models status 2>&1 | grep -E 'Default|Utility'. Expected both lines show openai/gpt-6-luna.
- Prices (official model pages, 2026-10-19, per 1M tokens, short context): gpt-6-luna $0.10 input, $0.01 cached input, $0.125 cache writes, $0.50 output. gpt-5.6-luna $0.20 input, $0.02 cached input, $0.25 cache writes, $1.20 output. gpt-6-luna is the cheaper model.
- Reasoning tokens are counted in output_tokens and billed at the output price. In the direct test, 16 output tokens included 11 reasoning tokens.
- Keys: one project key (life-os) is in ~/spk04/openai.env. Older keys were revoked on 2026-10-19. The grep for the key prefix found no other file holding a full key.

## Event subscription, channel allowlist and owner (verified 2026-10-20)
- Slack must send mentions to the Gateway. The manifest in this guide does not include an event subscription or the app_mentions:read scope, so add them in the Slack app settings, for each app (spk04-a and spk04-b):
    1. Go to api.slack.com/apps, open the app, then OAuth and Permissions. Under Bot Token Scopes, add app_mentions:read and keep the existing scopes.
    2. In the left menu, open Event Subscriptions. Turn Enable Events on. Under Subscribe to bot events, add app_mention. Click Save Changes.
    3. Click Reinstall to Workspace and approve.
    4. Open OAuth and Permissions again and check the Bot User OAuth Token. In the test it did not change, so slack.env did not need an update. If it changes, update SLACK_BOT_TOKEN_B in slack.env with nano and do a full gateway restart.
- The bot must be in the channel: /invite @spk04-b. Seeing the app in the mention list is not enough by itself.
- Channel allowlist: groupPolicy is allowlist by default, so the channel must be listed under the account. Without it, Slack replies with "This OpenClaw bot can't reply here because this channel isn't in its OpenClaw channel allowlist." The key was found in the config schema (see Config reference). The test used the gateway stopped for the change, then a restart.
- Binding check: a mention of @spk04-b opens a session keyed agent:spk04-b:slack:channel:<CHANNEL_ID>. That shows the specific accountId=spk04-b rule won over the main agent's catch-all rule (slack accountId=*). The reply came from the spk04-b app.
- Replies in a thread get their own session key (...:thread:<timestamp>), so a thread starts a new session.
- Owner-only commands: /new is refused with reason control-command-unauthorized. commands.ownerAllowFrom was set with the plain user ID and then with the slack-prefixed user ID. Neither authorized /new in the test. Not solved.

## Config reference (verified 2026-10-20)
- Per-agent model: agents.entries.<agentId>.model, value in the form provider/model, for example ollama/llama3.1-32k:latest. Check with: openclaw config get agents.entries.spk04-b.model
- Local provider: models.providers.ollama with baseUrl http://127.0.0.1:11434 (no /v1, because /v1 uses a mode where tool calling is not reliable), api ollama, timeoutSeconds 300, and a models list. Source: docs.openclaw.ai/providers/ollama/configuration.md
- Channel allowlist entry: channels.slack.accounts.<accountId>.channels.<CHANNEL_ID>.enabled, value true. Path from the schema under /properties/channels/properties/slack/properties/accounts/additionalProperties/properties/channels. Check with: openclaw config get channels.slack.accounts.spk04-b.channels
- Owner list: commands.ownerAllowFrom, an array of IDs. Schema path /properties/commands/properties/ownerAllowFrom. Effect on /new not confirmed (see above).
- Patches: always run openclaw config patch --file <file> --dry-run first. If the patch would replace a list, it refuses unless --replace-path <path> is given.
- Hot reload: patches to commands and channel entries reload live. The log shows "config change detected; evaluating reload" and "restarting slack channel". A full stop and start was used for the channel allowlist entry and the model change.
- Local models: ollama show <model> must list tools under Capabilities. llama3.1:8b, llama3.1-32k:latest and qwen3.5 list tools. llama3.1-32k:latest has num_ctx 32768. qwen25-32k:latest is the 1.5B model with a 32k context; it lists tools but looped in an earlier test.

## Open items after 2026-10-20 (Part B paused)
1. Part B (local model posting) is paused. Restart it only after item 2 is answered.
2. A thread turn on spk04-b was served by openai/gpt-6-luna, although agents.entries.spk04-b.model is ollama/llama3.1-32k:latest. An earlier channel session did use ollama. Find out why new sessions take the default model. Check the provider=... part of the model-fetch line in the log.
3. /new is refused as control-command-unauthorized, even with commands.ownerAllowFrom set. Find the sender rule before relying on /new. Until then, start a new session with a thread.
4. Done 2026-10-20 (Billing re-check 2026-10-20): gpt-6-luna is the only billed model in the test; gpt-5_6-luna shows $0.
5. Two mentions reached the gateway at 00:48:36 and 00:48:54 but only one reply was logged. Not explained.
6. Unchanged: gateway token as a plain value (SecretRef unconfirmed), kernel reboot planning.

## Open items (not verified)
1. Done 2026-10-19: top-level botToken and appToken removed; accounts-only shape connects (see Cleanup verified).
2. Done 2026-10-19: gateway auth token saved as a plain value (see Cleanup verified). Whether it can be a SecretRef is not confirmed in the docs.
3. The leakage check: the account argument of a send is not readable from the stored transcript. Find a way to read it, or design a test that would fail on the wrong account.
4. Part B: local model posting not tested. Local turns did not complete on this VM.
5. Done 2026-10-19 for the test: config, served model and billing all show gpt-6-luna after the utility change (see Model in use). Re-check billing tomorrow.
6. Kernel upgrade pending (6.17 running, 7.0 expected). A reboot restarts the default openclaw-gateway.service and stops the test Gateway. Plan it.
7. SPK-02 and SPK-03 ran on OpenClaw 2026.10.4. This guide was verified on 2026.10.5.

## History
- 2026-10-18 to 2026-10-19: SPK-04 Part A. See research/spikes/SPK-04-slack-multi-identity.md and ops/install-log.md.
