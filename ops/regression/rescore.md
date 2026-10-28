# Re-score of loop3-reg-001 to -003: old rule against the APR-0099 ack rule

Old rule = the stored result (any checker failure fails the run and stops the job). New rule = an acknowledgement error is information, not a failure; criteria that failed only because the old runner then did not run the job are listed as not scorable (the job never ran, so the outcome is unknown); every other failure stays. The old result files are unchanged.

| run | scenario | old rule | new rule | failures that stay | not scorable (job did not run) | info |
|---|---|---|---|---|---|---|
| loop3-reg-001-01 | bad-sleep-reschedule | FAIL (6 pass, 4 fail) | PASS (on the scorable criteria) | none | numstat after the job has no removed lines (missing); numstat 5 0 then 6 0; Google shows busy at 10-29 07:00 | ack error seen (checker line) |
| loop3-reg-001-02 | D1 delete (CEO instruction) | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-001-03 | D2 delete (CEO question, approval) | PASS (9 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-001-04 | D3 delete asked by a chief | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-001-05 | CFO entry | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-001-06 | overlap | FAIL (8 pass, 1 fail) | FAIL | the nearest free slot (08:00) was offered | none | none |
| loop3-reg-001-07 | privacy request | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-002-01 | bad-sleep-reschedule | FAIL (6 pass, 4 fail) | PASS (on the scorable criteria) | none | numstat after the job has no removed lines (missing); numstat 5 0 then 6 0; Google shows busy at 10-29 07:00 | ack error seen (checker line) |
| loop3-reg-002-02 | D1 delete (CEO instruction) | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-002-03 | D2 delete (CEO question, approval) | FAIL (8 pass, 1 fail) | FAIL | both delete lines: seed-3, requested by CEO, empty detail | none | none |
| loop3-reg-002-04 | D3 delete asked by a chief | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-002-05 | CFO entry | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-002-06 | overlap | PASS (9 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-002-07 | privacy request | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-003-01 | bad-sleep-reschedule | PASS (10 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-003-02 | D1 delete (CEO instruction) | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-003-03 | D2 delete (CEO question, approval) | PASS (9 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-003-04 | D3 delete asked by a chief | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-003-05 | CFO entry | PASS (7 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-003-06 | overlap | PASS (9 pass, 0 fail) | PASS | none | none | none |
| loop3-reg-003-07 | privacy request | PASS (7 pass, 0 fail) | PASS | none | none | none |

loop3-reg-001: old rule 5 pass of 7; new rule 6 pass of 7.

loop3-reg-002: old rule 5 pass of 7; new rule 6 pass of 7.

loop3-reg-003: old rule 7 pass of 7; new rule 7 pass of 7.
