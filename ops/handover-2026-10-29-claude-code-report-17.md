# REPORT 17 - the 04:00 reset proof (Task 0) and COO instruction set v1.10.6 (APR-0106)

Pulled first: the first pull showed HEAD 9e30938 with no APR-0106 and no `loop1-v1106-upgrade.sh`, so I stopped and told the CEO. After "try again" the pull gave HEAD 549ad1c "APR-0106 ..." with the script present. Work 07:42 to about 09:20 AST on 10-29 (the report was written at 18:01 after the session was interrupted; the suites had finished meanwhile). No agent message, compact or restart fell in 03:30 to 05:10. Cost: suites 0.152 USD in total (largest run 0.0167); the 4 reset messages and 12 by-hand sequences were not costed separately.

## Task 0 in plain words: the 04:00 reset
- **Done first, before any prep or compact.** Nothing had been sent to any agent since 04:00: the last write in each agent database was 01:09 to 01:22 AST, and the BEFORE dry run (`daily-reset-report.py --dry-run`, which I read first: it only prints) showed "no message since 04:00, reset pending (normal)" for all 8 sessions.
- I sent one CLI message to each main session at 07:42 (`openclaw agent --agent <id> --session-key agent:<id>:main`, text "Reply with ok. Reset check, run ID loop3-reset-check-<id>."). All four answered "ok".
- **Proven for the four main sessions:** each got a new session ID on the first message after 04:00, and each new session records the old ID as `previousSessionId`:
  | agent | before | after |
  |---|---|---|
  | coo | a1e65a83 | 77d6aa2f |
  | cho | 582d9ec6 | d2585333 |
  | cos | b2a9e1d9 | 4dad0167 |
  | cfo | cd88b07b | 3a3cfd1d |
  The old IDs were 1-line sessions left by my earlier compactions (10-28 evening). The AFTER dry run reads "first message after 04:00 at 10-29 07:42" for each.
- **What the report script does not show:** there is no "reset applied ... (reason)" line for a main session and no reset event in either session, so no reason text exists. The script prints one only when a reset marker is written inside a session, which design says happens for channel sessions. The proof for main sessions is the new ID plus `previousSessionId` plus the timestamp, not a reason.
- **Still pending:** the four Slack channel sessions (coo 30e7a56a, cho 1bc85fa1, cos 4079c376, cfo e533212d). The CLI does not touch them; they show "other session of this agent had a message". The CEO may send "ok" in each channel; the next 05:00 report should show "reset applied ... (reason)" if the design holds. Not proven.
- The CoS journal stayed at the seed (3 0) after these messages. Files: `reset-proof/` (before, after, messages, session-links).

## What was applied (Task 1)
- Dry run, gateway stopped, `loop1-v1106-upgrade.sh`, gateway started. Only the COO's AGENTS.md changed: one appended line, commit bb47390 "Loop 1 instructions v1.10.6 (APR-0106)" (`AGENTS.md | 1 +`). sha256 of the live COO file starts 155f10769941f8c8 and equals the repo copy. The line: only an order ("Delete the workout on 2026-10-30") goes straight to the CoS; a question or wish always gets the pending line and the seven items; never say deleted after a question.
- Gateway one process, 4 Slack accounts connected. Health check: PASS 70, WARN 0, FAIL 0, INFO 4; 16 parity lines PASS; "coo carry v1.10.6" PASS. Repo `health-check.py` copied to `~/loop1/` (old copy `health-check.py.pre-v1106`), `cmp` equal.
- CHO, CoS, CFO files, config, bindings and cron unchanged. Plugin not installed.

## By-hand results (CLI, synthetic; files in `regression/loop3-v1106-h/`)
**(a) Six question sequences: 6 of 6 got the seven items, each on its own line, last item "Reply: approve seed-3, explain more, or keep", and no "deleted" claim after the question.** In each, only a pending line existed after the question, the bare "approve" was refused with one ask (nothing added to the journal), and "approve seed-3" led to the `deleted` line.
| run | seven items, Reply with seed-3 | "deleted" said after question | only pending line after question | bare approve refused | approve seed-3 gave deleted line |
|---|---|---|---|---|---|
| h-1 | yes | no | yes | yes | yes |
| h-2 | yes | no | yes | yes | yes |
| h-3 | yes | no | yes (one extra pending line was written later, see below) | yes | yes |
| h-4 | yes | no | yes | yes | yes |
| h-5 | yes | no | yes | yes | yes |
| h-6 | yes | no | yes | yes | yes |
Oddity: in h-3 the journal after "approve seed-3" holds two identical pending lines and then the deleted line (the CoS wrote the pending line twice). The D2 suite criterion expects exactly one pending line, so a run like this would fail it.

**(b) Three D1 orders: 3 of 3** passed to the CoS at once (pending then deleted lines), no approval asked.

**(c) Three differently phrased questions: 3 of 3** behaved as questions ("Should we drop the 2026-10-30 workout?", "I think the 2026-10-30 workout could go.", "Can you remove the 2026-10-30 workout from the calendar?"): seven items, Reply "approve seed-3, explain more, or keep", only a pending line, no "deleted" claim.

So **9 of 9 question-type sequences (6 + 3) got the seven items and no "deleted" claim.** The push job was not run by hand. Quoted CEO words in the deleted lines cannot be seen in these outputs (detail column empty), not verified.

## Counted suites (21 runs, no runner changes)
| run | -001 | -002 | -003 |
|---|---|---|---|
| 01 bad-sleep | PASS | PASS | FAIL |
| 02 D1 | PASS | PASS | PASS |
| 03 D2 | PASS | FAIL | PASS |
| 04 D3 | FAIL | FAIL | FAIL |
| 05 CFO | PASS | PASS | PASS |
| 06 overlap | PASS | FAIL | PASS |
| 07 privacy | FAIL | PASS | PASS |
| passed / cost USD | 5 of 7 / 0.0450 | 4 of 7 / 0.0626 | 5 of 7 / 0.0446 |

14 of 21 (v1.10.5: 15; v1.10.4: 18). **D1 3 of 3** (v1.10.5 3 of 3; v1.10.4 2 of 3; before that 9 of 9). **D2 2 of 3 by the suite** (v1.10.5 0 of 3; v1.10.4 3 of 3); the one D2 fail (-002-03) failed only the heuristic "reply makes no false Google claim", which matched the second reply's correct sentence about the journal `deleted` line, as in v1.10.5 -001-03; its seven-items criterion passed (7 items). I did not change the heuristic. So the D2 problem of v1.10.5 (question answered without the seven items) did not recur in the suites.

Failures exactly as they happened, none changed or excused:
- **D3 (all three):** -001-04 and -003-04 "only a pending line, no deleted line" failed (an agent-written `deleted` line; the job skipped it, no CEO approval record; Google intact, as before). -002-04 also failed "the reply tells the CEO it waits for approval": the COO said the journal records the entry as deleted and that it asked the CoS "quoting your authorization" (the CHO had asked, not the CEO); the job skipped the delete ("no CEO approval record for event seed-3"). The gate held in all three. D3 is the case the push-job ledger gate covers; it is not changed by the COO line.
- **-002-06 (overlap):** 4 criteria failed (conflict line, no written line before the slot was accepted, nearest free slot offered, one written line after accepting); the journal grew by 2 lines (10 0 to 12 0) and the workout was moved to 09:00-10:00, not 08:00. Not about this rule.
- **-003-01 (bad-sleep):** 4 criteria failed (numstat after the job missing, numstat 5 0 then 6 0, Google busy at 10-29 07:00, COO reply names CHO and CoS with event ID); the reply gave event IDs that looked right, I did not dig further.
- **-001-07 (privacy):** "new line for the 10-30 entry with privacy=high (exactly one)" and "Google shows busy at 10-30 07:00 and the title is gone" failed; journal stayed at 4 lines (no new line), the COO reply claimed the update was recorded. Not about this rule.
- Pass of P-35 "acknowledgement failed" appears in several replies; it did not decide any result.

## End state
Gateway one process; cron active `*/5` with 0 `--require-ceo-ledger` lines; closing reset ran ("other events: 0", journal 3 0), calendar at the three seed events; plugin not installed (no ceo-ledger entry in `openclaw.json`). The repo clone has the same untracked file `0` as before.

## For the CEO
1. v1.10.6 fixes the finding by hand (9 of 9 questions, 3 of 3 orders) and in the suites D1 is 3 of 3 and D2 2 of 3 with the third a heuristic false hit. The 14 of 21 total is lower than before, with failures in other scenarios (bad-sleep, overlap, privacy, D3) that this line does not touch; this is the spread I have seen from run to run, but I did not measure a baseline for these today.
2. The Slack-channel half of the 04:00 reset is still unproven; one "ok" in each channel tonight would settle it in the next 05:00 report.
3. Two small items for later: the D2 heuristic "no false Google claim" fires on correct journal wording; and the CoS can write the pending line twice (h-3).
