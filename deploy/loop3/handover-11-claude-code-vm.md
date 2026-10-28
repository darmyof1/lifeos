# Handover 11 to Claude Code on the LifeOS VM (delete gate in code, APR-0100)

Same Claude Code as handovers 1 to 10. The CEO approved option C (APR-0100): an instruction rule (A) and a code check (B), code first. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0100 ..." at the top, with the handover 10 commit below it). If it is missing, stop and tell the CEO.

## Why
Regression runs loop3-cmp-001-04 and loop3-cmp-003-04: a delete asked for by the CHO ended as a deleted line and a deleted Google event with no CEO message. In 003-04 the COO told the CoS "the COO relayed your approval" and the CoS wrote the deleted line "requested by CEO". The instructions already forbid this (v1.10 to v1.10.3), so the instructions alone are not reliable. The push job must refuse a delete unless it can see proof of a CEO approval that no agent can write. Agents can write only inside their own workspaces, so the proof has to live outside them.

## Read first
APR-0044, APR-0093, APR-0099, APR-0100; scripts/gcal/gcal_sync.py (delete_was_requested, the `deleted` branch); deploy/loop1/ scripts for how the Slack and CLI messages reach the agents; ops/structure-test/comparison/loop3-cmp-003/loop3-cmp-003-04.txt.

## Hard limits (as before)
1. No change to any agent file, config, binding or cron in this handover. No gateway restart. Task 3 only writes a proposal.
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, calendar ID or VM address in ~/handover/.
3. TIME WINDOW: no agent message, `sessions compact` or gateway restart between 03:30 and 05:10 AST; finish by 02:30 AST.
4. Journals and git history append-only. Cost under 0.05 USD per run, 1 USD per night.

## Task 1. Read-only: where can an agent-proof CEO approval record come from?
Find out, and report with evidence (file paths, field names, one sanitized sample line each, no IDs):
1. Does OpenClaw keep an inbound message record outside the agent workspaces (session transcripts, trajectory exports, gateway logs) that holds, for each message: the sender identity as the channel reports it (not typed by an agent), the channel, the time, the full text? Can an agent write or edit that file with its tool policy (files limited to the workspace)? Check by reading the tool policy and trying nothing destructive.
2. Is there a gateway hook, plugin point or webhook where a small script could append a line (time, channel, sender role CEO, message text hash, quoted text) to a ledger file outside the workspaces, for every message from the CEO's Slack user and the CEO's CLI messages? If the CLI route (`openclaw agent -m`) has no sender identity, say how the scenario runner could write the line instead (the runner is code, not an agent).
3. If neither exists, list the nearest options with cost and risk (for example the push job reading the session export for the CoS and checking that the quoted CEO words appear in a message with a CEO sender).
Do not build the writer in this handover. Stop at the report if the answer needs a CEO decision.

## Task 2. Build the reader, switched off
In scripts/gcal/gcal_sync.py add an optional check, off by default: with `--require-ceo-ledger PATH`, a `deleted` line is run only if the ledger holds an entry whose run ID and event ID match the pending line and whose time is before the deleted line's push time; otherwise the job writes a skip line "no CEO approval record for event <id>" and does not delete. Ledger format: one JSON object per line: time, run, event, channel, sender "CEO", text_sha256. Unit tests in tests/unit/test_gcal_sync.py: with the flag and no ledger entry no delete; with a matching entry the delete runs; with an entry of another run or event no delete; without the flag nothing changes. Do not switch it on in the cron. Put the change in the repo copy only (the CEO runs fix scripts; do not edit ~/lifeos-ro): write the patch as a unified diff and the tests in ~/handover/delete-gate/ for Claude (me) to turn into a fix script.

## Task 3. Draft rule A, do not apply it
Write ~/handover/delete-gate/rule-A-proposal.md: one short rule for the COO, one for the CoS (and one line for the CHO and CFO) that says: a deleted line "requested by CEO" is written only when the message the agent itself received came from the CEO (not relayed by a chief or the COO), quoting the delete request; a chief's request, or a relayed approval, gives only a pending line requested by that chief; the COO never writes that the CEO approved unless the CEO's own message in this session says so. Say which of the existing rules it overlaps. No change to any live file.

## Report (~/handover/REPORT-11.md)
Task 1 answer first, in plain words: can an agent-proof approval record be made on this VM, how, and what is needed from the CEO. Then Task 2 and 3 files. Failures as they happened. Package with `tar czf ~/handover-11.tar.gz -C ~ handover` after a secrets check; confirm anything installed by checksum.
