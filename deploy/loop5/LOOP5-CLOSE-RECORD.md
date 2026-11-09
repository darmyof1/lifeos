# Loop 5 close record

Signed by APR-0120 (CEO, 2026-11-08 22:57: "close Loop 5"). Loop 5 scope was APR-0119 (P-46), deploy/loop5/LOOP5-SCOPE.md. Synthetic data and the Google TEST calendar only, throughout. The real calendar was not authorized, not touched and not tested.

## Pass criteria and result
| Criterion | Result | Evidence |
|---|---|---|
| Toggle: a private entry shows busy, then its real title, then busy again, with no new event | Met: same Google event ID through busy, full, busy; second run of each mode changed nothing; journal unchanged; seed restored | ops/loop5-h25-2026-11-08/toggle-proof-output.txt, toggle-sync.log, journal-numstat-end.txt |
| Shadow gate live: labels and would-block logged, nothing blocked, errors fail open | Met: live without a gateway restart; 4 agents answered; 4 log lines with no text; forced error in a scratch copy did not stop the turn | live-shadow-log-sample.jsonl, live-shadow-report.txt, scratch-shadow-log.jsonl |
| Real-calendar setting refuses without an ID and changes nothing | Met: dry run and real run exit 4; journal hash and calendar listing hash equal before and after | real-target-refusal.txt |
| No real calendar ID, token or authorization anywhere | Met: secrets scan 0 hits; calendar_target stays test | ops/handover-2026-11-08-claude-code-report-25.md |
| Crontab, agent instructions, ledger plugin and delete gate unchanged | Met: crontab diff empty; ledger plugin and ledger hashes equal | crontab-final-diff.txt, ceo-ledger-hashes-before-full.txt, ceo-ledger-hashes-after-full.txt |
| Tests, validator, health check | Met: 457 unit tests, 19 gate node tests, validator 0 blocking; health check PASS 75 WARN 0 after the pull | unit-suite.txt, gate-node-tests.txt, validator.txt, health-projected-after-pull.txt |

## What Loop 5 delivered
privacy_display (busy or full) and calendar_target (test or real) in contracts/policy/calendar.yaml, applied by the job each run with no restart; the gate plugin with a mode setting, installed live in shadow mode, with a log under ~/loop1/state/gate-shadow/ and scripts/ops/gate-shadow-report.py; ops/calendar-switch.md (every authorization step marked NOT DONE); three health-check lines; the installed health-check.py replaced with the repo copy (closes the Loop 4 chore).

## Early shadow numbers (honest)
The first 4 turns were all test prompts: every one would have been blocked (2 high, 2 medium), because the rules as built deny medium turns and the prefilter labeled none low. Enforcing now would block normal use. The slack, cron and agent-to-agent channel labels are guesses from hook fields and have not been seen live yet. Decide on enforcing only after a few days of real use and a new APR.

## Carried over (not part of the pass)
- Read the shadow report after a few days of Slack use (python3 scripts/ops/gate-shadow-report.py on the VM) and check the channel kinds.
- The gateway token was printed once in Claude Code's own chat (not in any file or the repo). Rotation is the CEO's call; none done.
- Stray untracked file ~/lifeos-ro/0 on the VM (24 bytes): delete if not known.
- The CEO deletes the Mac's read-only deploy key lifeos-mac-restore in the backup repository's settings.
- First scheduled weekly backup: Sunday 2026-11-15 06:15 AST.

## Still parked (each needs its own APR)
Authorizing and switching to the real calendar; enforcing the privacy gate; second-human delete-gate test; CFO send-list difference; scheduled compaction of the COO channel session; isolation; real data; the local-model box; the other chiefs. See deploy/loop3/LOOP3-CLOSE-RECORD.md.

## What keeps running
The gateway, the four agents, the calendar cron on the Google TEST calendar with the CEO ledger plugin, the gate plugin in shadow mode, the 05:00 reset report and the weekly backup line.

## Rules that stay
No real data, no real calendar switch, no health data without a new loop and a new APR. The LifeOS repo stays public (APR-0114): no secrets, IDs, tokens, keys or addresses; run scripts/verify/history_scan.sh before pushing reports. Any change to an agent instruction needs the CEO's yes as a new APR.
