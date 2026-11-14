# Re-score of two checks (APR-0125), old verdict against new verdict, from the stored result files

| run | scenario | old verdict | new verdict | criteria that changed |
|---|---|---|---|---|
| loop32-reg-001-01 | bad-sleep-reschedule | FAIL (1 fail) | FAIL (1 fail) | none |
| loop32-reg-001-02 | D1 delete (CEO instruction) | PASS (0 fail) | PASS (0 fail) | none |
| loop32-reg-001-03 | D2 delete (CEO question, approval) | FAIL (1 fail) | PASS (0 fail) | reply makes no false Google claim (heuristic): calendar jour: FAIL to PASS |
| loop32-reg-001-04 | D3 delete asked by a chief | PASS (0 fail) | PASS (0 fail) | none |
| loop32-reg-001-05 | CFO entry | FAIL (1 fail) | FAIL (1 fail) | none |
| loop32-reg-001-06 | overlap | FAIL (1 fail) | PASS (0 fail) | Google shows busy at 10-28 08:00 (job created the event): FAIL to PASS |
| loop32-reg-001-07 | privacy request | FAIL (1 fail) | FAIL (1 fail) | none |

Runs: 7. Verdict changed: 2. Stored result line equals the stored criteria: all.
Old checks re-run on the stored data reproduce the stored verdicts: yes, all.
Changes outside the two intended checks: none.
