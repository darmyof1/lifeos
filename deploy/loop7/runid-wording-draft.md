# Loop 7: the COO builds its own run ID (DRAFT, waiting for the CEO's approval; nothing is approved here)

Why: on 2026-11-14 the COO used a stray word the CEO typed at 05:50 AM as the run ID and event ID of a Show Four log line, and at 10:28 AM it used "MPBLACK26" the same way (event ID MPBLACK26-clo-02). The routing was right both times. The COO instructions have no rule for making a run ID, so it reuses text it has seen. The state files are append-only, so the two lines stay.

## COO: instruction set v1.10.9 (agent-files/executive/coo/AGENTS.md)

Add one rule at the end of "Loop 1 rules (all agents)":

    - Run IDs (instruction set v1.10.9): when the CEO's message does not state a run ID, make one yourself in this form: coo-<YYYYMMDD>-<HHMM>, the date and the time in AST when you received the message, for example coo-20261114-1028. A message states a run ID only when it says "run ID" followed by the ID. Never use a word, name or code from the CEO's messages, from other channels or from your history as a run ID or as part of one. Use the same run ID for every agent you message about that request, and name it in your answer.

## What stays the same
- No change to the CLO, CoS, CHO or CFO files, the config, the crontab or the plugins. One file changes on the VM: the COO instruction file (gateway stopped, backup, commit in the workspace, as handover 31 did).
- The two odd lines in the CLO state file are not edited (append-only). A correction line is not part of this change.

## What handover 32 would check (not a decision, for your information)
- In a scratch copy first: that the COO can see the correct date and time. If it cannot, the handover stops and reports before any live change, and I come back with another wording.
- Live proof with new run IDs and synthetic names: a lifestyle request with no run ID gets coo-<date>-<time>; a message that says "run ID abc-1" keeps abc-1; a stray word typed before the request is not used; the CLO event ID becomes <run ID>-clo-01; routing and the earlier checks stay as in handover 31.

## Questions
1. Wording: reply "approved as written" or tell me the changes.
2. Time zone in the ID: AST (as written), or UTC?

Approval would be recorded as the next APR in your words.
