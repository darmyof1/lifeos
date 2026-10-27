# Scenario: a CFO calendar entry (Loop 2)

Rules: APR-0034 and APR-0035 (title domain CFO), APR-0086 (CFO entries are high privacy by default), APR-0044 (a chief's add goes straight to the CoS), APR-0030.
Run: loop2-scn-015. Instructions v1.9.1 / v1.9.

## Input (to the COO, CLI route)
    openclaw agent --agent coo --session-id <run ID>-coo --timeout 300 -m "Loop 2 scenario run, run ID <run ID>. I am the CEO. Put a bill-payment reminder on the calendar on 2026-10-29, 09:00 to 09:30 (synthetic data: Alex Test electricity bill). Route this to the CFO, which owns finance. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs."

## Expected
1. The COO routes to the CFO; the CFO asks the CoS (privacy=high in the message); one CFO event ID.
2. The CoS appends one written line, title domain CFO, privacy=high. 3. The job creates a busy event (created (busy)).

## Result 2026-10-26 (VM): PARTIAL
- Passes: title CFO - Pay Electricity Bill - 10292026-0001, privacy=high, one written line, job "created (busy)" at 10-29 09:00, numstat 4 0 then 5 0, header unchanged.
- Differs: the CFO cannot send to the CoS (config send list of the CFO is only the COO; same rule that refuses CFO to CHO in the health check). The CFO sent a FAILURE to the COO ("I don't have calendar access, can only message the COO"). The COO then wrote to the CoS directly; the line says requested by CEO (not CFO); the event ID is loop2-scn-015-cos-01 (a CoS ID, not a CFO ID).
- Both the CFO's and the CoS's sends to the COO returned SESSION_WORK_START_CHANGED with sentBeforeError true (known, P-35).
- The sessions_send checker is built for the CHO and was skipped.
- Cost: about 0.004 USD.

## Result 2026-10-26 (handover 4, v1.10): PASS (loop2-scn-022)
The CFO called the CoS itself (sessions_send agent:cos:main, followup, timeoutSeconds 120, ok), event ID loop2-scn-022-cfo-01, title CFO - Electricity Bill Payment - 10292026-0001, requested by CFO, privacy=high; the job created the busy event. The CFO's send list is now coo and cos (ops/cfo-send-list-diff-2026-10-26.txt).
