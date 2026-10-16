# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-14 (APR-0036), P-15 (APR-0035), agent roster (APR-0038). The old P-03 blocker note is removed from the agent contract.

## P-08 - Haiku 5.5 API model ID (still open)
Needs: a probe result recorded in research/spikes/.

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file). Partial: SPK-05 (see file).

## P-13 - Who holds the Google Calendar access token
The token was created on the VM during the calendar setup (guides/calendar-gcalcli.md). The design assumes it lives only on the VM and is never in the repo.
Needs: your confirmation that this matches what you did.

## P-16 - Agent contract is generated from the roster
Proposed: design/roster.md is the only hand-written roster. scripts/verify/roster_to_agents.py writes contracts/agents.yaml, and nobody edits that file by hand. To add an agent: add its row to design/roster.md, run the script, add its folder under agent-files/, and record an APR entry.
Needs: yes or change.
