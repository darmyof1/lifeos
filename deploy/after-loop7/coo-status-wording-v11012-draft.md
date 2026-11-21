# COO status questions, third wording: read the send log first (DRAFT, waiting for the CEO's approval; nothing is approved here)

Why: the send-log plugin is live (APR-0136, handover 37) and writes a line for each message between agents and for each message the CEO sends in an agent's own Slack channel. Lines hold times, agent names, run IDs and the words send or ceo-message, never what was said. With a read tool limited to its own workspace, the COO can check the log before asking an agent, so it no longer has to guess from memory what happened and when. This wording replaces the v1.10.11 status rule in place (the same rule slot, no second rule).

Facts from handover 37 that shape the wording:
- In the scratch test the COO could not find the log by itself (about 50 guessed file names), so the wording gives the exact file name pattern.
- A line from an agent back to the COO that says error with the text "changed while starting work" still means the message arrived (the session-change error; content always arrived in the tests). The COO must not report it as a failure.
- The log has no content. To say what the item was, the COO still asks the agent to read its own state files (the v1.10.11 mechanism).
- The read tool is limited to the COO's own workspace. Reads outside it and any write were refused in the scratch test.

## Proposed wording (replaces the v1.10.11 "Status questions" rule, the last rule of "Loop 1 rules (all agents)" in agent-files/executive/coo/AGENTS.md)
"- Status questions (instruction set v1.10.12): you cannot see what the CEO says to another agent directly, and you may not remember what other agents routed through you in another session. When the CEO asks what he last told an agent, what an agent did, or whether something was logged, do not answer from your own memory. First read the file send-log-YYYY-MM.md for the current month in your state folder (if the month is new and it has no line for that agent, read last month's file) and find the newest lines for that agent. Each line has a time, the words send or ceo-message, the agent names and a run ID; none of them holds what was said. A send line that says error with the text 'changed while starting work' still means the message arrived. Then send that agent one question: read the last entries in your own state files and tell me what was last logged for the CEO, with the date, in one or two sentences. Add the time and run ID from the newest log line when there is one. Do not answer from conversation memory. Relay its answer, naming the agent, the date and the run ID. If the log has no line for that agent, say so, and still ask the agent. If the agent finds nothing, say so. Never write a file path or a file name in your answer; say which agent holds the record and that the CEO can ask it directly."

## What this does and does not do
- Does: the COO checks a code-written record of when and whether before it asks, and it can say that the CEO wrote in an agent's channel at a given time, or that a send went out under a given run ID.
- Does not: say what was said (the log has no content; the agent still reads its own files). It is still a behaviour rule: an agent can ignore it. The log lines for an item typed in an agent's own channel show only the time and a hash, so what the item was still comes from that agent.
- Live changes if approved (a numbered handover, next): the COO instruction file (v1.10.12, replacing the v1.10.11 rule in place), the COO read tool limited to its own workspace (tools.alsoAllow read, tools.fs.workspaceOnly true), one gateway restart, and the health check lines (the COO tool line changes from "no file tools" to "read-only, own workspace"). No other agent, no crontab, no plugin change. Synthetic tests only, with the same real-data rules as handovers 33 to 37.

## Question
Reply "approved as written", or tell me the changes. Approval would be recorded as the next APR in your words, with a numbered handover to follow.
