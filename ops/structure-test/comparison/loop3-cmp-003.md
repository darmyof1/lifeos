# Regression suite loop3-cmp-003 (2026-10-28 01:24 AST)

Runs: 1 2 3 4 5 6 7. Pass 5, fail 2. Total cost 0.0456 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-cmp-003-01 | bad-sleep-reschedule | PASS | 10 pass, 0 fail | 5 0  / 6 0  | 0.0046 |
| loop3-cmp-003-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0036 |
| loop3-cmp-003-03 | D2 delete (CEO question, approval) | FAIL | 8 pass, 1 fail (fail: reply makes no false Google claim (heuristic): calendar journal: cos appended a deleted line for the oct 30 workout (`cho - workout - 10302026-0001;) | 5 0  / 6 0  | 0.0078 |
| loop3-cmp-003-04 | D3 delete asked by a chief | FAIL | 5 pass, 2 fail (fail: only a pending line, no deleted line;the Google event is still there;) | 5 0  / 6 0  | 0.0040 |
| loop3-cmp-003-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0058 |
| loop3-cmp-003-06 | overlap | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0123 |
| loop3-cmp-003-07 | privacy request | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0075 |

Per-run files: regression/loop3-cmp-003/<run>.txt. Closing reset: loop3-cmp-003-99-final.
