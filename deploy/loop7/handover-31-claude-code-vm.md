# Handover 31 to Claude Code on the LifeOS VM (Loop 7: the COO routes lifestyle requests to the CLO; CLO v1.1)

Same Claude Code as handovers 1 to 30. The CEO approved the wording as written (APR-0128, deploy/loop7/routing-wording-approved.md, word for word). Background: on 2026-11-11 00:40 the CEO asked the COO in Slack to log a TV episode and make an appointment; the COO sent it to the CHO (wrong: the COO did not know the CLO, could not send to it, and the CLO lacks the handoff-call rule). Nothing was written (checked read-only). Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0128 ..." near the top; if not, stop and tell the CEO). Scratch copy `~/work31`. Return ONE patch `~/handover/handover31.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml), `~/handover/REPORT-31.md`, and `~/handover-31.tar.gz` containing ONLY the report, the patch and ~/handover/h31/ (move old files in ~/handover aside first, do not delete them).

## How to talk to the CEO
One step at a time; say which machine; exact text; what he should see. Never ask him for a secret, key or password; never print the gateway token or any Slack token.

## Hard limits
1. Allowed live changes, only these: (a) the pull; (b) COO instruction set v1.10.8 and CLO instruction set v1.1 exactly as in deploy/loop7/routing-wording-approved.md (stop the gateway first, back up both files, commit each in its workspace git as the earlier upgrades did, start the gateway); (c) ONE config key: "clo" added to agents.entries.coo.tools.agentToAgent.send (backup first, diff of that key only, every other key equal) plus whatever minimum the receiving side needs for the COO to reach agent:clo:main, found in scratch first and shown to the CEO before it is applied (if it needs a change on the CHO, CoS or CFO entries, STOP and ask); (d) the temporary pause of the calendar cron line for the tests that make the CoS write a line, exactly as handover 26, 28 and 30 did it, restored byte for byte (the CEO approved this pause again for this handover: APR-0128); (e) the installed health-check.py replaced with the repo copy (backup first, sha256 equal). Nothing else: no CHO, CoS or CFO instruction or config entry, no new crontab line, no plugin change (ledger and gate plugin files byte-equal).
2. Synthetic data only. The CEO's tonight message used a real show name: tests use "Show One" and "Show Two" and a made-up episode synopsis request; the real show request of the CEO is not replayed.
3. No secrets, Slack IDs, tokens, calendar ID, VM address, IPs or account names in ~/handover or the repo. Never print ~/loop1/ceo-slack-id (grep -cF only). Straight quotes only in repo files. Cited APR numbers must exist (APR-0128 does).
4. TIME WINDOW: no agent message, compaction or gateway restart between 03:30 and 05:10 AST; not across the 05:25 to 05:40 compaction; agent runs end by 02:30 AST unless the CEO is present. Cost under 0.05 USD per run, 1 USD per day. Never reuse a run ID. One gateway. Do not change an agent instruction to make a run pass; if a test fails, keep the raw files and report it.
5. Final state: gateway one process; crontab equal to its starting copy; CHO, CoS, CFO instruction files and config entries equal to their starting copies; ledger and gate plugin hashes unchanged; calendar at the seed; health check PASS with the version lines at COO v1.10.8 and CLO v1.1, WARN 0, FAIL 0.

## Part 1. Repo and scratch
In ~/work31: edit agent-files/executive/coo/AGENTS.md (send line, table row, the new last rule, version marker v1.10.8) and agent-files/department/clo/AGENTS.md (handoff-call bullet, the two new rules, version marker v1.1) exactly as in routing-wording-approved.md. Add deploy/loop1/loop1-v11-clo-upgrade.sh and deploy/loop1/loop1-v1108-upgrade.sh in the style of loop1-v1107-upgrade.sh (dry run, refuses unless the file is on the previous version, gateway must be stopped, safe twice, commits in the workspace). Update the rebuild/parity expectations and the health check (COO v1.10.8, CLO v1.1) and their tests. Scratch gateway first (own state folder and port, no Slack): COO with "clo" in its send list and both new instruction files, one lifestyle request through the COO route reaches the CLO and is logged; also find what the receiving side needs (if anything) and write it down.

## Part 2. Live
Stop the gateway; apply both upgrade scripts and the one config change; start the gateway; one process; Slack probe 5 of 5; parity lines PASS.

## Part 3. Proof (new run IDs loop31-..., the Slack-channel-session route the earlier COO scenarios used, synthetic names)
1. Lifestyle log plus synopsis plus appointment, in one message: "I am watching Show One, season 5 episode 3, log it and give me a synopsis, and make an appointment to watch episode 4 at 4:00 am" (the 04:00 time is only a test input; the test calendar line is removed afterwards). Expected: the COO sends to the CLO (never the CHO), the CLO writes the line in state/lifestyle.md, answers with a short synopsis marked "from memory, may be wrong", asks the CoS for the calendar entry by the handoff call, the CoS writes the line (normal privacy), the COO reports only what the CLO confirmed and names it.
2. A lifestyle request that does not ask for an appointment: no calendar line.
3. The CLO asked directly in its own channel route for something it cannot look up: it says so and asks for the date.
4. A workout request still goes to the CHO; a budget request still goes to the CFO; the COO never names the CHO for a lifestyle request (3 tries with different wording).
5. The existing COO regression scenarios (A to E style, run the same set handover 21 used) still pass; the existing CFO calendar scenario still passes.
6. Calendar cleanup: remove the test line(s) from the CoS journal the way handover 30 did (the pushed seed stays: journal 3 0), cron restored.
7. The CEO sends one real message in the COO channel at the end, when you ask: a lifestyle request with a made-up show; check the route and the answer.

## Rollback (in the report, exact commands)
COO back to v1.10.7 and CLO back to v1.0 (the pre-upgrade files and their commits), the one config key removed from the backup copy.

## Report (REPORT-31.md)
Per part: done, files, results with raw evidence in ~/handover/h31/ (file diffs, the one config diff, gateway process counts, probe, each scenario's raw reply, plugin hashes before and after, crontab diff, health check). A plain statement that no token or Slack ID is in the package. End state per rule 5. Secrets scan before packaging. `tar czf ~/handover-31.tar.gz -C ~ handover`.
