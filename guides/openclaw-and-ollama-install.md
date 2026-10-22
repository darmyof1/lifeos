# OpenClaw and Ollama on a GPU instance (AWS): install guide

Status: working
Last verified: 2026-10-21 on AWS EC2 g4dn.xlarge (Tesla T4), user ubuntu
Tool version: OpenClaw 2026.10.5 (1b58cb9). Ollama: record the output of ollama --version at install time.
Owner: CEO

## What this is for
Build a GPU test host from nothing: OpenClaw with the Slack plugin, Ollama with a 32k-context Qwen model, and the two Slack identities. The steps are in the order that worked. Where a step failed before, the note says so.

## Before you start (HUMAN)
- An instance: g4dn.xlarge (one Tesla T4). Use a security group that allows SSH from your own address only. Use placeholders in every note: <HOST>, <KEY_FILE>, <MAC_FOLDER>.
- Two Slack apps (spk04-a and spk04-b) and one OpenAI project key. Their values go in env files on the VM, edited with nano. Never paste the values into chat or into a repo file.
- Terminate the instance when the test is finished. A stopped instance keeps its disk and its secrets.

## 1. Connect and check the GPU
    ssh -i <KEY_FILE> ubuntu@<HOST>
    nvidia-smi

Expect a table that names a Tesla T4. If nvidia-smi is not found, the driver is missing. Install the driver before Ollama. Otherwise the model runs on the CPU, which was too slow on the Oracle VM.

## 2. Install OpenClaw
Set the npm global folder first, so no install needs sudo:

    mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global
    echo 'export PATH=$HOME/.npm-global/bin:$PATH' >> ~/.bashrc
    source ~/.bashrc

Install OpenClaw:

    npm install -g openclaw
    openclaw --version

Expect 2026.10.5, the version this guide was verified on. To pin a different version, use npm's version suffix after the package name. If openclaw says "command not found", the PATH line is not loaded. Run source ~/.bashrc or open a new shell.

Note: the install command above is the one this guide assumes. The exact method used in the test run was not recorded. Check docs.openclaw.ai before using it on another host.

If an installer starts the setup wizard, press Ctrl-C. Do not answer its prompts. The wizard creates ~/.openclaw, which the test must not use. Every test uses its own state folder (section 6).

## 3. Install the Slack plugin before the first gateway start
    openclaw plugins install @openclaw/slack
    openclaw plugins list

Without it, the gateway logs "no channel plugin is installed or loadable (no-channel-owner)" and the Slack channels do nothing.

## 4. Install Ollama and create the 32k model
    curl -fsSL https://ollama.com/install.sh | sh
    ollama --version
    ollama pull qwen3.5:latest
    cat > ~/Modelfile-qwen35-32k <<'EOF'
    FROM qwen3.5:latest
    PARAMETER num_ctx 32768
    EOF
    ollama create qwen35-32k -f ~/Modelfile-qwen35-32k
    ollama show qwen35-32k

Expect Capabilities to list tools and thinking, and Parameters to show num_ctx 32768. Without the 32k setting, OpenClaw's prompt overflows the context. See guides/local-model-setup.md, step 2.

## 5. Test the model directly, before OpenClaw
Run the direct tool-call test in guides/local-model-setup.md, section 4. Expect a tool_calls entry that names exec. If it prints null, fix the model before going further.

## 6. Set up the state folder and the env files
    mkdir -p ~/spk04/state
    # run on the Mac, not the VM: copy the transfer folder contents
    scp -i <KEY_FILE> -r <MAC_FOLDER>/. ubuntu@<HOST>:~/spk04/
    chmod 600 ~/spk04/*.env ~/spk04/gateway-token

Move openclaw.json into ~/spk04/state/ and the workspaces to ~/spk04/ws-b and ~/spk04/state/workspace. Then create ~/spk04/env.sh. It holds no secrets:

    export OPENCLAW_STATE_DIR=~/spk04/state
    export OPENCLAW_CONFIG_PATH=~/spk04/state/openclaw.json

Run source ~/spk04/env.sh in every terminal you use for the test. A terminal without it reads the default state folder and shows no channels.

To load the Slack and OpenAI values for the gateway, without printing them:

    set -a; source ~/spk04/slack.env; source ~/spk04/openai.env; set +a

Delete <MAC_FOLDER> after the copy is verified. It holds secrets.

## 7. Apply the model settings (dry run first)
Save this as ~/spk04/qwen-patch.json. It holds no secrets; the apiKey is a fixed placeholder for the local provider:

    {
      "models": {
        "providers": {
          "ollama": {
            "baseUrl": "http://127.0.0.1:11434",
            "api": "ollama",
            "apiKey": "ollama-local",
            "timeoutSeconds": 300,
            "models": [{ "id": "qwen35-32k:latest", "name": "qwen35-32k:latest" }]
          }
        }
      },
      "agents": {
        "defaults": { "model": { "primary": "ollama/qwen35-32k:latest" } },
        "entries": { "spk04-b": { "model": "ollama/qwen35-32k:latest" } }
      }
    }

Then:

    source ~/spk04/env.sh
    openclaw config patch --file ~/spk04/qwen-patch.json --replace-path models.providers.ollama.models --dry-run
    openclaw config patch --file ~/spk04/qwen-patch.json --replace-path models.providers.ollama.models
    openclaw config get agents.defaults.model

Expect ollama/qwen35-32k:latest. The --replace-path flag is needed because the model list already has entries. If OpenAI handles side calls, set agents.defaults.utilityModel as described in guides/slack-multi-identity.md.

## 8. Tool settings
- Text only (default for the Slack test): {"tools": {"profile": "messaging"}}
- Tool test: see guides/local-model-setup.md, section 4. Set the profile back to messaging afterwards.

## 9. Start the gateway
Terminal 1, in the foreground:

    source ~/spk04/env.sh
    set -a; source ~/spk04/slack.env; source ~/spk04/openai.env; set +a
    openclaw gateway run

Stop it with Ctrl-C in the same terminal. Do not run openclaw gateway stop from another terminal: it once stopped the default service. A second gateway on the same state folder is refused.

In a second terminal:

    source ~/spk04/env.sh
    openclaw channels status --probe

Expect both Slack accounts to be connected.

## 10. Check in Slack
Post a top-level message in the channel, for example: @<bot name> reply with only the word OK. Top-level posts share one channel session. Replies inside a thread get their own session. See guides/local-model-setup.md, troubleshooting.

## Known gaps (not fixed)
- /new is refused as control-command-unauthorized, even with the owner list set. See guides/slack-multi-identity.md.
- Slack image downloads fail because the apps lack the files:read scope. The bot logs the failure and continues. Adding the scope would bring images into the context.
- Warnings in the log: agent database stale lease or Worker owner closed, and MaxListenersExceededWarning. Recorded, not errors.

## Never paste here
Env values, the gateway token, the OpenAI key, Slack tokens, workspace or channel IDs, and VM addresses.

## History
- 2026-10-21: written from the AWS rebuild (fix-42). The instance was terminated after the test.
