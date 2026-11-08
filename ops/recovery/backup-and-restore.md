# Backup and restore

Status: draft, Loop 4 (APR-0117), extends the handover 23 work (APR-0113). Scripts: scripts/ops/backup-weekly.sh, backup-push.sh, backup-run.sh, restore-backup.sh. Tests: tests/unit/test_backup_weekly.py, test_backup_push.py, test_restore_backup.py. Health line: "newest backup is younger than 8 days".

## How it works
1. `backup-weekly.sh --execute` copies the four agent workspaces (coo, cho, cos, cfo) and a token-free copy of the OpenClaw config (fields named like token, secret, password or apikey become "<redacted>") into a temp folder, writes FILES.sha256 (the manifest: one hash per file, not listing itself), makes a tar and encrypts it with gpg to the backup PUBLIC key. Result: `~/loop1/backups/lifeos-backup-YYYYMMDD-HHMM.tar.gpg` plus a `.sha256` line (folder mode 700, files mode 600). Two runs in the same minute get the seconds added, so nothing is overwritten. The last 4 stay on the VM (older date-only names from handover 23 still count).
2. `backup-push.sh --execute` copies the newest archive and its .sha256 line into a clone of the private backup repository (`~/loop1/backup-repo`), commits "backup NAME" and pushes. It refuses a file that is not gpg-encrypted data, a clone with uncommitted changes, a clone that diverged from the remote, and a failed push. It never forces a push. Settings (repository address, branch) live only in `~/loop1/backup.env` (mode 600); the address is never printed or logged.
3. `backup-run.sh --execute` runs both and writes one line to `~/loop1/backups/run.log` (time, archive name, bytes, push result; nothing secret). It exits non-zero if either step failed. Without `--execute` all three scripts are dry runs.
4. The weekly cron line calls `backup-run.sh`. The health check shows PASS when the newest archive is younger than 8 days, WARN when older, INFO when there is none yet.

## Where each key lives
| Key | Where | Who can use it |
|---|---|---|
| Backup PRIVATE key | The CEO's Mac and a copy in his password manager. Never on the VM, never in the chat, never in a repository | Only the CEO, with his passphrase |
| Backup PUBLIC key | `~/loop1/backup-public-key.asc` and the VM keyring (a public key is not secret) | The backup script can encrypt, nobody can decrypt with it |
| Deploy key (private half) | `~/loop1/backup-deploy-key` on the VM, mode 600 | Can write to the one backup repository, nothing else |
| Deploy key (public half) | In the backup repository's Settings, Deploy keys (write access) | n/a |
| Repository address | `~/loop1/backup.env` only | n/a |

## What is lost if the private key is lost
Every backup becomes unreadable, on the VM and in the repository, and nobody can recover them (including us). Keep the key export in the password manager and test a restore now and then. A new key protects only backups made after it is installed on the VM.

## Restore on a new machine (4 commands)
Needs the private key in the local gpg keyring (import it from the password manager: `gpg --import lifeos-backup-private.asc`, then delete that file). On a Mac: `brew install gnupg` if `gpg --version` says command not found.
1. `git clone <backup repository address> ~/lifeos-restore-test`
2. `git clone <the LifeOS repository address> ~/lifeos-ro` (this is where the restore script lives; skip if you already have it)
3. `cd ~/lifeos-ro && bash scripts/ops/restore-backup.sh --latest ~/lifeos-restore-test ~/lifeos-restore-out`
4. Read the last lines: `files: N`, `mismatches: 0`, `elapsed seconds: S`. gpg asks for the passphrase itself. The script exits non-zero unless there are 0 mismatches. Then follow ops/recovery/restore-drill.md to put the workspaces back (real tokens come from the password manager, they are not in the archive).
The script never restores into ~/loop1/workspaces or ~/loop1/state, and only into a folder that is new or empty. For one archive instead of the newest: `bash scripts/ops/restore-backup.sh ARCHIVE.tar.gpg TARGET_DIR`.
Delete the test folders afterwards (they hold decrypted agent files).

## What it does not back up
Session state, the plugin folder, the ledgers, the crontab, and every secret (gateway token, Slack and Google credentials). Those stay in the password manager or are rebuilt from the repository.

## Cron lines
- Drill (temporary, removed after it fired twice): `*/5 * * * * bash PATH/backup-run.sh --execute >> $HOME/loop1/backups/cron.log 2>&1 # lifeos-backup-drill`
- Weekly: `15 6 * * 0 bash $HOME/lifeos-ro/scripts/ops/backup-run.sh --execute >> $HOME/loop1/backups/cron.log 2>&1 # lifeos-backup-weekly` (Sunday 06:15 AST: after the 05:00 report, outside 03:30 to 05:10, away from the 5-minute calendar rhythm).
Until the repository copy of the scripts is pulled on the VM, the lines point at the scratch copy used for the drill and need one edit after the pull.
