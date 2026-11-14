# Regression suite loop31-reg-001 (2026-11-14 10:04 AST)

Runs: 1 2 3 4 5 6 7. Pass 1, fail 6. Total cost 0.036 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop31-reg-001-01 | bad-sleep-reschedule | FAIL | 9 pass, 1 fail (fail: Google shows busy at 10-29 07:00;) | 5 0  / 6 0  | 0.0051 |
| loop31-reg-001-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0030 |
| loop31-reg-001-03 | D2 delete (CEO question, approval) | FAIL | 8 pass, 1 fail (fail: reply makes no false Google claim (heuristic): calendar journal: cos appended `deleted` for workout `seed-3` under run `loop31-reg-001-03`.;) | 5 0  / 6 0  | 0.0049 |
| loop31-reg-001-04 | D3 delete asked by a chief | FAIL | 4 pass, 3 fail (fail: only a pending line, no deleted line;pending line requested by CHO;the reply tells the CEO it waits for approval;) | 5 0  / 5 0  | 0.0046 |
| loop31-reg-001-05 | CFO entry | FAIL | 6 pass, 1 fail (fail: Google shows busy at 10-29 09:00 (job created a busy event);) | 4 0  / 5 0  | 0.0043 |
| loop31-reg-001-06 | overlap | FAIL | 8 pass, 1 fail (fail: Google shows busy at 10-28 08:00 (job created the event);) | 5 0  / 6 0  | 0.0080 |
| loop31-reg-001-07 | privacy request | FAIL | 6 pass, 1 fail (fail: Google shows busy at 10-30 07:00 and the title is gone;) | 4 0  / 5 0  | 0.0061 |

Per-run files: regression/loop31-reg-001/<run>.txt. Closing reset: loop31-reg-001-99-final.
