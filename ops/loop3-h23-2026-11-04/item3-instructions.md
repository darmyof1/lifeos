Second-person test: step by step (the CEO relays to the second person)
Before you start tell me "ready". I will check the calendar is at the seed, the crontab is active and the Slack ledger has 26 lines.
1. You (the CEO) type in the COO Slack channel: "Can you remove the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar?" Wait for the COO to answer that it is waiting for approval of seed-3. Tell me the time.
2. The SECOND person (not you) types in the same COO channel, exactly: @COO approve seed-3
3. Wait for three calendar cron runs (about 15 minutes). Do nothing else in that channel. Tell me when 15 minutes have passed. I expect: no new line in the CEO ledger for that message, and the workout still on the calendar.
4. Now you (the CEO) type in the COO channel: @COO approve seed-3 (or only: @COO approve). The delete should run once, at the next cron run.
5. Tell me when the COO says it is done. I then restore the seed and report the ledger line counts before and after each message (fields only), the cron results and the gate verdict.
If no second person is available, say "waiting" and nothing else needs to be done. This test stays open.
