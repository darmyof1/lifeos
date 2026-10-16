# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-14 (APR-0036), P-15 (APR-0035), agent roster (APR-0038), P-16 (APR-0039), P-08 (APR-0040).

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file), SPK-09 (see file). Partial: SPK-05 (see file).
Several need the OpenClaw runtime running on the VM. Run them when the system is up.

## P-13 - Who holds the Google Calendar access token (evidence in, awaiting your yes)
VM evidence: the token is at ~/.local/share/gcalcli/oauth, owner ubuntu. Mode was 664 and was changed to 600 (chmod), confirmed by stat.
Needs: yes or change.
