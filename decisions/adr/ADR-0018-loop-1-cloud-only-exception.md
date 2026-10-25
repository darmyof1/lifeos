# ADR-0018 - Loop 1 runs cloud-only on synthetic data (time-boxed exception)
Status: expired (Loop 1 closed 2026-10-25, APR-0071)
Date: 2026-10-22
Approval basis: APR-0052, APR-0053, APR-0054, APR-0055, APR-0056.

## Context
The local model was too slow on the CPU VM (SPK-06), and the hardware decision is deferred. The privacy gate (ADR-0003), the router and the event bus are not built. Loop 1 must prove that agents can hand work to each other before those parts exist. A round-3 audit by three AI tools (Claude, Codex, Gemini) agreed on this shape.

## Decision
- Four agents (COO, CHO, CoS, CFO) run on openai/gpt-6-luna through OpenClaw's OpenAI provider. No router, privacy gate, CLI adapter or local model.
- Agent-to-agent messages use OpenClaw's sessions_send. The CHO sends calendar adds straight to the CoS (APR-0044). Every other message goes through the COO, which forwards it to the agents that need it.
- Allowed sends: COO to CHO, CoS and CFO; CHO to COO and CoS; CoS to COO and CHO; CFO to COO. All other sends are denied.
- Transcript visibility is limited to each agent's own sessions. Spawning is denied. Run timeouts are set explicitly.
- Every write carries a run ID and an event ID, so a retried message cannot write twice.
- Synthetic data only. The calendar is a local journal (APR-0054). Slack follows APR-0053.
- Each config key is checked against openclaw config schema on the pinned version and applied with a dry run first.

## Alternatives rejected
- File event bus with a code dispatcher (ADR-0008, ADR-0011): the right durable design, but none of it is built. It is the Loop 2 target.
- Slack as the bus: agents mentioning each other can loop, and the human channel becomes the control path.
- Waiting for the local model and the privacy gate: blocks the agent loop on a hardware decision.

## Consequences
- ADR-0003 and ADR-0004 are not superseded. They apply again when this exception expires (APR-0052).
- Router-level privacy checks, model aliases and cost logging are not exercised in Loop 1.
- Behaviour across a gateway restart is tested in the acceptance run. The result decides how soon the file bus is built.
- This record expires with APR-0052.
