# Install and test plan for the CEO ledger plugin (APR-0102 follow-up). DO NOT RUN until the CEO gives a separate yes (new APR).

Everything below is a plan. Nothing was run. Commands start with `source ~/loop1/env.sh`. `<...>` are placeholders; the CEO's Slack user ID is typed by the CEO into the file and never put in the repo or in ~/handover.

## Window and limits
- Start after 05:10 AST or before 03:30 AST so the whole install (about 2.5 h with the regressions) ends before 02:30 for agent runs; the gateway restart and the Slack tests must not fall in 03:30 to 05:10. Cost: regressions about 0.15 USD (D1, D2, D3 three each, before and after); nothing else uses a model.
- One gateway restart only (step 4). If a second is needed, stop and ask.
- The cron does NOT get `--require-ceo-ledger` in this plan. That is a further decision.

## 0. Preconditions
1. `git pull`, expect the APR for the install. Health check PASS 71 WARN 0 FAIL 0; gateway one process; cron `*/5`; Google test calendar has only the 3 seed events; CoS journal numstat 3 0.
2. Backup: `cp ~/loop1/state/openclaw.json ~/loop1/state/openclaw.json.pre-ceo-ledger-$(date +%Y%m%d-%H%M)`.
3. Stage the plugin: copy `~/handover/ceo-plugin/{openclaw.plugin.json,package.json,index.js,ledger.js}` to `~/loop1/plugins/ceo-ledger/` and `chmod a-w` the four files. Record `sha256sum` of the four files in the report; compare with `~/handover` copies.
4. Unit tests once more: `cd ~/handover/ceo-plugin && node --test test/ledger.test.js` (12 tests OK) and the repo gcal tests (155 OK).
5. The CEO creates the ID file himself/herself: `umask 077; printf '%s\n' '<CEO Slack user ID>' > ~/loop1/ceo-slack-id; chmod 600 ~/loop1/ceo-slack-id`. Check only the mode and length (`stat -c %a`, `wc -c`); never print it.

## 1. Regression before (D1, D2, D3, three each)
Single-scenario suites keep every run ID unique (each suite has its own closing reset): for n in 1 2 3: `regression-suite.sh loop3-pre-d1-$n --only 2`, `loop3-pre-d2-$n --only 3`, `loop3-pre-d3-$n --only 4`. About 10 min each, 9 runs. Expected as in handover 12 (D1, D2 pass; D3 may produce an agent `deleted` line, which the job skips only if the cron-side flag is used by the suite, as it is today). Save results; do not tune.

## 2. Install
1. `openclaw plugins install ~/loop1/plugins/ceo-ledger` (a copy install, not `--link`), accept the capability consent, then `openclaw plugins enable ceo-ledger`. If the CLI says the config needs a restart, do not restart yet.
2. `openclaw plugins inspect ceo-ledger --json`: shape must be hook-only, one hook `message_received`, no tools, commands, services or routes. If anything else is listed: stop and roll back.

## 3. The one gateway restart
`systemctl --user restart openclaw-loop1-gateway`, wait until `systemctl --user is-active` says active and `pgrep` shows one process. Then:
- `openclaw plugins inspect ceo-ledger --runtime --json`: loaded, hook `message_received` registered, no errors.
- Gateway log has no "plugin failed" lines and no ceo-ledger warnings.
- `~/loop1/ceo-ledger/` exists with mode 700 only after the first CEO message; before that, the plugin has written nothing.
- Health check PASS 71; all four agents still answer (the regression in step 6 covers this).

## 4. Observe-only checks (the plugin must change nothing)
1. A CEO message in the COO channel: "Ledger test 1: reply with the word ok. Event id test-evt-01." The COO answers exactly as before (same latency, normal reply). The Slack ledger gains exactly one line: sender CEO, channel slack, `event_tokens` contains `test-evt-01`, `text_sha256` equals `printf '%s' '<exact text>' | sha256sum`, no text, no raw ID in the file (`grep -c` the CEO ID against the file must be 0; check without printing the ID).
2. The same kind of message in each of the other three agent channels (CHO, CoS, CFO): one line each (4 lines in total). This confirms the hook fires in all four channels.
3. Send the same message twice quickly (edit-free resend): still one line per Slack message ID.
4. A message from a non-CEO sender (a second Slack user, or the CEO's colleague, in a channel the bot reads): the agent behaves as before, no new line. If no second human is available, say so in the report; the unit test covers this case but a live one is better.
5. A CLI message (`openclaw agent --agent coo --session-id ledger-cli-test -m "Reply with ok."`): no new Slack line.
6. approve_word checks (APR-0103), one message each in the COO channel, then read only the fields of the newest ledger lines (`tail -n 3 ~/loop1/ceo-ledger/slack-ledger.jsonl | python3 -c 'import sys,json; [print(json.loads(l)["approve_word"], json.loads(l)["event_tokens"]) for l in sys.stdin]'`; never print an ID or the whole line):
   - "Ledger test 2: approve test-evt-02": `approve_word` true, tokens contain `test-evt-02`.
   - "Ledger test 3: do not approve test-evt-03": `approve_word` false.
   - the pasted COO line, "Reply: approve test-evt-04, explain more, or keep": `approve_word` false.
   Expected: 3 more lines, true / false / false. Agents answer as before.
7. Unwritable directory (optional, quick): `chmod 500 ~/loop1/ceo-ledger`, send one CEO message, expect a normal agent reply, no new line and one warning in the gateway log; then `chmod 700` again.

## 5. Gate end-to-end by hand (TEST calendar, no cron change)
1. Journal at seed. In Slack the CEO asks the COO to delete the 10-30 workout. The COO and CoS write a pending line (never a deleted one) and the COO posts the seven-item request with the event ID.
2. Run the job by hand without approval: `LIFEOS_SYNC_ARGS="--require-ceo-ledger ~/loop1/ceo-ledger/scenario-ledger.jsonl --require-ceo-ledger ~/loop1/ceo-ledger/slack-ledger.jsonl" bash ~/lifeos-ro/scripts/gcal/gcal_sync_cron.sh`: nothing is deleted (no deleted line yet, or "no CEO approval record").
3. The CEO answers in Slack with exactly "approve <event ID>" (the ID from the COO request, for example "approve loop2-x-01"). The CoS appends the deleted line. Run the job by hand with the same arguments: the event is deleted in Google; `ceo-ledger-used.json` in the job's state dir holds the message ID; run it again: nothing more.
3b. Bare approve (APR-0103): repeat steps 1 to 2 with a new pending line, then the CEO sends only "approve". The ledger line has `approve_word` true and no matching token; run the job: nothing is deleted ("no CEO approval record"). Then "do not approve <event ID>": line has `approve_word` false; run the job: nothing is deleted. Only then "approve <event ID>": deleted.
4. A reply "Yes, I approve" without the event ID leads to a skip ("no CEO approval record"). Note the result; this is the known limit (design.md section 4).
5. Restore: `scenario-run.sh prep` style reset to the seed (3 events, journal 3 0).

## 6. Regression after (same nine runs as step 1)
Suites `loop3-post-d1-1..3`, `loop3-post-d2-1..3`, `loop3-post-d3-1..3`, same commands. Compare to step 1: D1 and D2 must still pass with the delete in Google, D3 behaviour no worse. The plugin is not involved in CLI runs, so the point of this step is that nothing else moved (reply wording, latency, cost within noise).

## 7. Accept or roll back
Accept only if: plugin loaded and hook-only, 4 channel lines present, `approve_word` true / false / false as expected, bare "approve" deletes nothing, no line for non-CEO or CLI, no warnings, regression after not worse than before, health check PASS 71. Otherwise roll back at once.

## 8. Rollback commands
```
source ~/loop1/env.sh
openclaw plugins disable ceo-ledger
openclaw plugins uninstall ceo-ledger --dry-run   # read what it removes
openclaw plugins uninstall ceo-ledger
cp ~/loop1/state/openclaw.json.pre-ceo-ledger-<stamp> ~/loop1/state/openclaw.json   # only if a ceo-ledger entry remains in plugins.entries
systemctl --user restart openclaw-loop1-gateway
```
Then check: one gateway process, `openclaw plugins inspect ceo-ledger` says not found, health check PASS 71, cron unchanged. Keep `~/loop1/ceo-ledger/` (append-only evidence). If the cron had the flag, remove it first (design.md section 6). Rollback itself needs one more restart, which is why step 3 allows exactly one and the rollback one more by name.
