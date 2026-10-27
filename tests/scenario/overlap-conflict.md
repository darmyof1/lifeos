# Scenario: overlapping entries and the job's conflict status (Loop 2)

Rules: S-08 (two events in the same slot: the CoS decides, the decision is logged; one kept or both flagged), APR-0028 (CoS checks conflicts across domains), APR-0077 (conflict status), APR-0034.
Runs: loop2-scn-016 (agents, overlap), by hand (job, conflict status; fake journal ~/loop1/gcal-sync-d).

## D1 input (to the COO, CLI route)
    openclaw agent --agent coo --session-id <run ID>-coo --timeout 300 -m "Loop 2 scenario run, run ID <run ID>. I am the CEO. Add a dentist appointment (synthetic: Alex Test) on 2026-10-28, 07:30 to 08:30. Route this to the CHO, which owns health. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs."
The seed workout is 2026-10-28 07:00 to 08:00, so the new entry overlaps by 30 minutes.

## D1 expected (S-08)
The CoS decides (keep one or flag both) and the decision is logged (a journal line or a log entry exists).

## D1 result (loop2-scn-016): PARTIAL
- The CoS refused to add the entry, sent a FAILURE to the COO, and wrote nothing in the journal. The CHO also sent a FAILURE to the COO. The COO told the CEO: no appointment added, conflict with the workout, event ID loop2-scn-016-cho-01.
- Checker all passed (one CHO call, followup, ok). numstat 3 0 (seed lines only), header unchanged.
- Gap: the decision is only in the chat and the trajectory, not in the journal; S-08 asks for a log entry. The job does not detect time overlaps at all (it only compares titles).
- Cost: about 0.003 USD.

## D2: the job's conflict status (by hand, test calendar, fake data)
1. Journal ~/loop1/gcal-sync-d/journal.md, job with --journal and --state-dir: written CHO - Conflict test - 10292026-9801 at 12:00 to 12:30 (d1-01): created.
2. Appended the same title at 13:00 to 13:30 (d2-01): the job appended one conflict line (reason=an event with this title exists in Google at another time) and touched nothing in Google.
3. A second run added nothing (a conflict is not retried).
Result: PASS. Cleanup: the event was deleted with --title and the approval note.
