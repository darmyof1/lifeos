# Handover 32 to Claude Code on the LifeOS VM (Loop 7: the COO builds its own run ID; COO v1.10.9)

Same Claude Code as handovers 1 to 31. The CEO approved the wording as written (APR-0129, deploy/loop7/runid-wording-approved.md, word for word; time zone AST). Background: on 2026-11-14 the COO used a stray word the CEO had typed at 05:50 as the run ID and event ID of a Show Four line, and at 10:28 it used "MPBLACK26" the same way. The routing was right both times. The COO instructions have no rule for making a run ID. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0129 ..." near the top; if not, stop and tell the CEO). Scratch copy `~/work32`. Return ONE patch `~/handover/handover32.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml), `~/handover/REPORT-32.md`, and `~/handover-32.tar.gz` containing ONLY the report, the patch and ~/handover/h32/ (move old files in ~/handover aside first, do not delete them).

## How to talk to the CEO
One step at a time; say which machine; exact text; what he should see. Never ask him for a secret, key or password; never print the gateway token or any Slack token.

## Hard limits
1. Allowed live changes, only these: (a) the pull; (b) COO instruction set v1.10.9 exactly as in deploy/loop7/runid-wording-approved.md (stop the gateway first, back up the file, commit in the COO workspace git as the earlier upgrades did, start the gateway); (c) the installed health-check.py replaced with the repo copy (backup first, sha256 equal). Nothing else: no config key, no CLO, CHO, CoS or CFO file or config entry, no crontab change, no plugin change (ledger and gate plugin files byte-equal). No test in this handover asks for a calendar entry, so the calendar cron line is NOT paused and the CoS must not write a calendar line; if one appears, report it.
2. Synthetic data only: "Show One", "Show Two", "Show Three". The CEO's real shows are not replayed.
3. No secrets, Slack IDs, tokens, calendar ID, VM address, IPs or account names in ~/handover or the repo. Never print ~/loop1/ceo-slack-id (grep -cF only). Straight quotes only in repo files. Cited APR numbers must exist (APR-0129 does). The CEO's two odd run IDs may be shown as <STRAY-TEXT> and <ODD-ID> in repo files.
4. TIME WINDOW: no agent message, compaction or gateway restart between 03:30 and 05:10 AST; not across the 05:25 to 05:40 compaction; agent runs end by 02:30 AST unless the CEO is present. Cost under 0.05 USD per run, 1 USD per day. Never reuse a run ID or a session ID. One gateway. Do not change an agent instruction to make a run pass; if a test fails, keep the raw files and report it.
5. Final state: gateway one process; crontab equal to its starting copy; CLO, CHO, CoS, CFO instruction files and all config entries equal to their starting copies; ledger and gate plugin hashes unchanged; calendar journal at the seed (3 0) and Google at the three seed events; health check PASS with version lines COO v1.10.9 and CLO v1.1, WARN 0, FAIL 0.

## Part 1. Repo and scratch
In ~/work32: edit agent-files/executive/coo/AGENTS.md (the new last rule and the version marker v1.10.9) exactly as in runid-wording-approved.md. Add deploy/loop1/loop1-v1109-upgrade.sh in the style of loop1-v1108-upgrade.sh (dry run, refuses unless the file is on v1.10.8, gateway must be stopped, safe twice, commits in the workspace). Update the rebuild/parity expectations and the health check (COO v1.10.9) and their tests. Scratch gateway first (own state folder and port, no Slack, deleted afterwards): FIRST check what date and time the COO can see: ask it in scratch "what is the date and time now" and compare with the VM clock in AST. If it cannot give the right date and time (more than 5 minutes off or unknown), STOP: no live change; write the raw evidence in the report and tell the CEO, I will return with another wording. If it can, then in scratch: a lifestyle request with no run ID in the message gets a run ID of the form coo-YYYYMMDD-HHMM, and the CLO event ID is that run ID plus -clo-01.

## Part 2. Live
Stop the gateway; apply the upgrade script; start the gateway; one process; Slack probe 5 of 5 (the same probe as handover 31); parity lines PASS; install the repo health-check.py.

## Part 3. Proof (route: explicit-session CLI route as in handover 31; session IDs and any run ID the message states are new, loop32-...)
For tests 1 to 3 the message must NOT contain the words "run ID" (do not use the earlier ask.sh prefix); write a small variant that sends the bare message with a fresh session ID, and record the exact command.
1. No run ID stated: "Add a new show to my list: Show Three, watching season 1 episode 1." Expected: the COO builds coo-<today>-<time in AST within 5 minutes of the real time>, sends it to the CLO, the CLO line carries that run ID and the event ID <run ID>-clo-01, the COO names the run ID in its answer.
2. Stray word first: in one session send first the single word "Ozark" alone, then (second message in the same session) "Note that I dropped Show Three." Expected: the run ID is built from the date and time, not from "Ozark".
3. Run ID stated: "Run ID loop32-keep-1. Log that I finished Show One season 5." Expected: the COO keeps loop32-keep-1, the CLO event ID is loop32-keep-1-clo-01.
4. Routing unchanged (new IDs, with the ask.sh prefix is fine here): a lifestyle request goes to the CLO only; a budget question to the CFO; a workout question with "ask the right chief" to the CHO.
5. The regression suite (the same set handover 31 used, one run) compared with handover 31's re-scored result (3 pass, 4 fail: D3 and three stale busy checks): no new failure. Report the numbers.
6. Cleanup: the test lines in the CLO state file stay (append-only, synthetic); the CoS journal must still be 3 0 and Google three seed events.
7. The CEO sends one real message in the COO channel at the end, when you ask: a lifestyle request with a made-up show and no run ID; check the route and the run ID.

## Rollback (in the report, exact commands)
COO back to v1.10.8: stop the gateway; in ~/loop1/workspaces/coo run `git revert --no-edit <the v1.10.9 commit>` (the pre-upgrade file is also saved in ~/start32); start the gateway. Revert the repo patch as well.

## Report (REPORT-32.md)
Per part: done, files, results with raw evidence in ~/handover/h32/ (file diff, gateway process counts, probe, each scenario's raw reply and the exact command, the clock comparison, plugin hashes before and after, crontab diff, health check). A plain statement that no token or Slack ID is in the package. End state per rule 5. Secrets scan before packaging. `tar czf ~/handover-32.tar.gz -C ~ handover`.
