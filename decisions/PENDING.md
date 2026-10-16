# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Resolved since the last version: P-12 (APR-0032), ADR-0003 acceptance (APR-0033).

## P-08 - Haiku 5.5 API model ID (still open)
Needs: a probe result recorded in research/spikes/.

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file). Partial: SPK-05 (see file).

## P-13 - Who holds the Google Calendar access token
The token was created on the VM during the calendar setup (guides/calendar-gcalcli.md). The design assumes it lives only on the VM and is never in the repo.
Needs: your confirmation that this matches what you did.

## P-14 - Triage latency budget
SPK-06 measured llama3.1:8b at 3.68 tokens per second, with about 4.1 seconds to first token. A routing JSON of roughly 60 tokens would take about 20 seconds. The design assumed under one second.
Options:
  a) Accept about 20 seconds for triage for now.
  b) Test smaller local models for triage in a new spike (SPK-08), then choose one. (recommended)
  c) Triage with deterministic rules first; use the local model only when the rules cannot decide.
Needs: a, b, or c.
