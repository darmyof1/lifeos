# Regression suite loop3-reg-001 (2026-10-27 21:49 AST)

Runs: 1 2 3 4 5 6 7. Pass 5, fail 2. Total cost 0.0455 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-reg-001-01 | bad-sleep-reschedule | FAIL | 6 pass, 4 fail (fail: numstat after the job has no removed lines (missing);sessions_send checker: all checks passed;numstat 5 0 then 6 0;Google shows busy at 10-29 07:00;) | 5 0  /  | 0.0107 |
| loop3-reg-001-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0060 |
| loop3-reg-001-03 | D2 delete (CEO question, approval) | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0064 |
| loop3-reg-001-04 | D3 delete asked by a chief | PASS | 7 pass, 0 fail | 4 0  / 4 0  | 0.0015 |
| loop3-reg-001-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0088 |
| loop3-reg-001-06 | overlap | FAIL | 8 pass, 1 fail (fail: the nearest free slot (08:00) was offered;) | 5 0  / 6 0  | 0.0078 |
| loop3-reg-001-07 | privacy request | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0043 |

Per-run files: regression/loop3-reg-001/<run>.txt. Closing reset: loop3-reg-001-99-final.
