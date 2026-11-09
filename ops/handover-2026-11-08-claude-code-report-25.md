# REPORT 25: Loop 5 (APR-0119): calendar privacy toggle, privacy gate in shadow mode, real-calendar setting

Status: DONE. One patch: `handover25.patch` (13 files, no commit, no push; `contracts/registry/artifacts.yaml` NOT included, as instructed; it applies cleanly to a fresh clone of ~/lifeos-ro at 4fa20d8). Evidence is in `h25/`.

**The real calendar was NOT touched.** No real calendar ID, token, Google authorization or sign-in exists anywhere; `GCAL_CALENDAR_REAL` does not exist; every live calendar action in this loop used the Google TEST calendar. `calendar_target` stays `test`.

First pull: it showed APR-0118 at the top (APR-0119 was not pushed yet). I stopped, told the CEO, and continued after the push showed APR-0119 (commit 4fa20d8).

## Tests (scratch copy ~/work25)
- Full unit suite: 457 tests OK (h25/unit-suite.txt). Before this loop: 422. New: 35 (20 gcal, 5 shadow report, 10 health lines).
- Validator: 0 blocking failure(s), 1 warning(s) (h25/validator.txt).
- Gate plugin node tests: 19 pass (h25/gate-node-tests.txt). Before: 11. The node tests need the openclaw package; I used a temporary symlink in the scratch copy and left it out of the patch.
- A pre-existing ResourceWarning (an unclosed SSL socket from a gcal test that builds a Google client) appears in the baseline too; not changed.

## Item 1. Calendar privacy toggle (done)
Files: contracts/policy/calendar.yaml, scripts/gcal/gcal_sync.py, scripts/gcal/gcal_busy.py, tests/unit/test_gcal_sync.py (PrivacyDisplayTests 11 tests, PolicyAndTargetTests 9 tests).
- calendar.yaml: `privacy_display: busy` and `calendar_target: test`, with comments (values, default, effect, "edit the line, push, VM pulls"). Status stays draft.
- The job reads `privacy_display` from the repo policy copy (`--policy PATH` overrides the file); `--privacy-display busy|full` overrides the value. Missing, unknown or unreadable value: busy, and one alert line "privacy_display unreadable, using busy".
- Full mode: a privacy=high entry is created, moved and deleted like a normal mandated event but keeps the hidden key (`lifeos_event`) so it is found again. Journal lines are identical in both modes (the journal keeps the real name).
- Reconcile (each run): for every live privacy=high entry whose latest journal line is pushed, the job reads its Google event (newest first, at most 50 reads per run) and fixes the title when the mode differs: busy to full sets the real title from the journal name, full to busy blanks it (description and place cleared). Only an event with the entry's hidden key is touched; never recreated; no journal line written; deletes keep the CEO approval path in both modes.
- Design notes: (1) `require_busy_event` now accepts a keyed event shown with its mandated title (full mode). An event without the key is still refused. (2) One extra Google read per live privacy=high entry per run (cap 50). (3) A move after a mode change retitles and moves in one patch.
- Live proof on the TEST calendar (h25/toggle-proof.sh, toggle-proof-output.txt, toggle-sync.log). Run ID loop5-tog-001, cron paused the suite way. COO request "make the 10-30 workout private": CHO to CoS, journal line `written ... privacy=high`, checker passed, job: `made busy`. Then the job from ~/work25:
  - step 1 `--privacy-display busy`: Google event u5hu1cvtppfs9vna4qtqvbro2c at 2026-10-30T07:00 shows `busy`.
  - step 2 `--privacy-display full`: same event ID, title `CHO - Workout - 10302026-0001` ("retitled (full)"); a second full run changed nothing.
  - step 3 `--privacy-display busy`: same event ID, title `busy` again ("blanked (busy)"); a second busy run changed nothing.
  - No duplicate, no new event, journal 11 lines before, during and after (numstat 5 0 throughout), no leftover.
  - Cleanup: run loop5-tog-002 prep deleted the busy event with its key and re-seeded. Final: journal numstat 3 0, calendar listing equals the seed (3 workouts and the existing busy seed event; other events 0). Crontab restored (byte-equal to the start copy).
  - Cost: loop5-tog-001 0.0104 USD (h25/run-costs.txt).

## Item 2. Privacy gate in shadow mode (done, LIVE, left running)
Files: deploy/loop3/gate-plugin/{index.js, openclaw.plugin.json, README.md, tests/gate.test.js}, scripts/ops/gate-shadow-report.py, tests/unit/test_gate_shadow_report.py.
- `mode` plugin setting (`plugins.entries.gate-plugin.config.mode`): shadow is the default; only the exact word `enforce` enforces; any other value is shadow. Shadow always returns pass, never blocks, fails OPEN (error logged as `hook_error_failed_open`). Enforce is unchanged (existing tests now pass `mode: "enforce"`).
- Shadow log, one JSON line per turn: time, mode, agent, channel_kind (slack, main, cron, agent-to-agent, suite), trigger_kind (human, internal), label, would_block, reason code, text_hash (16 hex), ms. Never the text. Parity test: shadow `would_block` equals enforce's decision for 72 combinations of agent, channel and prompt, with equal reason codes.
- Deviation, on purpose: the log is written to `~/loop1/state/gate-shadow/gate-log.jsonl` (folder 700, file 600), not in the plugin folder. OpenClaw runs the plugin from a temporary staged copy, so a log there would not last. In my first scratch run the log did land in a temporary capture folder; that is why I changed it.
- Scratch test first (own state folder, own port, no Slack, no cron; h25/scratch-*.txt, scratch-shadow-log.jsonl): 4 agents each answered; 3 of 4 would have been blocked and none was; forced error (the prefilter throws, scratch copy only): the turn answered and the log shows `hook_error_failed_open`. Scratch folder deleted afterwards (it held a copy of the agent auth files).
- LIVE install (21:07 AST, outside 03:30 to 05:10, no suite running): `openclaw plugins install --force --accept-capabilities <clean copy>` (the plugin asks for capability consent), `openclaw config set plugins.entries.gate-plugin.hooks.allowConversationAccess true`, `... config.mode shadow`, `openclaw plugins enable gate-plugin`. The gateway said "Applied in Gateway generation 3" and "Change will apply without restarting the gateway": NO restart. Gateway pid 3792080 and 0 restarts before and after; one process.
- Config diff before and after (backup `~/loop1/state/openclaw.json.pre-loop5-gate`): only the gate-plugin entry is new; every other key equal.
- CEO ledger plugin: the 4 plugin files and both ledgers have identical sha256 before and after (h25/ceo-ledger-hashes-before-full.txt, ...-after-full.txt, diff empty). The delete gate and the crontab were not changed.
- Live proof (run IDs loop5-gate-001-coo, -cho, -cos, -cfo; one plain turn each, all answered "ok"; cost 0.0010 to 0.0012 USD each, h25/run-costs.txt). The log has 4 lines, one per agent, each with the label the prefilter gave and no text (h25/live-shadow-log-sample.jsonl). Labels: coo medium, cho high, cos medium, cfo high; all 4 would have been blocked and none was. Channel kind `suite` (the session IDs carry the run ID), trigger `human`.
- First counts from the report script (h25/live-shadow-report.txt): turns 4, would block 4, high 2, medium 2, error lines 0.
- What the early numbers say (honest): the prefilter labels nothing low in these prompts, and medium turns are denied by the policy as built, so enforce mode would have blocked every one of these turns, including CHO and CFO turns by rule. The meaningful numbers need days of normal use (Slack turns, cron, agent-to-agent); the shadow log collects them. Channel kind `slack`, `cron` and `agent-to-agent` come from guesses on the hook context fields and have not been seen live yet; check them in the first Slack-day report.
- Rollback, exact commands (run with `. ~/loop1/env.sh` first):
  1. `openclaw plugins disable gate-plugin`
  2. `openclaw config unset plugins.entries.gate-plugin` (removes the entry with `hooks.allowConversationAccess` and `config.mode`)
  3. If `openclaw plugins inspect gate-plugin` still shows it loaded, restart the gateway outside 03:30 to 05:10 AST.
  4. Check: `openclaw plugins inspect gate-plugin` says not found; the health check line "privacy gate plugin loaded in shadow mode" then shows FAIL (expected after a removal; remove the line with the next health-check patch).
  The log file stays (`~/loop1/state/gate-shadow/`); delete it by hand if wanted.

## Item 3. Real-calendar setting, no authorization (done)
- `calendar_target` in the policy: test uses GCAL_CALENDAR, real uses GCAL_CALENDAR_REAL. With target real and the ID unset or empty the job exits 4 with a clear message before any Google call and writes nothing; an unknown target also refuses (exit 4); a missing key or file means test; `--calendar` still overrides (tests). Tests: 9 (PolicyAndTargetTests).
- `ops/calendar-switch.md`: how it works, where each value lives (alias in the repo YAML, IDs only in `~/loop1/gcal-sync/env`, mode 600), the later authorization step (the CEO opens the Google page, signs in and allows; token only on the VM; the old authorization was closed), one-line rollback, what changes for the CEO. Every authorization step is marked "NOT DONE, needs the CEO's go" (a separate APR).
- Proof on the VM (h25/real-target-refusal.txt): a scratch policy file with `calendar_target: real` and no real ID: dry run and real run both print the refusal and exit 4; journal sha256 and calendar listing hash equal before and after. The normal policy (test) dry run works (exit 0), nothing changed.

## Item 4. Health check (done)
- deploy/loop1/health-check.py: new line "privacy gate plugin loaded in shadow mode" (PASS shadow, WARN enforce or unknown mode, FAIL missing or not enabled), and INFO lines "calendar policy: calendar_target" and "calendar policy: privacy_display" read from the repo policy copy (WARN if not an allowed word). 10 tests (test_health_check_loop5.py).
- The installed `~/loop1/health-check.py` is replaced with the patched copy from the scratch repo (old copies kept as `health-check.py.pre-loop5`; sha256 equal to the scratch copy, cmp equal). This also closes the Loop 4 chore (it was already replaced with the Loop 4 repo copy at the end of handover 24).
- Output NOW (h25/health-installed-now.txt): PASS 75, WARN 2, FAIL 0, INFO 4. The 2 WARN are the new policy lines: the repo copy of calendar.yaml on the VM does not have the two keys until the patch is pushed and pulled. Honest.
- Output as it will read after the push and pull (h25/health-projected-after-pull.txt: the same script with only the policy path pointed at the scratch copy): PASS 75, WARN 0, FAIL 0, INFO 6.
- One line moved from PASS to INFO by itself: "log: MaxListenersExceededWarning" (it counts gateway starts in today's shared log file; my two scratch gateways added starts). Known startup warning, not a fault. The PASS count still equals 75.

## End state
- Gateway: one process, pid 3792080, 0 restarts.
- Crontab equal to its starting copy (`~/loop1/crontab.pre-loop5-20261108-2007`; diff empty, h25/crontab-final-diff.txt). The calendar cron line was paused twice the suite way and restored byte for byte.
- Calendar at the seed: journal numstat 3 0; Google listing equals the seed.
- CEO ledger plugin: same hashes (and the two ledgers).
- Health check: PASS 75, WARN 0 after the push and pull (WARN 2 until then, see Item 4), FAIL 0.
- Stray file `0` in ~/lifeos-ro: untracked, 24 bytes (three short numbers), NOT empty, so I did not delete it. CEO: delete it if you know what it is (`rm ~/lifeos-ro/0` on the VM).
- After the push: `cd ~/lifeos-ro && git pull -q`. The live cron and the live health check then read the new code and the new policy lines. Until then the live cron runs the old job (busy only), which is fine.
- Which code ran live in this loop: the toggle proof ran `~/work25/scripts/gcal/gcal_sync_cron.sh` (the new job); the normal cron still runs the old `~/lifeos-ro` job. The gate plugin runs from a clean copy of ~/work25/deploy/loop3/gate-plugin (installed into the OpenClaw state folder); the repo patch contains the same files.

## Exposure note
While reading the live config I printed the live gateway token in a tool output (a command that printed the whole `gateway` section). It is in this session's transcript only; it is not in any file, the repo, the handover folder or this package (scan: 0 hits). I did not rotate it (a config change outside this handover's list). If you want it rotated, say so.

## Secrets scan (before packaging)
CEO Slack ID (grep -cF, not printed): 0 hits. Calendar ID: 0. Gateway token: 0. Account name: 0. E-mail-like strings: 0. Deploy key: 0. Key blocks: only the old handover23.patch (its own secret-scanner patterns, not keys). Token-like strings (xox, sk-): none.
