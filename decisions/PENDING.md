# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Resolved since the last version: P-14 is still open; the naming mandate is approved (APR-0034).

## P-08 - Haiku 5.5 API model ID (still open)
Needs: a probe result recorded in research/spikes/.

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file). Partial: SPK-05 (see file).

## P-13 - Who holds the Google Calendar access token
The token was created on the VM during the calendar setup (guides/calendar-gcalcli.md). The design assumes it lives only on the VM and is never in the repo.
Needs: your confirmation that this matches what you did.

## P-14 - How long the triage step may take
What "triage" means: the first step. When you send a request, a small local model reads it and decides what kind of request it is (health, finance, calendar, and so on) and how private it is. Everything after that depends on this answer.
What we measured (SPK-06): the local model produces about 3.7 tokens per second on this VM. A token is roughly three-quarters of a word. The triage answer is about 60 tokens, so it takes about 20 seconds. The design assumed under one second.
Options:
  a) Accept about 20 seconds for triage for now.
  b) Test smaller local models for triage in a new spike (SPK-08), then choose one. (recommended)
  c) Triage with plain rules first (keywords such as "gym", "budget", "meeting"); use the local model only when the rules cannot decide.
Needs: a, b, or c.

## P-15 - Details of the naming standard (APR-0034)
Please confirm each point. A "yes" approves it; a change replaces it.
  1. Date order: MMDDYYYY, as the example suggests (10202026 = October 20, 2026). Confirm, or give the order you want.
  2. ID scope: the four digits restart every day (0001 for each date), so the name is unique when combined with the date. Confirm, or choose one counter for all events.
  3. Domain codes: CHO, CSP, CDO, CFO, CFA, CLO, CSO, CCO for domain events. For events that belong to no domain, use COO (operations) or COS (staff). Confirm, or change.
Needs: yes or change for each of 1, 2, and 3.
