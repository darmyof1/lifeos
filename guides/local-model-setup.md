# Local model setup for OpenClaw (test VM)

Status: working for text replies and for one verified tool call (see section 4). Last verified: 2026-10-21 on AWS EC2 g4dn.xlarge (Tesla T4) with OpenClaw 2026.10.5 and Ollama.
Not yet verified: tool calls over many turns and long threads. See "What is not established" below.

Purpose: register a local Ollama model in OpenClaw, and run the checks to do before blaming the agent.

## Before you start
- Use a separate state folder for every test. Never use the default ~/.openclaw for a test. In every terminal you use:
  export OPENCLAW_STATE_DIR=~/spkNN/state OPENCLAW_CONFIG_PATH=~/spkNN/state/openclaw.json
- Stop any gateway you started for an earlier test. openclaw gateway run is foreground; press Ctrl-C.
- Patch files contain no secrets. Keep it that way.

## 1. Check Ollama on its own
    ollama list
    time ollama run <model> "Reply with the word OK only."

If this hangs or takes minutes, the problem is Ollama or the machine, not OpenClaw. Measured here: qwen2.5:1.5b answered in about 3 seconds. llama3.1:8b took 3 min 14 s on its first (cold) load.

If a runner is stuck (ollama ps shows "Stopping..." with the model at 100% CPU): ollama stop <model>, then repeat this step.

## 2. Create a model variant with the context size set
Ollama uses its own default context size unless the model sets one. OpenClaw sends a large request, so set the size in Ollama:

    cat > ~/spkNN/Modelfile <<'EOF'
    FROM qwen2.5:1.5b
    PARAMETER num_ctx 32768
    EOF
    ollama create qwen25-32k -f ~/spkNN/Modelfile
    ollama show qwen25-32k --parameters | grep -i num_ctx

Expect num_ctx 32768. In testing, setting contextWindow in OpenClaw alone did not stop overflow errors.

## 3. Register the model in OpenClaw (dry run first)
Save this as ~/spkNN/ollama-provider.json5:

    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://127.0.0.1:11434",
            api: "ollama",
            timeoutSeconds: 300,
            models: [ { id: "qwen25-32k", name: "qwen25-32k", contextWindow: 32768 } ]
          }
        }
      }
    }

Notes from the Ollama configuration docs:
- api must be "ollama", and baseUrl must have no /v1 suffix. /v1 selects OpenAI-compatible mode, where tool calling is not reliable.
- timeoutSeconds: 300 is recommended for cold local models.

Then:

    openclaw config patch --file ~/spkNN/ollama-provider.json5 --replace-path models.providers.ollama.models --dry-run
    openclaw config patch --file ~/spkNN/ollama-provider.json5 --replace-path models.providers.ollama.models
    openclaw models set ollama/qwen25-32k
    openclaw models status | head -12

The --replace-path flag is needed when the model list already has entries. Without it the patch is refused.

## 4. Tool calling: the settings, the direct test, and the Slack proof

Every agent turn sends the tool catalog. Two settings decide what the model sees:
- tools.profile: messaging (text only, used for the Slack test) or coding (adds shell and file tools). Profiles in this build: minimal, coding, messaging, full.
- tools.toolSearch.enabled: when true, the model sees a compact list of names and must call a search tool to reach the shell tool. The local model never made that call. When false, the full tool list is sent.

Observed on 2026-10-21: the tool-search line reported 18 tools with the messaging profile, and 34 to 43 with the coding profile.

For a tool test, save this as ~/spk04/tools-test.json (no secrets in it):

    {
      "tools": {
        "profile": "coding",
        "toolSearch": { "enabled": false }
      }
    }

Dry run, then apply, then check:

    source ~/spk04/env.sh
    openclaw config patch --file ~/spk04/tools-test.json --dry-run
    openclaw config patch --file ~/spk04/tools-test.json
    openclaw config get tools

The change reloads without a gateway restart. Afterwards, set the profile back to messaging with the same steps, using {"tools": {"profile": "messaging"}}. The coding profile lets the bot run commands on the machine, so keep test prompts harmless and never ask it to print files from ~/spk04.

Direct test, outside OpenClaw. Expect a tool_calls entry that names exec. If it prints null, fix the model before testing in Slack:

    curl -s http://127.0.0.1:11434/api/chat -d '{"model":"qwen35-32k:latest","stream":false,"think":false,"messages":[{"role":"user","content":"Run the shell command: echo -n TOOL-PROOF-7 | sha256sum"}],"tools":[{"type":"function","function":{"name":"exec","description":"Run a shell command and return its output","parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}}]}' | python3 -c 'import json,sys; m=json.load(sys.stdin)["message"]; print("tool_calls:", json.dumps(m.get("tool_calls"))); print("content:", (m.get("content") or "")[:200])'

Slack proof, with a value the model cannot guess. Compute the expected answer on the VM first:

    echo -n TOOL-PROOF-9 | sha256sum | cut -c1-12

That prints 69de5eddebdb. Post a top-level message in the channel:

    @<bot name> run the shell command "echo -n TOOL-PROOF-9 | sha256sum" and reply with only the first 12 characters of the hash

Expect 69de5eddebdb. On 2026-10-21 the bot replied 69de5e, which is the right value, but only 6 characters. The log line to check is a tool_execution_started milestone in the agent-turn-timing subsystem.

Results on 2026-10-21 (AWS, qwen35-32k): the direct test returned an exec call, and the OpenClaw test ran the command once tool search was off. llama3.1-32k wrote its tool calls as text and never ran them.

## 5. Run one turn with the output saved
    openclaw agent --agent <id> --local --session-id <new-id> --timeout 900 --message "<message>" 2>&1 | tee ~/spkNN/run.txt

- Use a new --session-id for each attempt. A stuck earlier session left a message that was dropped on the next run.
- Do not pipe a long run through tail. Nothing shows until the run ends.
- Expect the first turn with a local model to be slow.

## When a turn does not reply
- "Unknown model ... no matching models.providers[ollama].models[] entry": step 3 was not applied, or the id in models set does not match the entry.
- "Refusing to replace models.providers.ollama.models": add --replace-path.
- "Context overflow ... input length exceeds the context length": set num_ctx in Ollama (step 2).
- "transient same-model retry ... reason=timeout": the turn is too slow for the timeout. Narrow the tools (step 4), raise timeoutSeconds, and check ollama ps.
- "lane task error ... This operation was aborted": the command was stopped, by Ctrl-C or a closed terminal.
- "agent database stale lease: owner-pid-dead" after a stopped run: not an error by itself. The integrity gate reported healthy.

- "Reply repeats the request text, or copies an earlier wrong answer": the channel session holds the earlier turns. Top-level posts in a channel all share one channel session, so posting at the top level does not start a clean session. Replies inside a thread get their own session. To start clean, delete the channel session with the gateway running: openclaw sessions delete <key> --agent <id> --dry-run, then the same command without --dry-run.
- "Reply is plain text and no command ran": check openclaw config get tools. With toolSearch on, the model may never reach the shell tool. Set it as in section 4, then repeat the direct test.

## What is not established
- Tool calling was verified once, with one command, and the reply was 6 characters instead of 12. Repeat it in a fresh session before relying on it.
- The prompt size with the full tool list on a long thread is not measured. The 32k limit may be reached.
- /new authorization is unresolved. See guides/slack-multi-identity.md.
- Slack image downloads fail because the apps lack the files:read scope. The scope was not added. Adding it would bring images into the context.
- Other local models for tool calls: not tested.
- The agent:main:main session ran a tool at 00:55 on 2026-10-21. Its tool profile is not known, and the cause was not checked.

## References
- https://docs.openclaw.ai/providers/ollama/configuration
- https://docs.openclaw.ai/providers/ollama/troubleshooting
- https://docs.openclaw.ai/concepts/model-providers
