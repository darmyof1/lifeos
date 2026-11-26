# Handover 43 to Claude Code on the LifeOS VM (Loop 8 step 3: the domain rule for the CHO, CFO and CLO, and the CFO savings sentence)

Same Claude Code as handovers 1 to 42. The CEO approved the wording as written, Option A (APR-0144, deploy/loop8/domain-rule-approved.md, word for word). Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0144" near the end of decisions/APPROVALS.md; if not, stop and tell the CEO). Scratch copy `~/work43`. Return ONE patch `~/handover/handover43.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml), `~/handover/REPORT-43.md`, and `~/handover-43.tar.gz` containing ONLY the report, the patch and ~/handover/h43/ (move old files in ~/handover aside first, do not delete them).

## How to talk to the CEO
One step at a time; say which machine; exact text; what he should see. Never ask for a secret; never print the gateway token or any Slack token.

## IMPORTANT: real data is in the workspaces
Real entries are in the CLO, CFO, CHO and CoS state files and the TEST calendar. The repo is public.
- Never copy, print or quote the content of any CLO, CFO, CHO or CoS state file, journal or calendar event. File names, counts and yes/no judgements only.
- Never reset, restore or re-seed anything. The regression suite is NOT run. Do not touch existing lines or calendar events.
- Tests use synthetic topics (prefix "test-"). Their files stay (append-only). Handover 41 already left test-houseplants (CLO) and test-water-intake (CHO) live; use NEW names for this run (below) and check by ls that they do not exist.
- If an agent reply or a raw file holds anything that looks real (the COO and CFO repeated real CFO entries in handover 41), leave the raw file out of ~/handover and write "raw not copied: real data".

## Hard limits
1. Allowed live changes, only these: (a) the pull; (b) the three instruction files at exactly the approved wording (CHO v1.11, CFO v1.13, CLO v1.3): gateway stopped, backups in ~/start43, commit in each workspace git, gateway started (one restart); (c) the installed health-check.py replaced with the repo copy (backup first, sha256 equal). Nothing else: no config key, no COO or CoS file, no state/topics.md change except the lines the synthetic tests add, no crontab change, no plugin file. The calendar cron line is NOT paused. No test asks for a calendar entry; if one appears, report it.
2. Synthetic data only. Topics: CLO "test-orchids"; CHO "test-stretching"; CFO "test-gift-fund" (the same as handover 41, which failed: now it must work); "test-bike-lights" for an other-chief test. No real names, amounts or accounts.
3. No secrets, Slack IDs, tokens, calendar ID, WirePusher ID, VM address, IPs or account names in ~/handover or the repo. Never print ~/loop1/ceo-slack-id (grep -cF only) or ~/loop1/gcal-sync/env. Straight quotes only. Cited APR numbers must exist (APR-0144 does).
4. TIME WINDOW: no agent message, compaction or gateway restart between 03:30 and 05:10 AST; not across the 05:25 to 05:40 compaction; agent runs end by 02:30 AST unless the CEO is present. Cost under 0.05 USD per run (record per run), 1 USD per day. Never reuse a run or session ID (use loop43-...). One gateway. Do not change an agent instruction to make a run pass; if a test fails, keep the raw files (unless real data) and report it.
5. End state: gateway one process; crontab equal to its start; config equal; COO and CoS instruction files equal; plugin hashes unchanged; CHO, CFO and CLO instruction files equal to the approved wording; no older journal line or calendar event changed (counts before and after: only your synthetic lines and files added); health check PASS with WARN 0, FAIL 0 and version lines CHO v1.11, CFO v1.13, CLO v1.3, COO v1.10.12, CoS v1.10.2.

## The wording (copy from deploy/loop8/domain-rule-approved.md exactly; do not retype it)
Part A: one new last rule in each of the CHO ("Loop 1 rules (all agents)"), CFO (same) and CLO ("Rules"), after the New topics rule, with the version marker "Domains (instruction set v1.11 / v1.13 / v1.3)". Part B (Option A): for the CFO only, the savings sentence is added inside the CFO's Domains rule, as its last sentences. Versions: CHO v1.10 becomes v1.11; CFO v1.12 becomes v1.13; CLO v1.2 becomes v1.3. Nothing else in any file changes.

## Part 1. Repo and scratch
In ~work43: edit the three agent files; add deploy/loop8/loop8-domain-rule-upgrade.sh in the style of loop8-topic-rule-upgrade.sh (one agent id or all three; dry run; refuses unless the file is on the expected old version CHO v1.10, CFO v1.12, CLO v1.2; gateway must be stopped; inserts the rule once and is safe to run twice; commits AGENTS.md only with the message "Loop 8 domain rule <ver> (APR-0144)"). Update the rebuild and parity tests, the health check version lines and the "workspace ready" commit-message rule (accept a message starting "Loop 8 domain rule"; handover 41 hit this exact failure); the rebuild test must prove exactly ONE "Domains" rule per file. Strict suite and validator must pass. Then a scratch gateway (own state folder and port, no Slack, header-only synthetic state, deleted afterwards): apply the script to the three scratch workspaces and run the scenarios of Part 3 there first.

## Part 2. Live
Stop the gateway; dry runs; apply; second run says "already"; live files equal the repo files; start the gateway; one process; Slack probe 5 of 5; install the repo health-check.py; run it.

## Part 3. Scenarios (explicit-session CLI route as in handovers 33 and 41; bare messages; new session IDs; scratch first, then live)
A. Other chief's domain, six checks, each a bare message to that chief; expected: ONE sentence naming the right chief; no file proposed; ls and line counts unchanged.
 1. To the CLO: "start tracking my sleep" (expected: the CHO).
 2. To the CLO: "start tracking my monthly budget" (the CFO).
 3. To the CHO: "start tracking my vacation plans" (the CLO).
 4. To the CHO: "start tracking my test-bike-lights" (the CLO).
 5. To the CFO: "start tracking my houseplants" (the CLO).
 6. To the CFO: "start tracking my protein intake" (the CHO).
B. Own domain still works (the handover 41 normal case, with new names): CLO "I want to start tracking my test-orchids." then "Yes, use that." then "Add: test-bloom, first flower"; CHO "I want to start tracking my test-stretching." then yes then one entry. Expected as in handover 41: propose, wait, create file with header and entry with run and event ID, +1 index line, later entries append, no calendar entry.
C. CFO savings case (the handover 41 failure): "I want to start tracking a test-gift-fund." Expected: it proposes state/test-gift-fund.md (its own file, columns include date, what, amount, running balance, run ID, event ID) and does NOT ask for a starting balance first or point at the investments file; "Yes, use that." creates the file, one entry, +1 index line; the investments file line count unchanged.
D. The older CFO investments rule still works: "What do you track?" lists the topics by name including the investments file; in scratch only, an invested fund entry ("Add test-index-fund, contribution 10.00") still goes to the investments file. Do NOT write test entries into the live investments file.
E. Account number refusal for each chief: "log my bank account number 1234 for the test-orchids" (CHO: test-stretching; CFO: test-gift-fund): refused, nothing written.
F. COO routing still works: a lifestyle request to the CLO only, a budget question to the CFO only; calendar untouched. If the COO status question about the CFO is partial again, record it only.
Report pass or fail per scenario with raw files (synthetic only) and cost per run. Stop and report if any chief writes to the calendar or edits an older line.

## Rollback (in the report, exact commands)
Stop the gateway; in each of the three workspaces run `git revert --no-edit <the commit>` for the domain rule (the pre-upgrade files are also in ~/start43); the test-* files may stay (append-only, synthetic); start the gateway; reinstall the previous health-check.py; revert the repo patch.

## Report (REPORT-43.md)
Per part: done, files, results with raw evidence in ~/handover/h43/ (file diffs, process counts, probe, each scenario's raw reply and exact command, plugin hashes before and after, crontab diff, health check, line and event counts before and after, cost per run). A plain statement that no token, Slack ID, WirePusher ID, live send-log line or real item is in the package. End state per rule 5. Secrets scan before packaging. `tar czf ~/handover-43.tar.gz -C ~ handover`.
