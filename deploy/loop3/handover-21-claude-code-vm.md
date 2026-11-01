# Handover 21 to Claude Code on the LifeOS VM (plain approve: install the gate rule and COO v1.10.7, then test with one and with two requests waiting)

Same Claude Code as handovers 1 to 20. The CEO approved APR-0110 (the gate accepts a plain approve when exactly one delete is waiting) and approved the COO wording v1.10.7 as written (APR-0111). Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0111 ..." at the top; deploy/loop1/loop1-v1107-upgrade.sh must exist). If not, stop and tell the CEO. Start after 05:10 AST.

## Hard limits (as before, plus)
1. Changes allowed: the COO's AGENTS.md through deploy/loop1/loop1-v1107-upgrade.sh only (gateway stopped, one commit, AGENTS.md only), the installed health-check.py (backup first), and the pull of the repo. No other agent file, no config, plugin or crontab change (except the suites' own pause and resume).
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, tokens, calendar ID or VM address in ~/handover/. Never print ~/loop1/ceo-slack-id (grep -cF only).
3. TIME WINDOW: no agent message, `sessions compact` or gateway restart between 03:30 and 05:10 AST; agent runs end by 02:30 AST. Cost under 0.05 USD per run, 1 USD per day.
4. Journals and git history append-only. Never reuse a run ID. Do not change an instruction to make a run pass. One gateway only.
5. If the COO upgrade or the health check fails, restore the COO AGENTS.md from its git history (git checkout of the previous commit's file, committed), start the gateway, and tell the CEO.

## Part 1. Install
1. Run the unit tests on the VM copy: `python3 -m unittest discover -s ~/lifeos-ro/tests/unit -p "test_*.py"` (expect all OK, one skipped). Show the PlainApprovalTests names passing.
2. `bash ~/lifeos-ro/deploy/loop1/loop1-v1107-upgrade.sh --dry-run`, then stop the gateway (`systemctl --user stop openclaw-loop1-gateway`), run it for real, start the gateway. Show the commit (AGENTS.md only) and that the live COO AGENTS.md equals agent-files/executive/coo/AGENTS.md in the repo (the COO file has no channel placeholders).
3. Back up and replace `~/loop1/health-check.py` with `deploy/loop1/health-check.py` (it expects COO v1.10.7), sha256sum equal. Run it: expect PASS 74 or more, WARN 0, FAIL 0. Save the full output to ~/handover/health-check-output.txt this time.
4. The plugin and the cron line stay as they are; confirm both in the health check.

## Part 2. Live check in Slack, through the cron, with the CEO
Tell the CEO exactly what to type; every message to an agent needs the @mention. Use the calendar seed events. Between steps wait for two cron runs (10 minutes) and read sync.log, the journal and the calendar by their fields only. Report each step.
A. One request waiting. The CEO asks the COO to remove the workout on 2026-10-30. Check the COO's request ends with "Reply: approve <event ID>, explain more, or keep" and has the sentence "type approve and the event ID, or just approve if this is the only request waiting". The CEO sends "@COO approve" (plain). Expect: the COO passes it to the CoS; a deleted line; the next cron run deletes the Google event once. Then restore the seed (closing-reset method of earlier handovers) and confirm the calendar is at the seed.
B. Two requests waiting (the test the CEO asked for first). The CEO asks the COO to remove two different seed events (the 2026-10-30 workout and one other seed event you choose; say which). Two requests, two event IDs. The CEO sends "@COO approve" (plain). Expect: the COO asks once for approve and the event ID and does not pass it; if it passes it anyway, record that, and the gate must still delete neither (two cron runs). Report what the COO said and what the ledger line shows (fields only).
C. Still two waiting. The CEO sends "@COO approve <event ID of the second request>". Expect: only that one is deleted.
D. One left. The CEO sends a NEW "@COO approve" (plain). Expect: the remaining one is deleted, and its deletion happens after this new message, not earlier (the plain message of step B must not count: compare ledger times with the sync.log delete time). Restore the seed and confirm.
E. One regression run each of D1 (scenario 2), D2 (scenario 3) and D3 (scenario 4) as single-scenario suites with new prefixes (for example loop3-p21-d1, -d2, -d3). Report pass or fail by criterion.

## Report (~/handover/REPORT-21.md)
Part 1 results first (tests, commit, equality, health check). Then A to E with the exact COO wording seen, ledger fields, sync.log lines and the gate's verdict on each plain approve. Say plainly whether any delete happened that should not have. End state: gateway one process, crontab line unchanged and active, calendar at the seed, plugin enabled, costs. Package with `tar czf ~/handover-21.tar.gz -C ~ handover` after a secrets check that includes the CEO's Slack ID (compare against the ID file without printing).
