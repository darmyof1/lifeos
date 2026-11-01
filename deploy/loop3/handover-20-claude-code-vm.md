# Handover 20 to Claude Code on the LifeOS VM (install two tooling changes; measure the two held gaps, no tuning)

Same Claude Code as handovers 1 to 19. The CEO approved (APR-0109): (A) two new health-check lines and the reset-report process-count fix, (B) no change to the COO's "already approved" wording, (C) measuring the two held gaps first. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0109 ..." at the top; tests/unit/test_health_check_ledger_lines.py must exist). If not, stop and tell the CEO.

## Hard limits (as before, plus)
1. Part 1 changes only two files on the VM: the health check and the reset report script (backup both first). Part 2 changes NOTHING: no agent file, instruction, config, plugin, crontab (except the normal pause/resume by the suites) or gateway restart.
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, tokens, calendar ID or VM address in ~/handover/. Never print ~/loop1/ceo-slack-id (grep -cF only).
3. TIME WINDOW: no agent message, `sessions compact` or gateway restart between 03:30 and 05:10 AST; agent runs end by 02:30 AST. If Part 2 cannot finish before 02:30, do Part 1 now and run Part 2 after 05:10. Cost under 0.05 USD per run, 1 USD per day.
4. Journals and git history append-only. Never reuse a run ID. Do not change an instruction to make a run pass.

## Part 1. Install the tooling change
1. Back up `~/loop1/health-check.py` and the installed reset-report script (find its path from the 05:00 crontab line; do not edit the cron line) to `~/loop1/backup-tooling-$(date +%Y%m%d-%H%M)/` (not in ~/handover).
2. Copy `deploy/loop1/health-check.py` and `deploy/loop2/vm/daily-reset-report.py` over them. Check with sha256sum that each installed file equals the repo file.
3. Run `python3 ~/loop1/health-check.py` (offline). Expected: the previous lines unchanged; three new lines: "calendar cron line requires the CEO ledger (both ledgers)" PASS, "CEO ledger plugin loaded and hook-only" PASS, "CEO ledger plugin files equal the repo copy" PASS (4 files equal). So PASS rises by 3 from the last run (70 or 71, say which). Any FAIL or WARN: show it, do not fix by editing the script.
4. Run the reset report with `--dry-run`: the Gateway line must read "1 process (OK)". Also run it once while a harmless shell command text containing `openclaw-loop1-gateway` is running (for example `bash -c 'sleep 20; echo openclaw-loop1-gateway' &`) and show it still reads 1.
5. Pause test: comment the calendar cron line the way the suites do (use their own pause logic via a dry run, or `sed` on a copy) and show the health check would say INFO for that line (run the function only, or run on a copy; do not leave the cron paused).

## Part 2. Measure the two held gaps (no changes, no tuning)
Gap D2: the pending line sometimes says "requested by COO" instead of CEO (seen in baseline 002-03). Gap overlap: the COO does not always offer the 08:00 slot. Use the existing regression suite only.
1. Run scenario 3 (D2) five times and scenario 6 (overlap) five times, each as a single-scenario suite with a new prefix (for example `loop3-m20-d2-1` ... `-5` with `--only 3`; `loop3-m20-ov-1` ... `-5` with `--only 6`), one after the other. Stop early if cost or the time window would be exceeded; say how many runs completed.
2. For every run record: run ID, pass or fail, each failing criterion by name, the journal line the agents wrote (event ID, status, requested by), and the COO's reply text (redact IDs and names; keep the wording). For overlap, record which slots the COO offered.
3. Count: D2 runs with "requested by" correct / wrong; overlap runs where 08:00 was offered / not. Say plainly what looks like the cause if the evidence shows one (for example, the same wording in the COO's own reply), but propose no wording yet.

## Report (~/handover/REPORT-20.md)
Part 1 results first (hashes, health-check line counts and the three new lines, the reset-report gateway line, the pause test). Then Part 2 table and counts. End state: gateway one process, crontab line unchanged and active, calendar at the seed, costs. Package with `tar czf ~/handover-20.tar.gz -C ~ handover` after a secrets check that includes the CEO's Slack ID (compare against the ID file without printing).
