# Loop 4 scope: backup and recovery

Approved by APR-0117 (CEO, 2026-11-05). Synthetic data and the Google TEST calendar only, as in Loop 3. Nothing about the agents changes in this loop.

## Why this loop
Nothing off the VM holds the four agents' workspaces or the OpenClaw config (report 22). Before anything real enters the system, a lost VM must be recoverable. The scripts exist (handover 23); what is missing is a destination, a key, a schedule and a restore proof from another machine.

## What is built
1. A private GitHub repository for the encrypted backups (separate from the public LifeOS repo). Only ciphertext and checksum lines go in. The VM holds a deploy key that can write to that one repository only.
2. A backup key made by the CEO on his Mac. The VM holds the PUBLIC half only; the private half stays with the CEO (his Mac and a copy in his password manager). Without it a backup cannot be read, and nobody else can read it either.
3. `scripts/ops/backup-weekly.sh` (exists): file names get the time (YYYYMMDD-HHMM) so several runs in one day do not collide. New: `scripts/ops/backup-push.sh` (commit the new archive to the backup repository and push) and `scripts/ops/restore-backup.sh` (decrypt an archive, check every file against the manifest inside it, restore into a folder the CEO names, never into a live folder).
4. A health-check line: the newest backup is younger than 8 days (INFO if none yet).

## Controlled timing (no waiting a week)
The schedule is tested in minutes, not weeks:
1. Run the backup and push by hand once.
2. Install a TEMPORARY cron line that fires every 5 minutes (marked "lifeos-backup-drill"), let it fire twice by cron itself (this proves the cron environment: PATH, gpg, ssh key), then remove it. The crontab must equal its starting state afterwards.
3. The CEO restores from the backup repository on his Mac into a scratch folder and the restore script reports 0 mismatches.
4. Only then install the weekly line (Sundays, outside 03:30 to 05:10 AST) and verify it is present. It is not waited for.

## Pass criteria
- The backup repository holds only encrypted archives and checksum lines (no plaintext from the agent files; checked).
- Restore on a machine other than the VM, with the CEO's private key, matches every file in the manifest.
- Time to restore is recorded.
- The cron drill fired twice by cron and the temporary line is gone.
- The weekly line is installed; the crontab differs from its start only by that line.
- The health check shows the backup line; PASS count does not drop; the gateway and the other cron lines are untouched; no agent instruction, config or plugin changed.

## Not in this loop
Wiring the privacy gate, the toggle for calendar privacy, the real calendar, real data, isolation, the CFO send-list difference, the COO session compaction, more chiefs, the local-model box. Each needs its own approval.

## Carried requirement (from the CEO, 2026-11-05; built in a later loop)
Calendar privacy must be flexible, not "never": a setting in a YAML file (busy or full) that the CEO can flip, and the job applies to what Google shows. In full mode Google holds the real titles and the CEO accepts that. See APR-0116.
