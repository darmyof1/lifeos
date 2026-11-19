# Handover 34 to Claude Code on the LifeOS VM (COO status questions: the agent reads its own state files; COO v1.10.11)

Same Claude Code as handovers 1 to 33. The CEO approved the wording as written (APR-0133, deploy/after-loop7/coo-status-wording-v11011-approved.md, word for word). Background: handover 33 installed v1.10.10. It works when the item was routed through the COO, but on the CEO's real question (2026-11-17 17:12, "what did I last tell the CFO?") the CFO answered from its main session, which does not hold what the CEO typed in the CFO's own Slack channel, so the answer was wrong; and in one test the COO repeated a file path. v1.10.11 replaces the v1.10.10 rule: the COO asks the agent to read the last entries in its own state files, and never writes a file path or file name. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0133 ..." near the top; if not, stop and tell the CEO). Scratch copy `~/work34`. Return ONE patch `~/handover/handover34.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml), `~/handover/REPORT-34.md`, and `~/handover-34.tar.gz` containing ONLY the report, the patch and ~/handover/h34/ (move old files in ~/handover aside first, do not delete them).

## How to talk to the CEO
One step at a time; say which machine; exact text; what he should see. Never ask him for a secret, key or password; never print the gateway token or any Slack token.

## IMPORTANT: real data is in the workspaces
Since 2026-11-13 the CEO has put REAL entries into the CLO, CFO, CHO and CoS state files and the TEST calendar. The repo is public (APR-0114).
- Never copy, print or quote the content of any CLO, CFO, CHO or CoS state file, journal or calendar event into ~/handover, the report or the chat. Counts, file names and yes/no judgements only.
- Never reset, restore or re-seed anything. The regression suite is NOT run (it re-seeds the calendar). Do not touch existing calendar events or journal lines. Your tests add only synthetic lines, and they stay (append-only).
- Tests use synthetic items that you create first. Do not ask the COO about the CHO or the CoS in the synthetic tests (their latest items are real).
- If an agent reply or any raw file contains anything that looks real, leave that raw file out of ~/handover and write "raw not copied: real data" in the report.

## Hard limits
1. Allowed live changes, only these: (a) the pull; (b) COO instruction set v1.10.11 exactly as in deploy/after-loop7/coo-status-wording-v11011-approved.md (stop the gateway first, back up the file, commit in the COO workspace git as handover 33 did, start the gateway); (c) the installed health-check.py replaced with the repo copy (backup first, sha256 equal). Nothing else: no config key, no CLO, CHO, CoS or CFO file or config entry, no crontab change, no plugin change (ledger and gate plugin files byte-equal). The calendar cron line is NOT paused. No test asks for a calendar entry; if one appears, report it.
2. Synthetic data only for tests: "Test Item Two" (a purchase of 20.00 on 2026-11-18, no credit, no reminder), "Show Four-B" (a lifestyle log; use a name that was not used before, check the CLO file by grep -c only).
3. No secrets, Slack IDs, tokens, calendar ID, WirePusher ID, VM address, IPs or account names in ~/handover or the repo. Never print ~/loop1/ceo-slack-id (grep -cF only) or ~/loop1/gcal-sync/env. Straight quotes only in repo files. Cited APR numbers must exist (APR-0133 does).
4. TIME WINDOW: no agent message, compaction or gateway restart between 03:30 and 05:10 AST; not across the 05:25 to 05:40 compaction; agent runs end by 02:30 AST unless the CEO is present. Cost under 0.05 USD per run, 1 USD per day. Never reuse a run ID or a session ID (use loop34-...). One gateway. Do not change an agent instruction to make a run pass; if a test fails, keep the raw files (unless they hold real data) and report it.
5. End state: gateway one process; crontab equal to its starting copy; CLO, CHO, CoS, CFO instruction files and all config entries equal to their starting copies; ledger and gate plugin hashes unchanged; no existing journal line or calendar event changed (line and event counts before and after; only your synthetic lines added); health check PASS with version lines COO v1.10.11 and CLO v1.1, WARN 0, FAIL 0.

## Part 1. Repo and scratch
In ~/work34: edit agent-files/executive/coo/AGENTS.md: REPLACE the v1.10.10 "Status questions" rule with the v1.10.11 rule exactly as in coo-status-wording-v11011-approved.md (same place, version marker v1.10.11). Add deploy/loop1/loop1-v11011-upgrade.sh in the style of loop1-v11010-upgrade.sh: dry run; refuses unless the file is on v1.10.10; gateway must be stopped; replaces the old rule line in place (it does not add a second one); safe twice; commits in the workspace. Update the rebuild/parity expectations, the health check (COO v1.10.11) and their tests; the rebuild test must prove there is exactly ONE "Status questions" rule in the final file. Scratch gateway first (own state folder and port, no Slack, header-only synthetic state files, deleted afterwards): the script applies and the status rule is followed.

## Part 2. Live
Stop the gateway; dry run; apply; second run "already v1.10.11"; live file equals repo file; start the gateway; one process; Slack probe 5 of 5; parity PASS; install the repo health-check.py.

## Part 3. Proof (explicit-session CLI route as in handover 33; new session IDs; bare messages)
1. Create the latest CFO item: send the COO "Tell the CFO to log a purchase: Test Item Two, 20.00, on 2026-11-18. No reminder." Expected: routed, one line logged, a run ID coo-<date>-<time>.
2. Status question in a fresh session: "What did I last tell the CFO?" Expected: the COO sends the CFO one question that tells it to read its state files; the answer names Test Item Two, the CFO and a run ID. FAIL if the answer contains a file path, a file name (anything with "state/", ".md", ".csv") or says the answer came from conversation memory.
3. Create a CLO item ("Log that I started Show Four-B season 1 episode 1."), then in a fresh session "What did I last tell the CLO and was it logged?" Same expectations (CLO, Show Four-B, run ID, no path or file name).
4. Nothing exists: "What did I last tell the CFO about my pension?" Expected: it says plainly nothing was found, invents nothing, no path.
5. A synthetic item typed DIRECTLY to an agent, not through the COO (the case that failed): send a message straight to the CFO in a new session with `openclaw agent --agent cfo` (log "Test Item Three, 30.00, on 2026-11-18, no reminder"), then ask the COO in a fresh session "What did I last tell the CFO?" Expected: the answer names Test Item Three. This is the real test of the new wording. Report pass or fail plainly.
6. Routing unchanged (ask.sh prefix fine, new IDs): a lifestyle request goes to the CLO only; a budget question to the CFO.
7. The CEO sends his real status question in the COO channel when you ask: "What did I last tell the CFO?". You judge privately whether the answer names the real latest item (compare with the last line of the CFO budget file, which you read but do NOT copy) and report only: asked the CFO yes/no, named the CFO yes/no, run ID yes/no, path or file name yes/no, right item yes/no. Raw not copied: real data.

## Part 4. Read-only finding (no change)
In handover 33 the CFO reported a "session-change error" on its reply call to the COO in three runs, though the content arrived. Find the message in the gateway log for those runs (loop33 sessions, 2026-11-17 17:03 to 17:06 AST) and report in one paragraph what it says and your best explanation. Change nothing. If the log lines contain real data or tokens, report only the error text.

## Rollback (in the report, exact commands)
COO back to v1.10.10: stop the gateway; in ~/loop1/workspaces/coo run `git revert --no-edit <the v1.10.11 commit>` (the pre-upgrade file is also saved in ~/start34); start the gateway. Revert the repo patch as well (the health check expects v1.10.11).

## Report (REPORT-34.md)
Per part: done, files, results with raw evidence in ~/handover/h34/ (file diff, gateway process counts, probe, each synthetic scenario's raw reply and exact command, plugin hashes before and after, crontab diff, health check, line and event counts before and after). A plain statement that no token, Slack ID, WirePusher ID or real item is in the package. End state per rule 5. Secrets scan before packaging. `tar czf ~/handover-34.tar.gz -C ~ handover`.
