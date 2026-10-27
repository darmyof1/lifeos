# Scenario: the CEO asks for privacy on an existing entry (Loop 2)

Rules: APR-0086 (privacy=high on a new line, never lowered), APR-0079 and APR-0032 (busy in Google), APR-0054.
Run: loop2-scn-014. Instructions v1.9.1 / v1.9.

## Input (to the COO, CLI route)
    openclaw agent --agent coo --session-id <run ID>-coo --timeout 300 -m "Loop 2 scenario run, run ID <run ID>. I am the CEO. Please make the workout on 2026-10-30 (CHO - Workout - 10302026-0001) private. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs."

## Expected (APR-0086)
1. The CoS appends a new line for that entry with privacy=high in the detail column; no existing line is edited; header unchanged.
2. The job (run by hand after the checker) does "made busy" on the entry's Google event.
3. Google shows busy at 2026-10-30 07:00 and the mandated title is gone.
4. Checker (CHO handoff) all passed; numstat no removed lines.
5. The COO reply names who changed it and the event ID.

## Result 2026-10-26 (VM): PASS
- COO routed to the CHO; CHO sent to the CoS once (followup, ok); the CoS appended CHO - Workout - 10302026-0001 | ... | written | loop2-scn-014 | loop2-scn-014-cho-01 | CHO | privacy=high.
- Job: made busy 0e9k54aumipnjt9n8cu85j4fcs; Google then showed busy at 10-30 07:00. numstat 4 0 before the job, 5 0 after. Checker all passed.
- Cleanup: the busy event was deleted with --busy-key loop2-scn-014-cho-01 in the next prep.
- Cost: about 0.003 USD.
