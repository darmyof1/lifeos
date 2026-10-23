# Scenario: bad-sleep reschedule (Loop 1)

Rules: APR-0052 (synthetic data), APR-0054 (journal), APR-0056 (cost), APR-0057 (move), APR-0058 (instructions v1.2), ADR-0018.
Runs needed to close: three identical passing runs, plus one run with a gateway restart in the middle.
Status 2026-10-22: both met (runs 3 to 5 passed in a row; run 6 restart and retries passed). Still open: cost per run and the Slack view.

## Setup
- Agents COO, CHO, CoS and CFO with instruction set v1.2 (deploy/loop1/loop1-agent-files.sh).
- Gateway running once: pgrep -af "openclaw.*gateway" | grep -v pgrep | wc -l prints 1.
- Before each run, save the state and reset it to the seed:

      W=~/loop1/workspaces; E=~/loop1/evidence/<date>
      mkdir -p $E
      for a in cho cos cfo; do cp -r $W/$a/state $E/<run ID>-$a; git -C $W/$a checkout -- state/; done

- Use a fresh session id for each run.
- Between runs, cut the four main sessions to one line (synthetic data only; no backup is kept):

      T=$(cat ~/loop1/gateway-token)
      for a in coo cho cos cfo; do openclaw sessions compact "agent:$a:main" --agent $a --max-lines 1 --token "$T"; done


## Input (to the COO)
    openclaw agent --agent coo --session-id <run ID>-coo --timeout 300 -m "Loop 1 scenario run, run ID <run ID>. Alex Test slept 5 hours last night. Move the Wednesday workout on 2026-10-28 to Thursday 2026-10-29, 07:00 to 08:00. Route this to the CHO, which owns health. Wait for the result, then tell me in 3 lines what changed, who changed it, and the event IDs."

## Checks (after 120 seconds)
    tail -n 4 ~/loop1/workspaces/cos/state/calendar-journal.md
    tail -n 2 ~/loop1/workspaces/cho/state/health-plan.md
    git -C ~/loop1/workspaces/cos diff --numstat state/calendar-journal.md

## Pass criteria
1. The COO routes to the CHO. The CHO sends the move to the CoS and never writes the calendar itself (APR-0030, APR-0044).
2. The CHO creates the event ID <run ID>-cho-01 and logs the change in state/health-plan.md (APR-0058).
3. The CoS journal keeps the 10-28 seed line and appends two lines: 10-28 moved and 10-29 written, both with the run ID and event ID (APR-0054, APR-0057).
4. The numstat check prints 2 0: two lines added, none removed.
5. The COO summary names the CHO and the CoS and gives the event ID (APR-0050).
6. The run costs less than 0.05 USD (APR-0056). Not yet measured per run.

## Still to cover
- Cost per run (only a rough estimate so far: 0.15 USD for all tests on 2026-10-22, about 0.01 to 0.02 USD per scenario run).
- What the CEO sees in Slack (after SPK-10).

## Run log
| Run | Date | Instructions | Result | Notes |
|---|---|---|---|---|
| loop1-scn-001 | 2026-10-22 | v1 | Fail | The CHO refused: no event ID was given and no rule said who creates one. Led to v1.1. |
| loop1-scn-002 | 2026-10-22 | v1.1 | Partial | Move done. The CoS edited the 10-28 line in place, so the journal was not append-only. The COO summary named only the CHO. Led to APR-0057 and v1.2. |
| loop1-scn-003 | 2026-10-22 | v1.2 | Pass (criteria 1 to 5) | numstat 2 0; event ID loop1-scn-003-cho-01; the summary named the CHO and the CoS. |
| loop1-scn-004 | 2026-10-22 | v1.2 | Pass (criteria 1 to 5) | Summary listed the entry name as an event ID as well; the real event ID was given. |
| loop1-scn-005 | 2026-10-22 | v1.2 | Pass (criteria 1 to 5) | Third pass in a row. |
| loop1-scn-006 | 2026-10-22 | v1.2 | Pass (restart) | Ctrl-C during the run: the gateway drained for about 60 s and refused the CHO's sends; no change was written (numstat 0 0). Retry with the same run ID wrote one pair (2 0). |
| loop1-scn-006 resend | 2026-10-22 | v1.2 | Pass (duplicate check) | Resending the finished run reported the earlier result; no -cho-02, numstat still 2 0. |

Evidence copies stay on the VM in ~/loop1/evidence/ (synthetic data, not in the repo).
