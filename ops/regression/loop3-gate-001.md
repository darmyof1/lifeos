# Regression suite loop3-gate-001 (2026-10-28 19:02 AST)

Runs: 1 2 3 4 5 6 7. Pass 5, fail 2. Total cost 0.047 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-gate-001-01 | bad-sleep-reschedule | FAIL | 9 pass, 1 fail (fail: COO reply names the CHO and the CoS and gives the event ID;) | 5 0  / 6 0  | 0.0096 |
| loop3-gate-001-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0043 |
| loop3-gate-001-03 | D2 delete (CEO question, approval) | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0092 |
| loop3-gate-001-04 | D3 delete asked by a chief | PASS | 7 pass, 0 fail | 4 0  / 4 0  | 0.0015 |
| loop3-gate-001-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0060 |
| loop3-gate-001-06 | overlap | PASS | 9 pass, 0 fail [ack error seen] | 5 0  / 6 0  | 0.0091 |
| loop3-gate-001-07 | privacy request | FAIL | 5 pass, 2 fail (fail: new line for the 10-30 entry with privacy=high (exactly one);Google shows busy at 10-30 07:00 and the title is gone;) | 3 0  / 3 0  | 0.0073 |

Per-run files: regression/loop3-gate-001/<run>.txt. Closing reset: loop3-gate-001-99-final.
