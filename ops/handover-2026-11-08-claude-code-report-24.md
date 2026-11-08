# REPORT 24: Loop 4 backup and recovery (APR-0117)

Status: DONE. Part 1 to 4 complete, restore proof passed, weekly line installed. Nothing blocked.

## Part 1 (repo build, scratch copy ~/work24, then applied by the planning chat as commit a267606)
- backup-weekly.sh: names `lifeos-backup-YYYYMMDD-HHMM.tar.gpg` (same-minute second run adds seconds); keep-last-4 still works with old date-only names.
- New: backup-push.sh (never forces, refuses plaintext, dirty or diverged clone, undoes its commit on a failed push), backup-run.sh (cron wrapper, one line per run in ~/loop1/backups/run.log), restore-backup.sh (macOS and Linux, verifies checksum line, passphrase asked by gpg only, counts missing, different and extra files as mismatches).
- health-check.py: new line "newest backup is younger than 8 days" (INFO none, PASS under 8 days, WARN 8 days or older or future date).
- Docs: ops/recovery/backup-and-restore.md (renamed from backup-weekly.md), pointer in restore-drill.md; registry updated.
- Tests: full unit suite 422 OK (new: 17 push/run, 12 restore, 4 added weekly, 6 health line). Validator: 0 blocking, 1 warning. Evidence: h24/unit-suite.txt, h24/validator.txt.
- Repo scripts after pull are byte for byte the tested ~/work24 scripts (cmp).

## Part 2 (setup with the CEO)
- S1 key: the first backup key was EXPOSED. My step told the CEO to print the private key, and he pasted it in this chat. It was never saved to any file (grep checked). The key was discarded before any backup existed (public key and fingerprint file removed from the VM; deleted on the Mac). The old private block appears in the chat transcript only. A new key (fingerprint ends ...043175EF) was made; its private half went to the CEO's password manager through the clipboard only. VM keyring: public key only, 0 secret keys.
- S2: empty private repo `lifeos-backup` created; VM deploy key (ed25519, write access) added; address only in ~/loop1/backup.env (mode 600).
- S3: no separate first push needed; backup-push starts the empty branch itself.

## Part 3 (drill)
- D1: crontab saved (26 lines): ~/loop1/crontab.pre-loop4-20261108-0550.
- D2: dry runs OK (backup-push and the run wrapper's dry run exit 1 when no archive exists yet; expected on first use). One real run: 05:50:17, 1.7 s, 174,799 bytes, 259 files. Repo: 1 commit, only .tar.gpg and .sha256. Plaintext check over all blobs, 5 strings from AGENTS.md headings: 0 hits. Evidence: d2-run.log, d2-commits.txt, d2-tree.txt, d2-plaintext-check.txt.
- D3: temporary line fired by cron at 05:55:02 and 06:00:03 (commits 7fe9a4f 05:55:01, 5ebb9c6 06:00:02), both push=ok; cron.log 364 bytes, no errors. Line removed; crontab diff vs D1 empty. Evidence: d3-run.log, d3-cron.log, d3-commits.txt, d3-tree.txt, crontab-after-d3.txt. The drill used the ~/work24 path.
- D4 (CEO, Mac, after pushed commit a267606): Mac could not read the private repo over SSH, so a read-only deploy key was made on the Mac and later deleted. Restore output pasted by CEO: `archive checksum line: OK`, `files: 259`, `mismatches: 0`, `elapsed seconds: 14`. PASS. Mac test folders and Mac key deleted.
- D5: weekly line `15 6 * * 0 bash /home/ubuntu/lifeos-ro/scripts/ops/backup-run.sh --execute >> ...cron.log 2>&1 # lifeos-backup-weekly` (Sunday 06:15 AST, outside 03:30 to 05:10). Uses the ~/lifeos-ro repo path. Diff vs D1: only that line (crontab-diff-final.txt). Not waited for.
- D6: patched health-check from the repo: PASS 75, WARN 0, FAIL 0, INFO 3 (health-final.txt). The older copy ~/loop1/health-check.py (not replaced; outside the allowed list) still gives PASS 74.

## Times
backup 1.7 s total (backup plus push), restore 14 s on an Intel Mac.

## Notes
- run.log timestamps show -0400 (AST).
- Pruning of old archives sorts by name; push picks newest by file time.
- Leftover: delete the Mac's deploy key `lifeos-mac-restore` in the GitHub repo settings (CEO step, pending at report time).

## End state
Gateway: one process, not restarted. Other cron lines unchanged. No agent, OpenClaw config or plugin change. No backup activity inside 03:30 to 05:10. No model calls.
