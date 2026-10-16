# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-14 (APR-0036), P-15 (APR-0035), agent roster (APR-0038), P-16 (APR-0039).

## P-08 - Haiku 5.5 API model ID (probed, awaiting your yes)
SPK-09: the API returned HTTP 200 with claude-haiku-5-5, and the CLI works with that model. Needs: yes to close.

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file), SPK-09 (see file). Partial: SPK-05 (see file).
Several need the OpenClaw runtime running on the VM. Run them when the system is up.

## P-13 - Who holds the Google Calendar access token (path corrected, not yet confirmed)
The token lives on the VM at ~/.local/share/gcalcli/oauth (guides/calendar-gcalcli.md, "Where the token lives"). The earlier guide path was wrong. A test host showed no file at the old path.
Needs: the check in that guide section on the VM, then yes or change.
