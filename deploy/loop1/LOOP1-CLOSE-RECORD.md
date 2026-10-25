# Loop 1 close record

Date: 2026-10-25
Scenario: closed (APR-0069).
Loop 1: awaiting the CEO's sign-off. Signing off closes Loop 1 and ends the cloud-only exception (APR-0052, ADR-0018); after that the suspended entries apply again unless a new APR entry changes them. The exception expires on 2026-11-15 in any case.
Based on: the VM agent's draft (2026-10-25), corrected against the repo, the gateway logs and the run evidence.

## 1. What Loop 1 set out to prove
Four agents (COO, CHO, CoS, CFO) on openai/gpt-6-luna through OpenClaw can hand work to each other, keep the calendar journal append-only, and report back to the CEO in Slack, on synthetic data only (APR-0052, ADR-0018).

## 2. What passed
- Runtime: OpenClaw 2026.10.5, runtime pinned to openclaw (APR-0060), memory search and dreaming off (APR-0061), cron off.
- Slack: one app per agent (APR-0062, SPK-10), socket mode, one channel per agent with a users list holding only the CEO. That list also authorizes "@<agent> /new" (guides/loop1-baseline.md section 7.10). The CEO may address any agent (APR-0063).
- Hand-offs: COO to CHO to CoS and back, with append-only journal writes (APR-0054, APR-0057).
- Scenario bad-sleep-reschedule, criteria 1 to 5:
  - CLI: runs 003 to 005 passed in a row; run 006 passed with a gateway restart in the middle.
  - Slack: run 019 passed cleanly under instruction set v1.6 (one run per agent, the COO named the CHO and the CoS, numstat 2 0, no late reply, no FAILURE note). Runs 015, 016 and 017 passed on content.

## 3. Instruction sets
| Set | Approval | What it fixed |
|---|---|---|
| v1.2 | APR-0058 | Event IDs and append-only journal lines |
| v1.3 | APR-0064 | Early replies in Slack; one line per agent in its own channel |
| v1.4 | APR-0065 | Stale "pending" answers; wait for the result and answer once |
| v1.5 | APR-0066 | The COO puts the whole task in its hand-off and resends once |
| v1.6 | APR-0067 | The CoS reports an acknowledgement error as delivered, not FAILURE |

## 4. Problems found and how they ended
- First-contact miss (P-34): closed by v1.5 (APR-0066).
- SESSION_WORK_START_CHANGED (P-35): closed (APR-0068). It is a retryable race in OpenClaw's session ingress. No message was dropped in the logs for 2026-10-24 and 2026-10-25. Reopen if a session-start-conflict-retry-limit line appears.
- Agent memory survives a git state reset and a one-line compaction (run 014). Rule: never reuse a run ID.
- Run 018: the CoS ran twice (its first run took no action) and the COO named only the CHO. No duplicate write. Cause of the second CoS run not found.
- The COO's answer sometimes names only the CHO (runs 015 and 018). Run 019 named both. No rule change.
- Since run 017 the CHO treats the sleep report as context and logs only the move. The pass criteria do not require the sleep entry.

## 5. Deferred, with reasons
| Item | Decision | Reason |
|---|---|---|
| Criterion 6, cost per run | Deferred by the CEO (APR-0069) | The usage page lags by 5 to 20 minutes, so per-run readings were unreliable. The OpenAI project spend limit (P-31) stays in place. |
| SPK-03, Code Mode and the Docker sandbox | Deferred by the CEO (APR-0070) | No Docker isolation is planned for a while. Loop 1 file, shell and transcript checks passed. |
| P-36, 04:00 daily reset check | Pending; the CEO asked not to raise it for now | Needs the first inbound message after 04:00 and a session ID comparison (method in guides/loop1-baseline.md section 7.7). |

## 6. Cost
- Ceiling per run: 0.05 USD (APR-0056).
- Measured: about 0.047 USD for loop1-scn-007 (Slack, with retries); at most about 0.020 USD for loop1-scn-010.
- Runs 011 to 019: not measured (deferred by the CEO).

## 7. Open items for Loop 2
- P-26: Slack files:read scope (deferred).
- P-28: calendar journal and Google Calendar.
- P-31: cost hard stop (the kill switch is not built).
- P-32: memory design before Loop 2.
- P-37: COO SQLite maintenance warning about 2 seconds after each scenario post (runs 018 and 019); no visible effect so far.

## 8. Not yet in the repo
- The health check update made on the VM by the VM agent (it reported 41 PASS, 0 FAIL). deploy/loop1/health-check.py in the repo is the older version. Bring the VM patch in through a fix script.

## 9. CEO housekeeping on the Mac
- Delete ~/Downloads/spk04-transfer (it holds old secrets).
- Delete old copies of health-check.py and the upgrade and fix scripts in ~/Downloads.
- Keep the VM handoff archives (loop1-claude-handoff.tar.gz) out of the repo: their logs contain Slack IDs.

## 10. Sign-off
Loop 1 closed by the CEO: not yet.
