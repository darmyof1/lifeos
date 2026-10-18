# Local model setup for OpenClaw (test VM)

Status: draft. Verified on the test VM on 2026-10-18 with OpenClaw 2026.10.4 and Ollama.
Not yet verified: that a local model completes a full agent turn on this VM in a reasonable time. See research/spikes/SPK-03-agent-isolation.md.

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

## 4. Narrow the tool list
Every agent turn sends the tool catalog. In testing it was 55 tools by default. Add this to the patch:

    tools: { profile: "coding" }

The count went down to 41. Check the line "tool-search: cataloged N tools" in the run output. Profiles in this build: minimal, coding, messaging, full (from openclaw config schema). Not verified: that the read tool is included in "coding".

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

## What is not established
- Whether a local model completes a full agent turn on the test VM in a reasonable time.
- What supportsTools and the messaging profile do. Not in the docs pages read.
- Any change in OpenClaw releases after 2026.10.4. Release notes were not read.
- Docker is needed to turn sandbox isolation on. It is not installed and is deferred to the deploy.

## References
- https://docs.openclaw.ai/providers/ollama/configuration
- https://docs.openclaw.ai/providers/ollama/troubleshooting
- https://docs.openclaw.ai/concepts/model-providers
