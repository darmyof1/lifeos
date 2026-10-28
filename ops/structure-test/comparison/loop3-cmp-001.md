# Regression suite loop3-cmp-001 (2026-10-27 23:54 AST)

Runs: 1 2 3 4 5 6 7. Pass 4, fail 3. Total cost 0.0404 USD (measured by exporting the COO, CHO, CoS and CFO sessions).

| run | scenario | result | criteria (pass/fail) | numstat before / after the job | cost USD |
|---|---|---|---|---|---|
| loop3-cmp-001-01 | bad-sleep-reschedule | FAIL | 9 pass, 1 fail (fail: COO reply names the CHO and the CoS and gives the event ID;) | 5 0  / 6 0  | 0.0075 |
| loop3-cmp-001-02 | D1 delete (CEO instruction) | PASS | 7 pass, 0 fail | 5 0  / 6 0  | 0.0037 |
| loop3-cmp-001-03 | D2 delete (CEO question, approval) | PASS | 9 pass, 0 fail | 5 0  / 6 0  | 0.0047 |
| loop3-cmp-001-04 | D3 delete asked by a chief | FAIL | 4 pass, 3 fail (fail: only a pending line, no deleted line;the reply tells the CEO it waits for approval;the Google event is still there;) | 6 0  / 7 0  | 0.0057 |
| loop3-cmp-001-05 | CFO entry | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0052 |
| loop3-cmp-001-06 | overlap | FAIL | 8 pass, 1 fail (fail: the nearest free slot (08:00) was offered;) | 5 0  / 6 0  | 0.0084 |
| loop3-cmp-001-07 | privacy request | PASS | 7 pass, 0 fail | 4 0  / 5 0  | 0.0052 |

Per-run files: regression/loop3-cmp-001/<run>.txt. Closing reset: loop3-cmp-001-99-final.
