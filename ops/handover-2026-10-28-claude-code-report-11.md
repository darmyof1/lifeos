# REPORT 11 - delete gate in code (APR-0100)

Pulled first: HEAD 6804ad3 "APR-0100 ..." with the handover 10 commit below it. Work done 18:26 to about 18:50 AST, outside the 03:30 to 05:10 window. No agent message, compaction or gateway restart. No live file, config, binding or cron changed; ~/lifeos-ro untouched (git status clean).

## Task 1 answer: can an agent-proof approval record be made on this VM?
Yes for the record, and the source exists today. Not yet for the ledger writer: that is new code and needs a CEO decision.

1. The inbound record exists outside the agent workspaces. Each agent's transcript is in its own SQLite file `~/loop1/state/agents/<id>/agent/openclaw-agent.sqlite`, table `transcript_events` (column `event_json`; also `trajectory_runtime_events`). Each user message holds role, timestamp, full content, an idempotency key and a gateway-written `__openclaw` block:
   - Slack message: `__openclaw.senderId`, `senderName`, `senderIdentity` {type observation, pluginId slack, accountId, senderKind}, `transport` {channel slack, conversationRef, messageId}, `senderIsOwner`. Sample (IDs removed): `{"senderIsOwner": false, "senderId": "<ID>", "senderIdentity": {"type": "observation", "pluginId": "slack", "accountId": "default", "senderKind": "unknown"}, "transport": {"channel": "slack", "messageId": "<ts>"}}`.
   - CLI message (`openclaw agent -m`): `__openclaw` = `{"senderIsOwner": true}` only. No sender ID, no channel.
   - Message from another agent: carries a `provenance` field and the text starts "[Inter-session message] sourceSession=agent:cho:main sourceChannel=webchat sourceTool=sessions_send isUser=false". The gateway writes this, not the agent.
   Also: `channel_ingress_events` in `~/loop1/state/state/openclaw.sqlite` (channel, received_at; the payload is cleared to null after completion, so it is not usable as proof), and `audit_events` (actor, session, tool, channel; hashed refs, no text).
2. Can an agent write it? Not with its tools. The agents have profile "messaging" plus read, write and edit, with `fs.workspaceOnly: true`, and no exec tool. Those SQLite files and `~/loop1/` are outside every workspace. I read the policy in `~/loop1/state/openclaw.json` and tried nothing destructive. Limit: the files are owned by the same OS user as the gateway, so this protection is the tool policy, not file permissions. If an agent were ever given exec, it could write them.
3. Hook points for a writer:
   - Plugin hook `message_received` (docs/plugins/hooks/messages.md): observe-only, gives content, senderId, messageId, channel and run/session correlation for every inbound message. A small plugin could append a ledger line. This is a new plugin loaded by the gateway, so it needs a gateway restart and the CEO's decision. Its Slack sender is the CEO only if the CEO's Slack user ID is known to the plugin (kept in a local file, never in the repo).
   - The `hooks.*` HTTP ingress and internal hooks (`HOOK.md`) are not suited: hook tokens give no sender identity.
   - Today `commands.ownerAllowFrom` is not set, so `senderIsOwner` is false for the CEO's Slack messages. Setting it is a config change (CEO decision) and would let the ledger rule be "senderIsOwner true".
   - CLI route: there is no sender identity, only `senderIsOwner: true`. For scenario runs the runner (code, not an agent) writes the ledger line itself right after it sends the approval message, with the run ID and event ID it knows.
4. Nearest option without a plugin: the push job (or a small separate script) reads the COO's transcript database read-only and accepts a delete only if it finds a user message with a gateway sender (Slack message from the CEO's user ID, or CLI with senderIsOwner true, and no `provenance` field) whose text quotes the run ID or event ID, after the pending line. Cost: no restart, no gateway change, about one script plus tests; risk: it depends on OpenClaw's internal table layout (changes between versions) and reads a live WAL database.
5. Problem to decide: the CEO's approval text does not always carry the event ID (the scenario D2 message is "Yes, I approve deleting the 2026-10-30 workout"). The v1.10 COO layout asks the CEO to cite the event ID. A live writer must either require that or match on the pending line another way. The ledger check matches on run ID and event ID.
6. The journal has no time column. "Before the deleted line's push time" therefore means "not later than the job's run time". The check cannot prove the entry came after the pending line; it proves a CEO entry for that run and event exists. A writer that logs only after the pending line closes this.

Needed from the CEO: (a) choose plugin hook, transcript reader, or runner-written ledger for scenarios only; (b) if a plugin, allow a gateway restart and set the CEO's Slack ID in a local file; (c) decide whether to set `commands.ownerAllowFrom`; (d) decide whether the cron then gets `--require-ceo-ledger`. I did not build a writer.

## Task 2: the reader, switched off
Files in `~/handover/delete-gate/`: `gcal_sync.ceo-ledger.patch`, `test_gcal_sync.ceo-ledger.patch`, `gcal_sync.py.new`, `test_gcal_sync.py.new`, `README.md`.
- New option `--require-ceo-ledger PATH`, default none. With it, a `deleted` line still needs the existing `--allow-deletes` and pending line, and then also a ledger entry (one JSON object per line: time, run, event, channel, sender, text_sha256) with sender "CEO", the same run and event, and a time not later than the job run. Otherwise the job prints "skip   <name>: no CEO approval record for event <id> (APR-0100)", counts it as skipped and deletes nothing. A missing file, a broken line or an unparsable time approves nothing.
- The spec said the job "writes a skip line". The existing skip lines are printed by the job, not written to the journal (the journal is not the job's to write skips into), so I followed that. Tell me if you want a journal line.
- Tests: 7 new tests plus the 5 DeleteTests inherited by the new class, which run without the flag and show nothing changes. Cases: no entry (no delete), no ledger file, matching entry (deletes), other run, other event, sender not CEO, future time, bad time, broken line, pending line still required. 127 gcal unit tests OK, 67 in test_gcal_sync.py.
- Both patches apply cleanly to the repo copies at HEAD 6804ad3 and give files identical to the `.new` files (cmp). The cron is not changed.

## Task 3
`~/handover/delete-gate/rule-A-proposal.md`: one rule for the CoS, one for the COO, one line for the CHO and CFO, with the overlapping existing rules named. Not applied.

## Failures
None in the build. One note: the first test run needed `test_gcal_scripts.py` copied next to the tests (it holds the shared fake service).

## Installed or updated
Nothing installed. All outputs are files in `~/handover/`.
