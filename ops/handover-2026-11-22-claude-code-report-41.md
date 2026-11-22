# REPORT 41 (APR-0142): the topic rule for the CHO, CFO and CLO (Loop 8)

Pull ok (APR-0142 present). Patch `handover41.patch`: 7 files, `git apply --check` ok on a fresh clone.

## Result in one paragraph
The rule is live in all three chiefs at the approved wording (CHO v1.10, CFO v1.12, CLO v1.2) and works for the normal case: propose a file and columns, wait for yes, create the file, one index line, later entries append. Scenarios 5 (another chief's domain) FAILED for all three chiefs: they proposed a file instead of naming the other chief (nothing was written). The CFO also failed 1 to 3 with the specified topic "test-gift-fund" because it treated a fund as an investments entry. I did not change any instruction to make a run pass. Fixing these needs a wording decision (see the end).

## Part 1: repo
- agent-files/department/{cho,cfo,clo}/AGENTS.md: rule added once as the new last rule, wording copied from deploy/loop8/topic-rule-approved.md with the version marker; CLO first Role line widened in place as written. No other line changed.
- deploy/loop8/loop8-topic-rule-upgrade.sh: [cho|cfo|clo] (none = all three), --dry-run, refuses unless CHO v1.9, CFO v1.11, CLO v1.1, gateway must be stopped, inserts once ("already has the topic rule" on a second run), CLO role line widened, creates state/topics.md if missing (header plus one line per existing state file NAME, never content, never topics.md itself), commits AGENTS.md only with the message "Loop 8 topic rule <ver> (APR-0142)".
- health-check.py: version lines CHO v1.10, CFO v1.12, CLO v1.2 (COO v1.10.12 unchanged); new line "topic index" per chief (names only; WARN if a state file has no index line). One addition beyond the handover: the "workspace ready" rule accepts a commit message starting "Loop 8 topic rule" (the first live health run showed 3 FAIL "instruction commit missing" because it only knew "Loop 1 instructions" and "Loop 7 instructions"; first run kept as `h41/health-after-first-run-3-FAIL.txt`).
- Tests: rebuild test runs the new script, proves exactly one "New topics" rule per file, last-rule position, second run changes nothing, old version refused, seeding holds names only (content marker never copied); health tests for the index line and versions. Strict suite 551 OK; validator 0 blocking, 1 usual warning (`h41/strict-suite-tail.txt`, `validator-tail.txt`).
- Scratch gateway (own state, own port, no Slack, header-only synthetic state, deleted afterwards): script applied (`h41/scratch/apply.txt`, `second-run.txt`), scenarios run before live (`h41/scenarios-scratch/`). Scratch results matched the live ones below, with the CFO alternative topic "test-subscriptions" passing 1 to 4 (the specified test-gift-fund was not retried in scratch beyond the first run).

## Part 2: live
- Gateway stopped, dry run (`live-dryrun.txt`), apply (`live-apply.txt`; commits "Loop 8 topic rule v1.10 / v1.12 / v1.2 (APR-0142)" in each workspace git), second run "already" for all three (`live-second-run.txt`). Live files differ from the repo copies by exactly one line each (the channel placeholder), same as every earlier version. Backups in ~/start41. Gateway started once; one process; Slack 5 of 5 (`slack-probe.txt`).
- Topic index line counts (names only, `index-counts.txt`): CHO 1, CFO 2, CLO 4 at seeding.
- Health check installed from the repo copy (backup `health-check.py.pre-h41`, sha256 equal, `sha-equal.txt`).
- Health check run against the patched repo copy: PASS 92, WARN 0, FAIL 0, INFO 6 (`health-after.txt`): versions COO v1.10.12, CoS v1.10.2, CHO v1.10, CFO v1.12, CLO v1.2; topic index PASS for all three. Against ~/lifeos-ro the parity lines for the three chiefs stay red until the patch is pushed.

## Part 3: scenarios (live, `openclaw agent --agent <id> --session-id loop41-l-...`, bare messages; commands in `h41/run.py` and the scenario files)
Deviation: the messages name the topic with the "test-" prefix ("I want to start tracking my test-houseplants.") so the created files carry the test- prefix as required.

| # | CLO test-houseplants | CHO test-water-intake | CFO test-gift-fund |
|---|---|---|---|
| 1 propose, create nothing | PASS | PASS | FAIL: said the investments ledger covers funds, asked for a starting balance, no file proposal |
| 2 yes: file + header + entry with run and event ID, +1 index line, no calendar | PASS (3-line file, index 4 to 5, event ID present) | PASS (index 1 to 2) | FAIL: nothing created (it waited for a balance) |
| 3 second entry: +1 line, index unchanged | PASS | PASS (live: health-plan unchanged; in scratch the CHO also appended a health-plan line, as its older health-fact rule says) | not run (nothing exists) |
| 4 "what do you track?" lists topics, no content | PASS (raw not copied: real data) | PASS (raw not copied) | PARTIAL: lists budgets and investments (no test topic existed); no content (raw not copied) |
| 5 other chief's domain: names the chief, writes nothing | FAIL: proposed a sleep file (nothing written) | FAIL: proposed a vacation-plans file (scratch: said "CoS", wrong chief) (nothing written) | FAIL: proposed a houseplants file (scratch: "no owner listed") (nothing written) |
| 6 account number: refused, nothing written | PASS | PASS | PASS |
| 7 routing through the COO | lifestyle request to the CLO only: PASS (CLO +1 line); budget question to the CFO only: PASS; calendar untouched (CoS file counts unchanged). Status question "What did I last tell the CFO?": the COO relayed the CFO answer but said it could not check the send log, so this part is only partial. | | |

Counts before and after (`counts-before.txt`, `counts-after.txt`): only added lines and files: CLO lifestyle +1 (Test Place Nine), new test-houseplants (4 lines), CHO new test-water-intake (3 lines), new topics.md in CHO (3), CFO (3), CLO (6), COO send log +5. No older line changed; no calendar entry or CoS file change. The CLO and CHO each posted one line in their own channel (the usual rule). No calendar entry was made.
Cost per run: see `h41/run-costs.txt` (per scenario files; all under 0.0025 USD; 15 saved runs total 0.0223 USD). Runs whose raw is not copied cost 0.0011 to 0.0032 USD each.
Real data: some COO and CFO replies in scenario 7 repeated real CFO entries; they were not saved or copied. Everything in `scenarios/` and `scenarios-scratch/` is synthetic.

## Findings for the planning chat (wording decisions, not made here)
1. Domain split (scenario 5): the rule says to name the other chief, but the chiefs do not know the other domains (the CLO scope is now wide, so sleep looks like lifestyle). Suggest adding one short list of domains to the rule: health and nutrition and sleep with the CHO; money, budgets, investments and funds with the CFO; everything else personal with the CLO; calendar with the CoS.
2. CFO and funds: the 1.11 investments rule claims anything fund-like. A "gift fund" is cash saving; the handover topic was a poor test. A topic outside investments (test-subscriptions in scratch) worked.
3. Status question for the CFO via the send log (scenario 7c) was partial; worth one look in a later handover.

## End state (rule 5)
Gateway one process (PID changed once, by the planned restart). Crontab equal. Config equal (hash). COO and CoS instruction files equal to start. CHO, CFO and CLO files carry the approved wording. send-log, ceo-ledger, gate-plugin hashes unchanged (`hashes-before.txt`, `hashes-after.txt`: only the three chief AGENTS.md differ). Health PASS 92, WARN 0, FAIL 0.

## Rollback
1. systemctl --user stop openclaw-loop1-gateway
2. For each of cho, cfo, clo: cd ~/loop1/workspaces/<id> && git revert --no-edit <commit> (commits "Loop 8 topic rule ..."; the pre-upgrade files are also in ~/start41)
3. Remove state/topics.md in the three workspaces (names only; no real content); the test-* files may stay (append-only, synthetic).
4. systemctl --user start openclaw-loop1-gateway
5. cp ~/loop1/health-check.py.pre-h41 ~/loop1/health-check.py; revert the repo patch.

## Package statement
No token, Slack ID, WirePusher ID, live send-log line or real item is in the package.
