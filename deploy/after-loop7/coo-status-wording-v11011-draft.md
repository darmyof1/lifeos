# COO status questions, second wording: ask the agent to read its own state files (DRAFT, waiting for the CEO's approval; nothing is approved here)

Why: handover 33 installed the first wording (APR-0132, COO v1.10.10). It works when the item was routed through the COO. On the CEO's real question ("what did I last tell the CFO?", 2026-11-17 17:12) the COO asked the CFO, but the CFO answered from its main session, which does not hold what the CEO typed directly in the CFO's own Slack channel, so the answer was wrong. Also, in one test the COO's answer repeated a file path from the CFO's reply. The agents do keep durable state files in their own workspaces (budget log, lifestyle log, health plan, calendar journal), and those do hold the real last entries. So the question should send the agent to its files, not to its conversation memory.

## COO: instruction set v1.10.11 (agent-files/executive/coo/AGENTS.md)

Replace the v1.10.10 rule (same place, the last rule of "Loop 1 rules (all agents)") with:

    - Status questions (instruction set v1.10.11): you cannot see what the CEO says to another agent directly, and you may not remember what other agents routed through you in another session. When the CEO asks what he last told an agent, what an agent did, or whether something was logged, do not answer from your own memory. Send that agent one question: read the last entries in your own state files and tell me what was last logged for the CEO, with the date, in one or two sentences. Do not answer from conversation memory. Relay its answer, naming the agent and the run ID. If the agent finds nothing, say so. Never write a file path or a file name in your answer; say which agent holds the record and that the CEO can ask it directly.

## What stays the same
- One file changes on the VM, the COO instruction file (gateway stopped, backup, commit in the workspace, as handovers 31 to 33 did), plus the health-check version line. No other agent file, config, crontab or plugin change.
- The run ID rule (v1.10.9) applies as before.

## Limits (said plainly)
- This is still a behaviour rule: it depends on the chief reading its file. If the chief answers from memory anyway, the answer can be wrong again. The code-written routing log (P-51) is the deterministic fix and stays planned.
- It only covers items that an agent wrote to its state files. A request the agent did not log is not found.
- Not fixed here: in three handover 33 runs the CFO reported a "session-change error" on its reply call to the COO (the content still arrived). Cause not investigated.

## What the handover would check (for information, not a decision)
- Synthetic items created first; status questions in fresh sessions for the CFO and the CLO give answers from the files, with the agent's name and a run ID, and no file path or file name.
- The CEO's real status question again (raw not copied: real data): the answer should now name the real last item.
- Routing and the earlier checks stay as in handover 33. No reset, no re-seed, no raw copies of real items.

## Question
Reply "approved as written" or tell me the changes. Approval would be recorded as the next APR in your words.
