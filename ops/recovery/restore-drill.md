# Restore drill

Status: draft, drilled once on 2026-11-01 with a copy of the four agent workspaces and a token-free copy of the config (APR-0112). Based on SPK-07 (research/spikes/SPK-07-gpg-restore-drill.md): an encrypted archive restores from its passphrase alone, and a wrong passphrase fails with no output.

Backup and restore of the encrypted archives (Loop 4, APR-0117): see ops/recovery/backup-and-restore.md. Its `restore-backup.sh` checks every file against the manifest before you put anything back.

## What is backed up today (facts from the VM, read-only look)
| Thing | Backed up? | How |
|---|---|---|
| The repo (design, scripts, tests, deploy scripts) | Yes | GitHub; the VM clone is read-only; the CEO pushes |
| OpenClaw config (openclaw.json) | Partly | OpenClaw keeps `.bak` copies in the state folder (the last five edits) plus a few named copies from our upgrades (for example the one before the ledger plugin). They sit on the same disk |
| The four agent workspaces (coo, cho, cos, cfo; git repos holding AGENTS.md and state/) | No off-VM backup | Local git history only, no remote (0 remotes in each) |
| The rest of the state folder (~/loop1/state: sessions, agent databases, the installed plugin copy, caches; 329 MB) | No | Nothing copies it |
| The crontab | Partly | Named copies made by our handovers (for example the one before the ledger option) and the kill switch copy; no routine copy |
| The CEO ledger and the gcal-sync state | No | Only on the VM disk |
| The evidence folders and handover tarballs (~/loop1/evidence, ~/handover-N.tar.gz) | On the same disk only | Tarballs are delivered to the CEO, which is the only off-VM copy of those reports |
| The whole VM | Not seen from the VM | An Oracle boot-volume backup may exist; this was not checked and is unknown |
The repo has backup scripts planned (scripts/ops/backup-daily.sh, backup-hourly.sh, archive-pack.sh) but they are empty files: no backup job exists.
Plainly: if the VM disk is lost, the repo survives, the workspaces' git history and the session state do not. There is no automatic encrypted off-VM backup of ~/loop1/state and the workspaces. SPK-07 proved the mechanism; it was not turned into a routine.

## The drill (synthetic copy, nothing live touched)
1. Copy the four workspaces to a temporary folder (259 files including the .git folders).
2. Copy openclaw.json with every field whose name contains token, secret, password or apikey replaced by "<redacted>" (one field). The Slack tokens are environment references and are not in the file.
3. Make a tar.gz and encrypt it with `gpg --symmetric --cipher-algo AES256` using a throwaway passphrase made for the drill (24 random characters; never written to a file).
4. Try a wrong passphrase: refused (exit 2), no output file.
5. Decrypt with the right passphrase into a new folder and extract.
6. Compare sha256 of every file before and after.
7. Delete the temporary folder and the archive.

## Result
| Item | Value |
|---|---|
| Files | 259 |
| Compare | all 259 sha256 equal |
| Archive size | 158,913 bytes |
| Times | copy and redact 0.1 s, encrypt 1.1 s, decrypt and extract 0.4 s, total 1.5 s |
| Wrong passphrase | refused, no output |
| Cleanup | temporary folder and archive deleted; the passphrase was only in a shell variable |
This covers the config and the workspaces only. The session state and the plugin folder were not in the drill; the full state is 329 MB and was not timed.

## Routine proposed (not installed; the CEO decides)
Weekly: copy the workspaces and the token-free config, encrypt with the archive public key (SPK-07 Part B: the VM encrypts but cannot decrypt; only the CEO's key restores), keep four copies off the VM. Quarterly: repeat this drill with the CEO's key. The proposal is in the Handover 22 report with the seven items.

## Restore, in short (if the VM state is lost)
1. New VM; install the pinned OpenClaw (2026.10.5) and clone the repo.
2. Decrypt the latest archive with the CEO's key; extract the workspaces and the token-free config.
3. Put the secrets back from the password manager (gateway token, Slack tokens, Google client secret, OpenAI key). They are not in the archive.
4. Rebuild the plugin and cron lines from the repo (deploy/loop3/ceo-plugin, the crontab backups), start the gateway once, run the health check.
