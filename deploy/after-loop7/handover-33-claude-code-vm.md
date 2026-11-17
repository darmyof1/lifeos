# Handover 33 to Claude Code on the LifeOS VM (the COO answers status questions by asking the agent; COO v1.10.10)

Same Claude Code as handovers 1 to 32. The CEO approved the wording as written (APR-0132, deploy/after-loop7/coo-status-wording-approved.md, word for word). Background: on 2026-11-15 the CEO asked the COO what he had last told the CLO. A purchase the CLO had routed through the COO was relayed to the CFO in the COO's main session (agent:coo:main), but the question was answered in the COO's Slack channel session, which had not seen it, so the COO quoted an older item. The COO has no file tools, so the new rule uses the route it already has: it asks the agent. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0132 ..." near the top; if not, stop and tell the CEO). Scratch copy `~/work33`. Return ONE patch `~/handover/handover33.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml), `~/handover/REPORT-33.md`, and `~/handover-33.tar.gz` containing ONLY the report, the patch and ~/handover/h33/ (move old files in ~/handover aside first, do not delete them).

## How to talk to the CEO
One step at a time; say which machine; exact text; what he should see. Never ask him for a secret, key or password; never print the gateway token or any Slack token.

## IMPORTANT: real data is in the workspaces now
Since 2026-11-13 the CEO has put REAL entries into the CLO, CFO and CoS state files and the TEST calendar (a vehicle maintenance log, a purchase, a credit reminder, a workout). The repo is public (APR-0114).
- Never copy, print or quote the content of any CLO, CFO, CHO or CoS state file, journal or calendar event into ~/handover, the report or the chat. Counts and file names only.
- Never reset, restore or "re-seed" anything: the old "calendar at the seed" end state NO LONGER APPLIES. Do not touch the existing calendar events or journal lines. Your tests add only synthetic lines, and they stay (append-only).
- Test the status rule only with synthetic items that you create first, so the "latest" thing the agent reports is yours. Do not ask the COO about the CHO or the CoS (their latest items are real).
- If an agent reply or a trajectory file contains anything that looks real (a real item the CEO sent), leave that raw file out of ~/handover and write "raw not copied: real data" in the report.

## Hard limits
1. Allowed live changes, only these: (a) the pull; (b) COO instruction set v1.10.10 exactly as in deploy/after-loop7/coo-status-wording-approved.md (stop the gateway first, back up the file, commit in the COO workspace git as the earlier upgrades did, start the gateway); (c) the installed health-check.py replaced with the repo copy (backup first, sha256 equal). Nothing else: no config key, no CLO, CHO, CoS or CFO file or config entry, no crontab change, no plugin change (ledger and gate plugin files byte-equal). The calendar cron line is NOT paused. No test asks for a calendar entry; if one appears, report it.
2. Synthetic data only for tests: "Test Item One" (a purchase of 10.00 on 2026-11-17, no credit, no reminder), "Show Two" (a lifestyle log). The CEO's real items are not replayed.
3. No secrets, Slack IDs, tokens, calendar ID, WirePusher ID, VM address, IPs or account names in ~/handover or the repo. Never print ~/loop1/ceo-slack-id (grep -cF only). Never print ~/loop1/gcal-sync/env. Straight quotes only in repo files. Cited APR numbers must exist (APR-0132 does).
4. TIME WINDOW: no agent message, compaction or gateway restart between 03:30 and 05:10 AST; not across the 05:25 to 05:40 compaction; agent runs end by 02:30 AST unless the CEO is present. Cost under 0.05 USD per run, 1 USD per day. Never reuse a run ID or a session ID. One gateway. Do not change an agent instruction to make a run pass; if a test fails, keep the raw files (unless they hold real data) and report it.
5. End state: gateway one process; crontab equal to its starting copy; CLO, CHO, CoS, CFO instruction files and all config entries equal to their starting copies; ledger and gate plugin hashes unchanged; no existing journal line or calendar event changed (counts of lines and events before and after; only your synthetic lines added); health check PASS with version lines COO v1.10.10 and CLO v1.1, WARN 0, FAIL 0.

## Part 1. Repo and scratch
In ~/work33: edit agent-files/executive/coo/AGENTS.md (the new last rule and the version marker v1.10.10) exactly as in coo-status-wording-approved.md. Add deploy/loop1/loop1-v11010-upgrade.sh in the style of loop1-v1109-upgrade.sh (dry run, refuses unless the file is on v1.10.9, gateway must be stopped, safe twice, commits in the workspace). Update the rebuild/parity expectations and the health check (COO v1.10.10) and their tests. Scratch gateway first (own state folder and port, no Slack, deleted afterwards, synthetic only): the COO is asked a status question and the rule is followed in scratch.

## Part 2. Live
Stop the gateway; apply the upgrade script; start the gateway; one process; Slack probe 5 of 5 (as in handover 32); parity lines PASS; install the repo health-check.py.

## Part 3. Proof (explicit-session CLI route as in handover 32; new session IDs, loop33-...; every request without the words "run ID" unless stated)
1. Create the latest CFO item: send the COO "Tell the CFO to log a purchase: Test Item One, 10.00, on 2026-11-17. No reminder." Expected: routed to the CFO, one line logged, the COO names a run ID of the form coo-<date>-<time>.
2. Status question in a DIFFERENT, fresh session: "What did I last tell the CFO?" Expected: the COO sends the CFO one question, relays its answer (Test Item One), names the CFO and a run ID, gives no file path.
3. Create the latest CLO item: "Log that I started Show Two season 1 episode 1." Then in another fresh session: "What did I last tell the CLO and was it logged?" Expected: the answer comes from the CLO (Show Two), names the CLO and a run ID, no path.
4. An agent that cannot answer: "What did I last tell the CFO about my pension?" (nothing exists). Expected: the COO asks the CFO and says plainly there is nothing, without inventing.
5. Routing unchanged (ask.sh prefix fine, new IDs): a lifestyle request goes to the CLO only; a budget question to the CFO.
6. The regression suite is NOT run (it re-seeds the calendar: forbidden now).
7. The CEO sends one real status question in the COO channel when you ask: "What did I last tell the CFO?" (his real last item may appear in the answer: do not copy the raw reply into ~/handover; report only whether the COO asked the CFO, named it, gave a run ID and no path).

## Rollback (in the report, exact commands)
COO back to v1.10.9: stop the gateway; in ~/loop1/workspaces/coo run `git revert --no-edit <the v1.10.10 commit>` (the pre-upgrade file is also saved in ~/start33); start the gateway. Revert the repo patch as well.

## Report (REPORT-33.md)
Per part: done, files, results with raw evidence in ~/handover/h33/ (file diff, gateway process counts, probe, each scenario's raw reply and exact command for the synthetic tests, plugin hashes before and after, crontab diff, health check, line and event counts before and after). A plain statement that no token, Slack ID, WirePusher ID or real item is in the package. End state per rule 5. Secrets scan before packaging. `tar czf ~/handover-33.tar.gz -C ~ handover`.
