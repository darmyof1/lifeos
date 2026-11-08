# Loop 4 close record

Signed by APR-0118 (CEO, 2026-11-08 06:36: "close loop 4"). Loop 4 scope was APR-0117 (P-45), deploy/loop4/LOOP4-SCOPE.md. Synthetic data and the Google TEST calendar only, throughout.

## Pass criteria and result
| Criterion | Result | Evidence |
|---|---|---|
| The backup repository holds only ciphertext and checksum lines | Met: one .tar.gpg and one .sha256 line per backup; plaintext check over every blob, 0 hits | ops/loop4-h24-2026-11-08/d2-tree.txt, d2-plaintext-check.txt |
| Restore on another machine with the CEO's private key matches the manifest | Met: checksum OK, 259 files, 0 mismatches, 14 s (Intel Mac) | ops/handover-2026-11-08-claude-code-report-24.md (output pasted by the CEO) |
| Time to restore recorded | Met: 14 s restore, 1.7 s backup and push | same |
| Cron drill fired twice by cron and the temporary line is gone | Met: 05:55 and 06:00 on 2026-11-08, both pushes ok, crontab equals its starting copy | ops/loop4-h24-2026-11-08/d3-run.log, d3-cron.log, d3-commits.txt |
| Weekly line installed; crontab differs only by that line | Met: Sundays 06:15 AST, outside 03:30 to 05:10 | ops/loop4-h24-2026-11-08/crontab-diff-final.txt |
| Health check shows the backup line; no PASS drop; nothing else touched | Met from the repo copy: PASS 75, WARN 0, FAIL 0, INFO 3; no agent, config, plugin or gateway change | ops/loop4-h24-2026-11-08/health-final.txt |

## What Loop 4 delivered
scripts/ops/backup-weekly.sh (time in the archive name), backup-push.sh (never forced, refuses plaintext), backup-run.sh (cron wrapper with a run log), restore-backup.sh (macOS and Linux, verifies every file against the manifest, refuses live folders); a health-check line for backup age; ops/recovery/backup-and-restore.md; a private backup repository separate from the public repo; a write-only deploy key on the VM; the CEO's backup key (public half on the VM, private half only with the CEO).

## Incident, handled
The first backup key's private half was pasted into the Claude Code chat because a step told the CEO to print it. It was never written to a file and was discarded before any backup existed; a new key replaced it. Rule recorded: nobody asks the CEO to print or paste a private key; only public keys travel through chat.

## Carried over (not part of the pass)
- Replace the installed ~/loop1/health-check.py with the repo copy so the live health check shows the backup-age line (the installed copy is the older one, PASS 74).
- The CEO deletes the Mac's read-only deploy key lifeos-mac-restore in the backup repository's settings.
- The weekly line has not fired yet by its own schedule (the cron environment was proven by the drill); the first scheduled run is Sunday 2026-11-15 06:15 AST. The health check warns if the newest backup is 8 days old or more.
- If the private key is lost every backup is unreadable: the CEO keeps it in his password manager.

## Still parked (each needs its own APR)
Calendar privacy toggle (APR-0116, build in a later loop); wiring the privacy gate into the live agents; second-human delete-gate test; CFO send-list difference; scheduled compaction of the COO channel session; isolation; real data; the local-model box; the other chiefs. See deploy/loop3/LOOP3-CLOSE-RECORD.md.

## What keeps running
The gateway, the four agents, the calendar cron on the Google TEST calendar with the CEO ledger, the plugin, the 05:00 reset report and the weekly backup line. Nothing is stopped by this record.

## Rules that stay
No real data, no real calendar switch, no health data without a new loop and a new APR. The LifeOS repo stays public (APR-0114): no secrets, IDs, tokens, keys or addresses in it; run scripts/verify/history_scan.sh before pushing reports. Any change to an agent instruction needs the CEO's yes as a new APR.
