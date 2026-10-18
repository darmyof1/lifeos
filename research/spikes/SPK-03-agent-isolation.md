# SPK-03-agent-isolation - Can one agent read another agent's workspace?

Status: partial
Decision unblocked: agent isolation design (follow-up to ADR-0002); not yet answered
Owner: CEO
Date run: 2026-10-18

## Question
With sandbox isolation off (the current default), can agent spk03-b read a file in agent spk03-a's workspace? With isolation on, can it not?

## Pass criterion (from the runbook; recorded here)
- Isolation off: spk03-b reads the canary file in spk03-a's workspace. This is the expected baseline and shows the test can see a cross-read at all.
- Isolation on: spk03-b cannot read it.

## Environment
- OpenClaw 2026.10.4 on the test VM. Separate state folder under the home directory (OPENCLAW_STATE_DIR), so the SPK-02 state is untouched.
- Local model: Ollama on 127.0.0.1:11434. Installed: llama3.1:8b (about 4.9 GB) and qwen2.5:1.5b.
- Docker: not installed. Isolation on uses the Docker sandbox backend. Installing Docker is deferred to the deploy by CEO decision.

## Method
1. Setup in the test state folder: openclaw setup --baseline.
2. Two agents with separate workspaces: openclaw agents add spk03-a and spk03-b with --workspace.
3. Effective sandbox read for each agent: openclaw sandbox explain --agent.
4. Local model registered and set as default (see the guide at guides/local-model-setup.md).
5. Canary: a marker file in spk03-a's workspace; spk03-b asked to read it with openclaw agent --local.

## Results
- Step 1 PASS: setup complete. Config, workspace and session folders created under the test state folder.
- Step 2 PASS: spk03-a and spk03-b created. Each has its own workspace root and its own agent directory. agents list shows both.
- Step 3 READ: both agents report mode off, scope agent, workspaceAccess none, backend docker. agents.defaults.sandbox is unset, so the runtime default applies. Elevated is enabled: true with allowedByConfig: false. Not changed; listed as a config review item.
- Step 4 PARTIAL: the default model openai/gpt-6-astra has no key (missing auth). The default was changed to a local Ollama model. The first attempt without a provider entry failed with "Unknown model". Registration then worked. Results of the model runs are in step 5.
- Step 5 NOT OBTAINED: no reply to the canary in any run.
  - llama3.1:8b, 55 tools: the caller stopped the turn after about 18 minutes (caller_signal_aborted). No reply.
  - Two later llama runs: stopped by the caller after 17 seconds and 88 seconds. No reply.
  - llama3.1 with a 32,768 context set in OpenClaw only: context overflow errors. Ollama served the model with its own default window.
  - qwen2.5:1.5b with a 32,768 context set in Ollama and tools.profile "coding" (41 tools): provider timeout, automatic retry, no reply after about 6 minutes. Stopped by the operator. The Ollama runner was then stuck in "Stopping..." until ollama stop.

## Plain Ollama timings (no OpenClaw)
- llama3.1-32k variant, first call after create (cold load): 3 min 14 s for "Reply with the word OK only."
- qwen25-32k variant, first call after create: 3.4 s.
- qwen25-32k after ollama stop (runner reset): 3.3 s.
- llama3.1:8b and qwen2.5:1.5b answered "OK" in the other terminal (timing not recorded).

## Findings
1. On this VM, an OpenClaw agent turn with a local 8B or 1.5B model did not complete within about 15 minutes, while Ollama answers a plain prompt in seconds. OpenClaw sends a tool catalog with every turn (55 tools by default, 41 with tools.profile "coding"). The CPU has to process it before the model answers. A local model is not a practical default for agent turns on this VM.
2. Setting contextWindow in the OpenClaw provider did not stop context overflow. The window also has to be set in Ollama, through a model variant with PARAMETER num_ctx. The documentation pages read did not describe num_ctx.
3. tools.profile "coding" reduced the catalog from 55 to 41 tools. Not verified that the read tool is included, because no run reached a tool call.
4. The first load of a large model took minutes on this VM (3 min 14 s for the 8B). Plan for it.
5. A stopped or timed-out run leaves a stale lease on the agent database. The next run recovers it, and the integrity check reported healthy each time.
6. The gateway log still goes to /tmp/openclaw, outside the state folder (same as SPK-02).

## Conclusion
- Isolation off: canary not obtained. The question "can spk03-b read spk03-a's workspace" is still open.
- Isolation on: not tested. Needs Docker, which is deferred to the deploy.
- Established: two agents can be created with separate workspaces and separate agent directories, and the default sandbox mode is off.
- A local-model agent turn is not usable on this VM at the current tool catalog size.

## Next
- Re-run the canary when a usable model is available: a hosted model with a key, or a machine with more CPU. The pass criterion does not change.
- Decide the isolation default for the deploy (CEO; ADR-0002), and whether Docker is part of the deploy.

## Redaction log
- VM address, account names and paths outside the test folder omitted. No keys recorded.
