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

## Troubleshooting
- "Config file not found" from config validate: no patch has been applied. Apply the baseline (step 4).
- Revoked key: a copy of an old key stays revoked. Create a new key in the life-os project.
- A command run from a terminal without the env file reads the default folder. Source ~/loop1/env.sh first.

## What is not established
- Whether team create gives the four Loop 1 agents the right names and roles.
- Whether set-identity names appear in Slack (Spike 10).
- Whether the gateway starts on this config. It has not been started.

## Never paste here
Key values, tokens, Slack IDs, VM addresses, or the contents of any env file.

## History
- 2026-10-22: written from the baseline run on the Oracle VM (fix-44).
