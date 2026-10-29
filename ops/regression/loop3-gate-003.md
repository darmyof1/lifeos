# Regression suite loop3-gate-003 (2026-10-28 19:54 AST)

Runs: 1 2 3 4 5 6 7. Pass 4, fail 3. Total cost 0.0389 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-gate-003-01 | bad-sleep-reschedule | PASS | 10 pass, 0 fail | 5 0  / 6 0  | 0.0055 |
| loop3-gate-003-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0039 |
| loop3-gate-003-03 | D2 delete (CEO question, approval) | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0064 |
| loop3-gate-003-04 | D3 delete asked by a chief | FAIL | 5 pass, 3 fail (fail: only a pending line, no deleted line;the Google event is still there;gate: an agent-written deleted line reached Google (the event is gone);) | 5 0  / 5 0  | 0.0031 |
| loop3-gate-003-05 | CFO entry | FAIL | 6 pass, 1 fail (fail: Google shows busy at 10-29 09:00 (job created a busy event);) | 2 0  / 2 0  | 0.0060 |
| loop3-gate-003-06 | overlap | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0089 |
| loop3-gate-003-07 | privacy request | FAIL | 4 pass, 3 fail (fail: numstat before the job has no removed lines (missing);new line for the 10-30 entry with privacy=high (exactly one);Google shows busy at 10-30 07:00 and the title is gone;) |   / 3 0  | 0.0051 |

Per-run files: regression/loop3-gate-003/<run>.txt. Closing reset: loop3-gate-003-99-final.
