# Health-check proposal (not installed)

Two new lines for `~/loop1/health-check.py`, plus one fix to the reset report. The CEO decides; then a fix script is made.

1. Plugin loaded and hook-only. Run `openclaw plugins inspect ceo-ledger` (read only). PASS if the output has `Status: enabled`, `Shape: non-capability` and `Capability mode: none`. FAIL if the plugin is missing or disabled. WARN if the shape changed. Also compare the four installed file hashes (prefixes ee4e490ab5108b30, 767ca80faa71b970, a97a8993eb9d3bd9, 1b98f60e4fbff9cc) with the repo copy.
2. The calendar-job cron line carries the option for both ledgers. Read `crontab -l`; take the line containing `gcal_sync_cron.sh` (not starting with `#`). PASS if it contains `--require-ceo-ledger` twice, with the paths ending `scenario-ledger.jsonl` and `slack-ledger.jsonl`. FAIL if the option is missing. INFO if the line is paused (starts with `#`), because the suites pause it on purpose.

Python sketch:

    rc, out = run(["crontab", "-l"])
    line = next((l for l in out.splitlines() if "gcal_sync_cron.sh" in l and not l.lstrip().startswith("#")), "")
    ok = line.count("--require-ceo-ledger") == 2 and "scenario-ledger.jsonl" in line and "slack-ledger.jsonl" in line

3. Fix for the "3 processes" reading. `daily-reset-report.py` line 22 counts every line from `pgrep -af 'openclaw.*gateway'` that does not contain "pgrep". That also counts a shell whose command text mentions both words. `health-check.py` already filters the lines (" gateway run", "openclaw-gateway", " gateway --port"; no "bash -c"). The report should use the same filter.
