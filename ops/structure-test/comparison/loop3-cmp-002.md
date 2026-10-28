# Regression suite loop3-cmp-002 (2026-10-28 00:40 AST)

Runs: 1 2 3 4 5 6 7. Pass 7, fail 0. Total cost 0.0409 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-cmp-002-01 | bad-sleep-reschedule | PASS | 10 pass, 0 fail | 5 0  / 6 0  | 0.0088 |
| loop3-cmp-002-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0046 |
| loop3-cmp-002-03 | D2 delete (CEO question, approval) | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0062 |
| loop3-cmp-002-04 | D3 delete asked by a chief | PASS | 7 pass, 0 fail | 4 0  / 4 0  | 0.0016 |
| loop3-cmp-002-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0053 |
| loop3-cmp-002-06 | overlap | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0088 |
| loop3-cmp-002-07 | privacy request | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0056 |

Per-run files: regression/loop3-cmp-002/<run>.txt. Closing reset: loop3-cmp-002-99-final.
