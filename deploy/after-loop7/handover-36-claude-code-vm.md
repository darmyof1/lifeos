# Handover 36 to Claude Code on the LifeOS VM (P-51 step 1: read-only check of what an OpenClaw plugin can see; scratch probe only)

Same Claude Code as handovers 1 to 35. The CEO said "lets go ahead and implement p-51" (APR-0135). That approves STEP 1 ONLY: find out, read-only and in a scratch gateway, whether a plugin can see agent-to-agent sends and what it is given. The design, the COO tool change and any live plugin need a separate APR after your report. Nothing live changes in this handover. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0135" near the end of decisions/APPROVALS.md; if not, stop and tell the CEO). Scratch copy `~/work36`. Return `~/handover/handover36.patch` (empty is fine; git add -A; git diff --cached --binary; no commit, no push), `~/handover/REPORT-36.md`, `~/handover-36.tar.gz` with ONLY those and ~/handover/h36/ (move old files in ~/handover aside, do not delete).

## What P-51 is for (context, do not build it)
A log written by code, not by agents, of agent-to-agent sends: time, run ID, from, to, a neutral one-line type, NO content and no amounts. A second line type could record that the CEO wrote to an agent in its own channel (the existing ceo-ledger plugin already does this for Slack with a text hash only; see deploy/loop3/ceo-plugin/design.md). The COO would later read the log through a read-only file tool limited to its workspace, so a status question becomes a lookup instead of a rule the agents may ignore.

## How to talk to the CEO
One step at a time; say which machine; exact text. Never ask for a secret; never print a token.

## IMPORTANT: real data
Real entries are in the CLO, CFO, CHO and CoS files and the TEST calendar; the repo is public. Never copy or print their content. This handover needs no real data: all probes use a scratch gateway with header-only synthetic files. No reset, no re-seed, no regression suite.

## Hard limits
1. NO live change of any kind: no live config, no crontab, no plugin installed or enabled on the live gateway, no agent file, no gateway stop or restart. The only live action is the pull and read-only reading of the OpenClaw docs and the installed plugin SDK files.
2. Scratch gateway as in handover 34: own state folder and port, no Slack, deleted afterwards; the scratch probe plugin is a throwaway in the scratch state folder only.
3. The probe plugin is observe-only and writes only: time, hook name, tool name, calling agent id, target session key shape (mask any id), and the LENGTH of the message. It never writes message text. Delete it afterwards.
4. No secrets, Slack IDs, tokens, session IDs, VM address or account names in ~/handover. Straight quotes only. Cited APR numbers must exist.
5. TIME WINDOW: no agent message or gateway start between 03:30 and 05:10 AST (the scratch gateway counts). Cost under 0.05 USD per run, 1 USD for the whole handover. Never reuse a session ID.
6. End state: live gateway PID, crontab, config, plugin hashes, agent files unchanged (hashes before and after); scratch folder deleted; health check unchanged (PASS 86, WARN 0 once the compaction run of 2026-11-21 has fixed it).

## Part 1. Read the documentation and SDK (read-only)
Report, with file names and short quotes (no more than a few lines each):
a. The list of plugin hook names in this OpenClaw version (2026.10.5) and which are Observe (return value ignored) and which can change behaviour.
b. Is there a hook that fires around tool calls (names like before_tool_call, after_tool_call or similar)? What does its event hold: tool name, parameters, the calling agent id, the session key, the run id? Does it fire for the tool sessions_send?
c. Is there any hook for agent-to-agent delivery, a sub-agent or a session message (inbound to the target agent)? What does it hold?
d. For message_received (used by ceo-ledger): does it fire for a message that arrives through sessions_send into the target's session, or only for channel messages?
e. Is there a hook for the final reply an agent sends to the CEO in Slack (outbound)? Not needed yet; list it.
f. Can a plugin write files outside its own folder (the log must go in the COO workspace later)? What path rules apply?

## Part 2. Scratch probe
Build the throwaway observe-only plugin per hard limit 3 for every hook found in Part 1 that could see sends (tool-call hook and any delivery hook). In the scratch gateway with the same five agents' allow-list as live (synthetic header-only state), send: (1) the COO a synthetic request that makes it call sessions_send to the CFO ("Tell the CFO to log a purchase: Test Item Probe, 5.00, on 2026-11-20. No reminder."); (2) a message straight to the CFO with `openclaw agent --agent cfo` (synthetic). Report per scenario which hooks fired, with the fields seen, and whether the target agent id and the run ID (coo-<date>-<time>) are visible without reading message text. If the probe can see the message text, say so, but do not write it down.

## Part 3. Findings and options (no change)
One page: (1) can code log agent-to-agent sends with from, to, time and run ID, yes/no, by which hook; (2) can it also log the CEO's direct messages in an agent's own channel; (3) what exactly would be needed: plugin shape (hook-only, observe-only), install steps, restart, hash lines in the health check; (4) the minimum COO tool change (read-only, workspace-only) and the config keys involved; (5) risks (slow handler, write failure; it must never block a send); (6) anything that could affect an already tested flow, with the test that would prove it unchanged. State plainly what is not yet known.

## Report (REPORT-36.md)
Per part: done, files, raw evidence in ~/handover/h36/ (doc quotes, probe plugin source, probe output with no message text, hash lists before and after, process counts, crontab diff). A plain statement that no token, ID, session key or real item is in the package. Secrets scan before packaging. `tar czf ~/handover-36.tar.gz -C ~ handover`.
