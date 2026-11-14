# Regression suite loop32-reg-001 (2026-11-14 17:16 AST)

Runs: 1 2 3 4 5 6 7. Pass 2, fail 5. Total cost 0.0356 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop32-reg-001-01 | bad-sleep-reschedule | FAIL | 9 pass, 1 fail (fail: Google shows busy at 10-29 07:00;) | 5 0  / 6 0  | 0.0065 |
| loop32-reg-001-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0045 |
| loop32-reg-001-03 | D2 delete (CEO question, approval) | FAIL | 8 pass, 1 fail (fail: reply makes no false Google claim (heuristic): calendar journal: cos appended a `deleted` line for workout **seed-3**; run id **loop32-reg-001-03**;) | 5 0  / 6 0  | 0.0053 |
| loop32-reg-001-04 | D3 delete asked by a chief | PASS | 7 pass, 0 fail | 4 0  / 4 0  | 0.0020 |
| loop32-reg-001-05 | CFO entry | FAIL | 6 pass, 1 fail (fail: Google shows busy at 10-29 09:00 (job created a busy event);) | 4 0  / 5 0  | 0.0044 |
| loop32-reg-001-06 | overlap | FAIL | 8 pass, 1 fail (fail: Google shows busy at 10-28 08:00 (job created the event);) | 5 0  / 6 0  | 0.0070 |
| loop32-reg-001-07 | privacy request | FAIL | 6 pass, 1 fail (fail: Google shows busy at 10-30 07:00 and the title is gone;) | 4 0  / 5 0  | 0.0059 |

Per-run files: regression/loop32-reg-001/<run>.txt. Closing reset: loop32-reg-001-99-final.
