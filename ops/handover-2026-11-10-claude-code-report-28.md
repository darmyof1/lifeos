# REPORT 28 - Loop 7 (APR-0125): why the 04:00 reset does not show, health-check guard, two stale suite checks

Date: 2026-11-10 (AST), 02:15 to 03:15. Machine: the Loop 1 to 4 VM. Synthetic data and the Google TEST calendar only. Live changes: the pull, and the installed health-check.py replaced by the repo copy (rule 1b). Nothing else: no config key, crontab line, instruction, plugin, gateway restart or install. The CEO confirmed he was present for the scratch test (agent messages 02:57 and 03:01 AST, outside 03:30 to 05:10, none across 05:25).

## Plain verdicts
| Question | Answer |
|---|---|
| Does the daily reset apply to a Slack channel session? | Yes, by the OpenClaw docs and code. No override exists in the live config. |
| Does the setting work for a channel-style session? | Yes in the scratch test: after the 03:00 boundary both the main-style and the channel-style session got a new session ID (4 of 4, plain config and live-shaped config). |
| Why do the live CHO, CoS and CFO channel sessions not reset? | NOT proven. They reset once (10-29 20:12 to 20:19, at the first real Slack message after a plugin hot reload) and never again. Likely cause from the code: messages that reach them through agent-to-agent sends or `openclaw agent` runs skip the implicit expiry; only a real inbound Slack message checks it. Not tested. |
| Health-check guard | Done. New line PASS on the live config. Health check now PASS 78, WARN 0, FAIL 0, INFO 5. |
| Two stale suite checks | Done. Re-score of 51 stored runs: exactly the 14 intended verdict changes, nothing else. |

## Part 1. The 04:00 reset (P-36)
Files: `ops/session-reset-options.md` (new, in the patch). Evidence: `h28/session-keys-live.txt`, `h28/session-reset-doc-and-code-quotes.txt`, `h28/gateway-log-2026-10-29.txt`, `h28/live-sessions-started.txt`, `h28/reset-test/`.

a. Live config, session keys only: `session = {reset: {mode: daily, atHour: 4}}`. No resetByType, resetByChannel, idleMinutes, resetTriggers or per-agent session key (`session-keys-live.txt`).
Docs and code (quotes in `session-reset-doc-and-code-quotes.txt`):
- docs/concepts/session.md lines 176-179: "Daily reset ... a new session at a configured local hour (`session.reset.atHour`, default `4`) ... Daily freshness is based on when the current `sessionId` started."
- dist/reset-nVuHvB9V.mjs lines 70-81: a key containing ":group:" or ":channel:" is type "group"; with no resetByType/resetByChannel the group type uses the plain `session.reset` (lines 17-24). So a Slack channel session counts, and the live config applies daily 04:00 to it.
- Same file lines 39-49: stale when the session start time is before the most recent 04:00.
- Two code paths evaluate this. The inbound-message path (dist/get-reply-DE-fUW_A.mjs lines 4753-4781) always does. The explicit-session path (dist/agent-turn-service-C_6ZJjkm.mjs line 634) skips the implicit expiry when it is pinned to an existing session (`expectedExistingSessionId`), as agent-to-agent sends and `openclaw agent --session-key` runs may be.

b. Why a marker on 10-29 evening (`gateway-log-2026-10-29.txt`, no message text, IDs replaced): the ledger plugin was installed by hot reload at 19:40 to 19:42 (plugins.install, plugins.setEnabled, "config hot reload applied", the Slack plugin retired and restarted inside it). No gateway restart: the last start was 07:44 that day. The first real Slack messages after the reload came at 20:12 (CHO), 20:13 (CoS), 20:19 (CFO), and each produced one "daily" marker, which also set the channel session start time to that moment (`live-sessions-started.txt`: CHO 10-29 20:12, CoS 20:13, CFO 20:19; session IDs unchanged). The config had not changed since 10-24 (backups compared). My reading: before the reload the inbound check saw no start time on the row and treated the session as fresh; after the reload it read the 10-23 start from the transcript, saw it was stale, and reset. This is an inference; the log shows no reset line.
Since then real Slack inbound is rare (about 12 messages on 11-01, 2 on 11-08, 4 on 11-10 in the logs; I did not check which agent each went to). Most traffic to these sessions came by agent-to-agent sends and scenario runs.

c. Scratch test (`h28/reset-test/`: configs sanitized, scripts, replies, session tables before and after). Two scratch gateways, own state folders and ports, no Slack, no cron, cloud model, agents p (key agent:p:main) and q (key agent:q:slack:channel:<test id>). Boundary atHour 3 (the live value 4 is inside the no-message window). g1: plain `session.reset`. g2: the live `session` block and live `tools` block with atHour 3 (the only changed value). Messages before at 02:57, after at 03:01, via `openclaw agent --session-key`, run tags loop7-rst-g1/g2-p/q-before/after (new, not reused).
| gateway | session | before | after (03:01) |
|---|---|---|---|
| g1 plain | main-style | 31849300 | 2c555f38 NEW |
| g1 plain | channel-style | 5380c230 | 60180a1f NEW |
| g2 live shape | main-style | f279cd73 | 90dca8e8 NEW |
| g2 live shape | channel-style | b123ed7c | a3803744 NEW |
Result: the configured daily reset works for channel-style keys. The test used the `openclaw agent` route, so it does NOT show what happens through agent-to-agent sends or a real Slack message, and the exact value 4 was not tested. Scratch gateways were stopped by pid after checking their state folder; the scratch folder was deleted; the live gateway is untouched. Cost: 8 short messages, not measured per run, well under 0.02 USD.

d. Options (none applied; details in `ops/session-reset-options.md`):
- A. Leave it. No cost. The sessions grow (CHO 167 and CoS 274 messages in 9 to 10 days).
- B. A morning compaction job for the CHO, CoS and CFO channel sessions, like the COO's. Script change, tests, 3 crontab lines (live change, later handover). Low cost, small risk, already proven for the COO.
- C. Test the agent-to-agent path in a scratch copy at the next daytime boundary (about 0.02 USD, one hour, no live change) to confirm the cause, then choose between B and a different route.
Recommendation: C, then B if confirmed. A is acceptable in the meantime.

## Part 2. Health-check guard (APR-0125)
`deploy/loop1/health-check.py`: function `workspace_confined_status` and the line "file tools of the CHO, CoS and CFO are confined to their workspace". PASS when each of the three has `tools.fs.workspaceOnly` true (or has no read/write/edit in alsoAllow); FAIL when false or missing, or when the agent has no tools block. Tests `tests/unit/test_health_check_loop7.py` (7: PASS, FAIL per agent for false and for missing, missing block, no file tools, COO-style, non-file tool). The older per-agent line "<agent> file tools limited to workspace" stays; the new line is the single summary the handover asked for.
Installed copy replaced at the end: backup `~/loop1/health-check.py.pre-loop7`, sha256 equal to the repo copy (`h28/health-installed-sha.txt`). Output (`h28/health-end.txt`): the new line PASS ("cfo: confined; cho: confined; cos: confined"); PASS 78, WARN 0, FAIL 0, INFO 5. A first install failed with a NameError (function defined after its use); I fixed the order, re-ran the tests and re-installed within minutes. During that minute the installed health check errored; nothing else depends on it.

## Part 3. Two stale checks (`deploy/loop3/vm/reg-criteria.py`)
- D2 heuristic `claims_google_changed`: a journal statement ("appended a deleted line", "journal") is no longer a Google claim unless the same sentence also names Google. Future/conditional sentences ("will be removed", "if approved") are not claims. Still failing: "deleted from Google ... before the push job", "removed the event from the calendar", "Google Calendar is already updated", "has been deleted from the calendar". Tests `tests/unit/test_reg_criteria_loop7.py` (11): the four real handover 27 replies (d2-03, 04, 06, 08) as accurate cases, journal sentences, future sentences, 5 made-up false claims, the old shape, and the overlap check.
- Overlap check: `overlap_google_ok(glist, written_rows, display)`. busy: a Google row at 10-28 08:00 titled busy. full: a row at 08:00 whose title equals the written entry's journal title. No event at 08:00, or no written line in full mode, fails. The display value is the one the job printed ("(display full)"), else the policy file, else busy.
- Not changed (not asked): the other "Google shows busy" checks (scenarios R, C, P) are also stale under `full`.
- Re-score tool: `deploy/loop3/vm/rescore-criteria.py` (new; the old `rescore.py` was specific to the ack rule). It reads the stored result files, re-runs only the two checks, copies all other criterion lines, and also re-runs the OLD checks to prove the parser reproduces every stored verdict (it did: all). Result `h28/rescore.md`: 51 runs (20 of handover 27, handover 20's ten, loop3-reg-001 to 003). Verdict changed: 14 = d2-03, 04, 06, 08 and ov-01 to ov-10, all FAIL to PASS, each by the intended check alone. Every other run, including the genuine older failures (reg-001-01, 001-06, 002-01, 002-03), is unchanged. Changes outside the two checks: none. Old runs without a printed display value are scored as busy (the policy became full on 2026-11-09).

## End state (rule 5)
- Gateway: one process, pid 3792080, not restarted.
- Crontab equal to its starting copy (`h28/crontab-start.txt`, `crontab-end.txt`, diff empty). Config byte-equal to `~/loop1/state/openclaw.json.pre-loop7`.
- Ledger and gate plugin files: sha256 equal to the handover 27 end values (`h28/plugin-hashes-end.txt`).
- Calendar at the seed: journal numstat 3 0, Google lists 3 events (`h28/google-end.txt`). Prep was never run.
- Health check PASS 78, WARN 0, FAIL 0. Unit suite 502 OK (was 484). Validator: 4 blocking failures, all "tracked file not in registry" for the 4 new files (rescore-criteria.py, session-reset-options.md, two test files); the patch excludes artifacts.yaml as ordered, so the planning chat must add those 4 registry entries. Otherwise 0 blocking, 1 old warning.
- Time window: nothing between 03:30 and 05:10, nothing across 05:25.

## Patch and package
`~/handover/handover28.patch`: 6 files (2 changed, 4 new), no artifacts.yaml, no commit, no push; applies cleanly to a fresh clone. Package `~/handover-28.tar.gz`: report, patch, h28/ only. The stray `~/lifeos-ro/0` is still there (not in the patch).
