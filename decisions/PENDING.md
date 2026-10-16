# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-08 (APR-0040), P-13 (APR-0041), P-18 (APR-0042).

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file), SPK-09 (see file). Partial: SPK-05 (see file).
Several need the OpenClaw runtime running on the VM. Run them when the system is up.

## P-17 - Dashboard or website for the owner (future)
Owner: CMO (roster: "produces the weekly life dashboard"). Proposed, not yet approved: the CKO supplies the memory data behind it.
Decision made: the owner must be able to reach it from the internet. It will be heavily protected. How it is protected is decided later.
Not now: no design until the agent loop is proven.
Needs: nothing today. A design item is opened when the loop is proven.

## P-19 - Approve the scenario catalogue and decide the open scenarios
Catalogue: design/scenarios.md (status: draft). 12 rows are marked "Decision needed" and have no approved behavior yet. S-12 is now decided by ADR-0002 (APR-0042).
The catalogue becomes approved only after each of those 12 rows is answered: a yes to the proposed behavior, or a changed answer.
Needs: an answer for each of S-01, S-03, S-05, S-06, S-07, S-08, S-14, S-15, S-16, S-17, S-19, S-20. Decided rows do not need an answer. S-21 waits on P-17.
