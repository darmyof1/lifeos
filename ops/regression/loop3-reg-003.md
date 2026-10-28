# Regression suite loop3-reg-003 (2026-10-27 22:56 AST)

Runs: 1 2 3 4 5 6 7. Pass 7, fail 0. Total cost 0.0428 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-reg-003-01 | bad-sleep-reschedule | PASS | 10 pass, 0 fail | 5 0  / 6 0  | 0.0057 |
| loop3-reg-003-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0051 |
| loop3-reg-003-03 | D2 delete (CEO question, approval) | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0056 |
| loop3-reg-003-04 | D3 delete asked by a chief | PASS | 7 pass, 0 fail | 4 0  / 4 0  | 0.0021 |
| loop3-reg-003-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0056 |
| loop3-reg-003-06 | overlap | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0116 |
| loop3-reg-003-07 | privacy request | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0071 |

Per-run files: regression/loop3-reg-003/<run>.txt. Closing reset: loop3-reg-003-99-final.
