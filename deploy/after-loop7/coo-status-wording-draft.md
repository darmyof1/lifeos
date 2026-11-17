# COO status questions: ask the agent instead of answering from memory (DRAFT, waiting for the CEO's approval; nothing is approved here)

Why: on 2026-11-15 the CEO asked the COO what he had last told the CLO. A purchase the CLO had routed through the COO was relayed to the CFO in the COO's main session, but the question was answered in the COO's Slack channel session, which had not seen it, so the COO quoted an older item. Two sessions, no shared memory. The COO has no file tools, so a shared note file is not possible. This wording uses the route the COO already has.

## COO: instruction set v1.10.10 (agent-files/executive/coo/AGENTS.md)

Add one rule at the end of "Loop 1 rules (all agents)":

    - Status questions (instruction set v1.10.10): you cannot see what the CEO says to another agent directly, and you may not remember what other agents routed through you in another session. When the CEO asks what he last told an agent, what an agent did, or whether something was logged, do not answer from your own memory. Send that agent one question: what did the CEO last ask you and what did you do, in one or two sentences. Relay its answer, naming the agent and the run ID. If the agent cannot answer, say so. Do not give file paths; say which agent holds the record and that the CEO can ask it directly.

## What stays the same
- No other agent file, config, crontab or plugin changes. One file changes on the VM: the COO instruction file (gateway stopped, backup, commit in the workspace, as handovers 31 and 32 did).
- The run ID rule (v1.10.9) applies to the question like to any request.

## What the handover would check (for information, not a decision)
- A question "what did I last tell the CLO" gets an answer that comes from the CLO and names it, with a run ID, and no path.
- The 2026-11-15 case replayed with synthetic names: a purchase routed CLO to COO to CFO, then the CEO asks the COO in a different session what he told the CLO.
- Routing and the earlier checks stay as in handover 32.

## Question
Reply "approved as written" or tell me the changes. Approval would be recorded as the next APR in your words.
