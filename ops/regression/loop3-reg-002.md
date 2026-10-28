# Regression suite loop3-reg-002 (2026-10-27 22:36 AST)

Runs: 1 2 3 4 5 6 7. Pass 5, fail 2. Total cost 0.0424 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-reg-002-01 | bad-sleep-reschedule | FAIL | 6 pass, 4 fail (fail: numstat after the job has no removed lines (missing);sessions_send checker: all checks passed;numstat 5 0 then 6 0;Google shows busy at 10-29 07:00;) | 5 0  /  | 0.0086 |
| loop3-reg-002-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0032 |
| loop3-reg-002-03 | D2 delete (CEO question, approval) | FAIL | 8 pass, 1 fail (fail: both delete lines: seed-3, requested by CEO, empty detail;) | 5 0  / 6 0  | 0.0061 |
| loop3-reg-002-04 | D3 delete asked by a chief | PASS | 7 pass, 0 fail | 4 0  / 4 0  | 0.0014 |
| loop3-reg-002-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0057 |
| loop3-reg-002-06 | overlap | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0091 |
| loop3-reg-002-07 | privacy request | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0083 |

Per-run files: regression/loop3-reg-002/<run>.txt. Closing reset: loop3-reg-002-99-final.
