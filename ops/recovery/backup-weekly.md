# Weekly encrypted backup

Status: draft, written 2026-11-04 under APR-0113. Script: scripts/ops/backup-weekly.sh. Tests: tests/unit/test_backup_weekly.py. Not scheduled yet (no cron line installed). The off-VM destination is not decided (see the Handover 23 report).

## What it does
1. Refuses to run if the public key fingerprint file (~/loop1/backup-key-fingerprint) is missing, if the key is not in the keyring, or if the matching SECRET key is on this machine. The VM holds a public key only; no private key and no passphrase.
2. Copies the four agent workspaces (coo, cho, cos, cfo; they are git repos) and a copy of the OpenClaw config in which every field named like token, secret, password or apikey is replaced by "<redacted>" into a temp folder (mode 700).
3. Writes a list of file hashes (FILES.sha256) into the archive, makes a tar, and encrypts it with gpg to the public key.
4. Writes ~/loop1/backups/lifeos-backup-YYYYMMDD.tar.gpg and a .sha256 line (folder mode 700, files mode 600).
5. Keeps the last 4 backups (it removes only its own older lifeos-backup-*.tar.gpg and .sha256 files), deletes its temp folder, prints no secrets.
Default is a dry run. `--execute` acts. If ~/loop1/backup-public-key.asc exists it is imported first (public part only).

## What it does not do
It does not copy anything off the VM, install a cron line, or back up the session state, the plugin folder, the ledgers or secrets (the secrets stay in the password manager). The gateway token and the Slack and Google credentials are not in the archive.

## Cron line (proposed, NOT installed)
`30 6 * * 0 bash $HOME/lifeos-ro/scripts/ops/backup-weekly.sh --execute >> $HOME/loop1/backups/backup.log 2>&1`
Sunday 06:30 AST: after the 05:00 reset report, outside the 03:30 to 05:10 window, and not on the calendar job's 5-minute rhythm. Installing it is a crontab change and needs the CEO's yes.

## Restore (on the CEO's machine, with the private key)
1. Copy lifeos-backup-YYYYMMDD.tar.gpg and its .sha256 line; check `sha256sum -c`.
2. `gpg -d -o backup.tar lifeos-backup-YYYYMMDD.tar.gpg` (asks for the key's passphrase on the CEO's machine).
3. `mkdir restored && tar xf backup.tar -C restored && (cd restored && sha256sum -c FILES.sha256)` - every file must say OK except FILES.sha256 itself, which is not listed.
4. Put the workspaces back under ~/loop1/workspaces, the config under the state folder (with real tokens from the password manager), then follow ops/recovery/restore-drill.md.
