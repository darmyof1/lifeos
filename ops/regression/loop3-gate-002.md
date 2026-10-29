# Regression suite loop3-gate-002 (2026-10-28 19:20 AST)

Runs: 1 2 3 4 5 6 7. Pass 5, fail 2. Total cost 0.0341 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-gate-002-01 | bad-sleep-reschedule | PASS | 10 pass, 0 fail | 5 0  / 6 0  | 0.0068 |
| loop3-gate-002-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0040 |
| loop3-gate-002-03 | D2 delete (CEO question, approval) | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0043 |
| loop3-gate-002-04 | D3 delete asked by a chief | FAIL | 6 pass, 1 fail (fail: only a pending line, no deleted line;) | 5 0  / 5 0  | 0.0025 |
| loop3-gate-002-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0040 |
| loop3-gate-002-06 | overlap | FAIL | 8 pass, 1 fail (fail: one conflict line with reason=overlaps;) | 6 0  / 7 0  | 0.0077 |
| loop3-gate-002-07 | privacy request | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0048 |

Per-run files: regression/loop3-gate-002/<run>.txt. Closing reset: loop3-gate-002-99-final.
