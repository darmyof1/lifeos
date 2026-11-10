# REPORT 26 - Loop 6 (APR-0121): COO morning compaction and health check. Item 1 skipped by the CEO's decision.

Date: 2026-11-09 (AST). Machine: the Loop 1 to 4 VM. Synthetic data and the Google TEST calendar only. The real calendar was not touched.

## Summary
| Item | Result |
|---|---|
| 1. CFO send list to COO only | SKIPPED by the CEO (option A). The CFO keeps ["coo","cos"]. Why below. |
| 2. COO morning compaction | DONE. Script, 16 tests, manual live run, cron proof, real 05:25 line installed. |
| 3. Health check | DONE. One new line; the CFO send-list line already expects ["coo","cos"]. Installed copy replaced. |

Tests: full unit suite 484 OK (was 457; +16 compaction, +11 health lines). Validator: 0 blocking, 1 warning (the old count of planned/draft files). Health check now: PASS 77, WARN 0, FAIL 0, INFO 5.

## Why Item 1 was skipped (decision of the CEO in this chat)
The handover said the CFO's written instructions allow it to message only the COO. They do not. CFO instruction v1.10 (APR-0092) says calendar entries go straight to the CoS (sessions_send to the CoS, privacy=high in the message), and its privacy rule (APR-0086) needs the same handoff. Handover 4 had widened the live list from ["coo"] to ["coo","cos"] for exactly that (its report holds the diff). The existing CFO scenario ("CFO entry") has the COO route the request to the CFO, and the CFO then messages the CoS. With ["coo"] that handoff would be refused and the scenario would fail. The note saying "COO only" was wrong. I stopped before any change, asked, and the CEO chose to skip Item 1.
- Config: not changed. `cmp` of the live config against the backup `~/loop1/state/openclaw.json.pre-loop6-cfo` (made before any work): byte equal. No config diff exists to show.
- The existing health line "cfo send list" already expects ["coo","cos"] (PASS now). I did not add a second line.
- Rollback: none needed. The backup file can be deleted.

## Item 2: COO morning compaction
Files (in the patch): `scripts/ops/coo-compact.sh` (new, executable), `tests/unit/test_coo_compact.py` (16 tests), `ops/coo-compaction.md` (what, rules, cron line, rollback).

How it works (see the script header and the ops note):
- Dry run by default; `--execute` acts. Same command as handover 23: `openclaw sessions compact <COO Slack channel session> --agent coo --max-lines 1 --token ...`. The session key is found at run time (the one key starting with `agent:coo:slack:channel:`), so no Slack ID is stored in the repo.
- Refuses 03:30 to 05:10 AST (exit 2). Skips and logs when the channel session had a message in the last 10 minutes, or when a CEO request is waiting (the newest journal line of an event is `requested` or `delete-pending-approval`), or when the journal cannot be read.
- One log line per run in `~/loop1/state/coo-compact.log`: time, mode, result, size in tokens before and after, lines kept. No text, no session ID.
- Exit codes: 0 compacted, dry run or skipped; 2 refused; 3 error (no session, several sessions, compact failed); 64 bad option.
- Tests (fake command, throwaway journal and log): window refused (03:30, 04:00, 05:09) and open at the edges (03:29, 05:10, 05:25); recent message skipped (9 min) and 10 min compacted; waiting request skipped (both statuses), answered request does not block; unreadable journal skips; normal run logs sizes and uses the handover 23 command; log has no ID or token; dry run changes nothing; no session, two sessions and a failed compact are errors; "no compaction needed"; unknown size after; bad option.

Live results (outside 03:30 to 05:10 AST, gateway untouched: pid 3792080, 0 restarts, one process):
1. Dry run 20:23 AST: `would-compact size=15289; nothing changed` (`h26/compact-log-dryrun.txt`).
2. `--execute` 20:24 AST: `compacted size_before=15289 size_after=0` (`h26/compact-log-manual.txt`). The after size read 0 because the gateway has no token count for the session until its next turn. I changed the script afterwards so this shows as `size_after=unknown` plus `kept_lines=1`, and added a test. The later runs use that format. The honest after-measure is "1 line kept".
3. COO request, run ID loop6-coo-001, through the COO Slack channel session with the same route as handover 23 (`openclaw agent --agent coo --session-key <channel session>`, no delivery to Slack). The question: what is on the calendar for 2026-10-30; ask the CoS to read the journal. Reply (`h26/coo-001-reply.txt`): entry CHO - Workout - 10302026-0001, 2026-10-30 07:00 to 08:00, written and pushed. This matches the two journal lines for that event. The trajectory shows 4 events with a sessions_send to the CoS during the run (`h26/coo-001-trajectory-check.txt`). Cost 0.0043 USD for the COO (`h26/coo-001-cost.txt`); the journal hash is unchanged.
   Deviation: the handover said to use the scenario tool. `scenario-run.sh prep` runs `git checkout -- state/` on the CoS journal. That would have wiped the CEO's own dentist lines, which this handover says to leave alone. So I used a read-only question and no prep. No journal write, so the calendar cron stayed active and untouched.
4. Cron proof: a temporary line `38 20 * * *` (marked `lifeos-coo-compact-proof-TEMP`, pointing at the `~/work26` copy because the repo file does not exist on the VM until the patch is applied). It fired at 20:38:01 AST and logged `compacted size_before=26640 size_after=unknown kept_lines=1` (`h26/compact-log-after-cron-proof.txt`, `h26/coo-compact-cron-output.txt`). I started it after the 10-minute quiet period that follows the loop6-coo-001 message, so it would compact and not skip. I removed it afterwards: the crontab equalled the starting copy byte for byte (checked with diff).
5. The real line is installed (below).

Crontab (`h26/crontab-start.txt`, `h26/crontab-end.txt`, `h26/crontab-diff.txt`). The diff against the starting copy is only this line:
```
25 5 * * * bash $HOME/lifeos-ro/scripts/ops/coo-compact.sh --execute >> $HOME/loop1/state/coo-compact.cron.log 2>&1 # lifeos-coo-compact
```
IMPORTANT for the CEO: that line runs the script from the repo copy. The script is in this patch, so it exists on the VM only after the patch is applied, pushed and pulled (`cd ~/lifeos-ro && git pull -q`). If that has not happened by 05:25 AST, the first run writes "No such file" to `coo-compact.cron.log` and does nothing; the health line stays INFO or turns WARN after 36 hours. Nothing breaks.

The first real 05:25 run happens after this handover ends. I did not see it. The health check shows it next time (the line is PASS now only because of the cron proof run at 20:38).

Rollback: `crontab -l | grep -v lifeos-coo-compact | crontab -` (deletes the line marked lifeos-coo-compact). The installed script is only in `~/work26` until the pull, so nothing else to undo.

## Item 3: health check
File: `deploy/loop1/health-check.py` (in the patch), tests `tests/unit/test_health_check_loop6.py` (11 tests).
- New function `compact_log_status` and line "COO morning compaction ran in the last 36 hours". It reads `~/loop1/state/coo-compact.log`. It counts the newest execute-mode run that compacted, needed no compaction, or was skipped by its own rule. PASS under 36 hours; WARN older, or when the newest run ended in an error or a refusal; INFO before the first run. Dry-run lines do not count.
- The CFO send-list line: the existing line (FAIL on drift) already expects ["coo","cos"] for the CFO. A test pins that expectation. No second line.
- Installed `~/loop1/health-check.py` replaced by the repo copy: backup `~/loop1/health-check.py.pre-loop6`, sha256 equal (checked). Output now: PASS 77, WARN 0, FAIL 0, INFO 5 (`h26/health-installed-now.txt`).
- Note: the policy lines (privacy_display, calendar_target) read `~/lifeos-ro/contracts/policy/calendar.yaml`, which now has the keys after the earlier pull.

## End state (rule 5)
- Gateway: one process, pid 3792080, 0 restarts. Not restarted in this handover.
- Crontab: the starting copy plus exactly the one lifeos-coo-compact line. The calendar line is active (not paused).
- Config: byte equal to its backup (Item 1 skipped).
- Calendar and journal: at the seed plus the CEO's dentist entry for 2026-11-09 (journal numstat "5 0" against the committed seed: 3 pushed seed lines and the 2 dentist lines). I did not touch the CEO's entry. The scenario tool was not run.
- CEO ledger plugin and ledgers: plugin files hashes equal before and after (`h26/ledger-hashes-before.txt`, `-after.txt`; script `h26/ledger-hashes.sh`). The Slack ledger differs from the end of handover 25 (it grew by the CEO's own Slack activity before this handover started); it did not change during this handover.
- Not changed: agent instructions, plugins, the delete gate.
- Costs: loop6-coo-001 0.0043 USD (COO). No other agent run. Far under 0.05 per run and 1 USD per day.
- Time window: all runs between 20:23 and 20:40 AST; nothing between 03:30 and 05:10 AST.

## Patch and package
`~/handover/handover26.patch`: 5 files (1 changed, 4 new, 1 of them executable), no `contracts/registry/artifacts.yaml`, no commit, no push. It applies cleanly to a fresh clone of `~/lifeos-ro` at 1c18849. The stray `~/lifeos-ro/0` is still there (not deleted: the CEO has not said so; it is not in the patch).
Package: `~/handover-26.tar.gz` (report, patch and evidence in `h26/`).

## Things to know
- The patch must be applied and pulled before 05:25 AST for the first real run (see above). If it is late, nothing breaks.
- The compaction skips when a request is waiting. A `delete-pending-approval` line with no later `deleted` line (for example one left by a test) would block the daily compaction until it is resolved. Each skip is logged with its reason, and the health line counts a skip as a run, so the health line alone would not show a long run of skips; the log would.
- Session size after a compaction shows as `unknown` (the gateway recounts at the next turn); the log records the lines kept instead.
- Item 1 can be reopened later if the CEO wants the CFO to go through the COO. That needs a change to the CFO instructions (APR-0092 moved it the other way), so it is a separate decision and handover.
