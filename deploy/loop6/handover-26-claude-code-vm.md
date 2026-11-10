# Handover 26 to Claude Code on the LifeOS VM (Loop 6: CFO send list, COO morning compaction)

Same Claude Code as handovers 1 to 25. The CEO approved Loop 6 (APR-0121, scope in deploy/loop6/LOOP6-SCOPE.md). Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0121 ..." at the top; if not, stop and tell the CEO). Work on repo files in a scratch copy (`rm -rf ~/work26 && cp -a ~/lifeos-ro ~/work26`), run the full unit suite and the validator there, return ONE patch `~/handover/handover26.patch` (git add -A; git diff --cached --binary; no commit, no push) EXCLUDING contracts/registry/artifacts.yaml (git reset that file before the diff). Write ~/handover/REPORT-26.md and package everything, raw evidence files included, as ~/handover-26.tar.gz (report and patch inside). Delete the stray untracked ~/lifeos-ro/0 only if the CEO says so in this chat.

## How to talk to the CEO
One step at a time; say which machine; give the exact text; say what he should see. Never ask him to print, paste or send a private key, a token or a password; never print the gateway token (when reading the config print only the key you need, e.g. with a small script that outputs that one value).

## Hard limits (as before, plus)
1. Allowed live changes, only these: (a) the pull; (b) the one config key agents.entries.cfo.tools.agentToAgent.send set to ["coo"] (back up the config first, show a diff of that key only, every other key equal; gateway restart only if the hot reload does not apply it, outside 03:30 to 05:10 AST); (c) ONE new crontab line, the one in the scope (plus a temporary extra line for the cron proof, removed byte for byte afterwards); (d) the temporary pause of the calendar cron line exactly as the suites do it, restored byte for byte. Nothing else: no agent instruction, no plugin change, no change to the delete gate or the CEO ledger plugin or its ledgers.
2. Synthetic data and the Google TEST calendar only. No real calendar, no real data.
3. No secrets, Slack IDs, tokens, calendar ID, VM address or account names in ~/handover or the repo. Never print ~/loop1/ceo-slack-id (grep -cF only). Straight quotes only in repo files; no IP addresses in evidence files (redact). Cited APR numbers must exist (APR-0121 does).
4. TIME WINDOW: no agent message, `sessions compact` or gateway restart between 03:30 and 05:10 AST; agent runs end by 02:30 AST unless the CEO is present. Cost under 0.05 USD per run, 1 USD per day. Never reuse a run ID. One gateway. Journals and git history append-only.
5. Final state: gateway one process; crontab = starting copy plus exactly the one new line; calendar at the seed (3 events, journal 3 0) unless a proof step left the dentist entry, which the CEO created: leave that CEO entry alone; ledger plugin hashes unchanged; health check PASS 75 or better, WARN 0, FAIL 0.

## Item 1. CFO send list to COO only
a. Save the crontab and the config backup (`~/loop1/state/openclaw.json.pre-loop6-cfo`). Show the current value of the key and the CFO AGENTS.md sentence about who it may message (read only).
b. Set the key to ["coo"]. Confirm it took effect (hot reload or restart per rule 1). Config diff: only that key.
c. Prove: run the existing CFO scenarios with new run IDs (loop6-cfo-001...): they still pass; one CFO turn that asks it to send to the CoS shows no send (log line or tool result), nothing reaches the CoS. Cost under the limit.
d. Rollback in the report: set the key back to ["coo","cos"] with the exact command.

## Item 2. COO morning compaction
Read ops/handover-2026-11-04-claude-code-report-23.md (the 6 and 6 measure, how `sessions compact` was run on the COO Slack channel session) and its evidence under ops/loop3-h23-2026-11-04/.
a. In ~/work26 write scripts/ops/coo-compact.sh as in the scope (dry run default; refuses 03:30 to 05:10 AST; skips and logs when the COO channel session had a message in the last 10 minutes or a CEO request is waiting; one log line per run, no text; exit codes). Use the same compact command and session key that handover 23 used (no new way). Tests (tests/unit/test_coo_compact.py) with a fake command: window refused, recent message skipped, waiting request skipped, normal run logs, dry run changes nothing.
b. Manual live run outside the window: first a dry run, then `--execute`; log line shows before and after sizes. Then one COO request from the CEO's Slack channel via the existing scenario tool (new run ID loop6-coo-001): the COO still answers correctly (it asks the CoS, the answer matches the journal).
c. Cron proof: add a temporary line a few minutes ahead (same wrapper, extra comment marker), let cron fire it once, check the log, remove it byte for byte. Then install the real line `25 5 * * *` ... # lifeos-coo-compact. Crontab diff against the starting copy: only that line.
d. The first real 05:25 run happens after you finish: say so in the report; the health check line (item 3) shows it next time (INFO until then).
e. Rollback in the report: delete the line marked lifeos-coo-compact from the crontab.

## Item 3. Health check
deploy/loop1/health-check.py: (1) CFO send list equals ["coo"] (PASS; WARN otherwise); (2) newest COO compaction log line younger than 36 hours (PASS; WARN if older; INFO if no run yet). Functions plus tests in the existing style. Replace the installed ~/loop1/health-check.py with the repo copy at the end (backup first, sha256 equal).

## Report (~/handover/REPORT-26.md) and package
Per item: done, files, test counts, live results with raw evidence files in ~/handover/h26/ (config diff of the one key, CFO scenario output, compaction log lines before and after, cron proof log, crontab before and after and their diff, health check output, ledger plugin hashes before and after). End state per rule 5. Secrets scan before packaging (CEO's Slack ID compared without printing, no keys, no tokens, no addresses). `tar czf ~/handover-26.tar.gz -C ~ handover`.
