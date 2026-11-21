# P-51 step 2: design of the code-written send log (DRAFT, waiting for the CEO's approval; nothing is approved here)

Why: status questions (what did I last tell the CFO?) failed twice because the agents keep separate sessions and the COO answers from memory (rows 8 and 9 of ops/real-request-log.md). Wording rules (APR-0132, APR-0133) help but depend on the agents behaving. Step 1 (APR-0135, handover 36) proved that code can see the sends. Evidence: ops/p51-h36-2026-11-20/ and ops/handover-2026-11-20-claude-code-report-36.md.

## What it would do
A new small plugin ("send-log") on the gateway, hook-only and observe-only, like ceo-ledger. It adds one line to a log file in the COO workspace for each of these events, and never writes message text:
- Agent to agent: every sessions_send call (hook after_tool_call). Line fields: time (AST), from (calling agent), to (agent id taken from the target session key), run ID (the token coo-YYYYMMDD-HHMM found in the message, or "none"), result ok or error, and a fixed type word "send".
- The CEO writes in an agent's own Slack channel (hook message_received, as ceo-ledger already does): time, "CEO", which agent's channel (the Slack account name), a short hash of the text, no text.
- Example lines (synthetic): `2026-11-20 22:45 | send | coo -> cfo | coo-20261120-2245 | ok` and `2026-11-20 22:46 | ceo-message | cfo channel | 9f2c41ab`.
- One file per month in the COO workspace (state/send-log-YYYY-MM.md), append-only, never edited.

## What it fixes and what it does not
- Fixes: "when and whether". The COO can say: on that date you wrote in the CFO channel, and the COO sent the CFO a task under run ID X. It no longer depends on the COO or the CFO remembering.
- Does NOT fix: "what". The log holds no content, so to say what the item was, the COO still asks the agent to read its own state file for that date or run ID (the v1.10.11 mechanism stays, but becomes a lookup on a known time instead of a guess).
- Not covered: a message sent from the VM with `openclaw agent --agent <x>` (no hook fires; used only in tests, not in Slack).

## What changes on the VM if approved (step 3, a numbered handover, in a scratch gateway first)
1. The plugin folder under ~/loop1/state/extensions/send-log (manifest, index.js, tests in the repo), enabled by one config key; no conversation access (not needed). Hash lines in the health check, like the other two plugins.
2. A gateway restart (outside 03:30 to 05:10 AST and the 05:25 compaction).
3. COO read access to its own workspace only: tools.alsoAllow gets read and tools.fs.workspaceOnly stays true. The COO workspace holds its instruction files and the log, no chief's real state files. The health check line "coo has no file tools" changes to "coo read-only, workspace only".
4. COO instruction set v1.10.12: for a status question, read the last lines of the log, find the agent and run ID, then ask the agent as v1.10.11 does. Exact wording to be drafted after the scratch test and approved as its own APR.

## Options
- Option A (recommended): as above. The plugin writes a file in the COO workspace; the COO gets a workspace-only read tool.
- Option B: the plugin registers its own tool "send_log" that returns the last N log lines; the COO gets no file tool. Tighter, but the plugin is then no longer hook-only (it adds a tool) and has more code to prove.
- Option C: stop here and keep the wording rules only.

## Choice for the CEO inside option A
When a sessions_send fails, should the log keep the error text (80 characters, ids masked) or only "error"? The error text is the gateway's, not your content, and it would show what the "session-change error" really says (in the probe the CFO's reply call to the COO also returned an error although the content arrived). Recommended: keep the short masked text.

## Risks and how they are covered
- A slow or failing handler never blocks a send: only after_tool_call and message_received are used (observe-only). before_tool_call is NOT used (it fails closed and could block a send).
- A write failure is swallowed and counted; no log line then means unknown, never a wrong answer.
- A third plugin could slow gateway start: measured in the scratch gateway.
- Scratch test first: routing, run IDs, CFO logging, and the COO behaviour with the read tool (it must not start answering from files it should not read) compared with the same runs without the plugin. Unit suite, validator, health check, and the ceo-ledger and gate plugin hashes unchanged.
- Not yet known (to be tested in scratch before going live): whether the read tool changes other COO behaviour; hooks in Slack threads; lines lost during a gateway restart.
- Privacy: no content is logged; the COO sees no more than it sees in a reply today.

## Question
Reply with A, B or C, and for A the error-text choice (keep the short masked text, or only "error"), or tell me the changes. Approval would be recorded as the next APR in your words; the live install is a later numbered handover.
