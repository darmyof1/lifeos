# Loop 2 close record (DRAFT, not signed)

Date drafted: 2026-10-26
Status: draft for the CEO. Loop 2 is NOT closed. It closes only when the CEO signs section 9 with a new APR entry in his words.
Scope of Loop 2: APR-0073 (cloud-only on openai/gpt-6-luna, synthetic data only, Google Calendar writes allowed, expiry when Loop 2 closes or on 2026-12-31).
Based on: decisions/APPROVALS.md (APR-0073 to APR-0090), tests/scenario/bad-sleep-reschedule.md (run log), deploy/loop1/STATE.md, guides/calendar-sync-job.md.

## 1. What Loop 2 set out to prove
The same four agents (COO, CHO, CoS, CFO) hand work to each other through Slack, and the CoS journal is pushed to Google Calendar by code (not by a model), append-only, with high-privacy entries shown as busy, on synthetic data.

## 2. What passed
- Slack hand-off, scenario bad-sleep-reschedule: runs loop2-scn-001 to -012 (010 void). Clean passes: 003, 004 (v1.7), 007, 008 (v1.8), 011, 012 (v1.9.1). Each pass: one CHO call to the CoS (followup, ok), no CoS send to the CHO, the COO names the CHO and the CoS with both event IDs, one line in the CoS channel and two in the CHO channel, numstat 5 0 then 6 0 (no deletions), checker all passed.
- Calendar push job (P-28, APR-0077 to APR-0080): scripts/gcal/gcal_sync.py, run every 5 minutes by plain cron on the Google test calendar. Proven on the VM: create, move in place, conflict, delete gate (needs APR-0044 approval), five failed attempts and one alert, revoked login pause, alerts to the COO channel (need the gateway). The agents write the journal; the job moves the Google event.
- High privacy (APR-0079, APR-0086, APR-0088): an entry marked privacy=high is a Google event titled busy with a hidden key; the mandated title never reaches Google; a normal event becomes busy when the entry is marked high; delete by key with approval. The CHO and CFO mark their entries high; the CoS writes the mark. Verified in runs 011 and 012.
- Health plan: the CHO logs a reported health fact with its own event ID (v1.8, APR-0081, APR-0082).

## 3. Instruction sets in Loop 2
| Set | Approval | What it fixed |
|---|---|---|
| v1.7 | APR-0075 | CHO sends to the CoS with exactly one sessions_send call (followup, timeoutSeconds 120, no watch); the CoS answers instead of sending back (P-38, APR-0076) |
| v1.8 | APR-0081 | The CHO logs a health fact with its own event ID (P-39, APR-0082) |
| v1.9 | APR-0086 | Privacy mark: the chief marks it, CHO and CFO entries are high by default |
| v1.9.1 | APR-0089 | The CoS never edits the journal header or an existing line (found in run 009) |

## 4. Problems found and how they ended
- Sessions_send arguments (notify, watch, resume) start no CoS turn: fixed by v1.7 (P-38).
- The sleep fact was logged inconsistently: cause was the COO's wording and an ambiguous setup note; fixed by v1.8 (P-39).
- Run 009: the CoS added a column to the journal header; fixed by v1.9.1. Run 010 was void (CHO compaction failed after a gateway restart; read every compact output).
- P-37 (COO SQLite maintenance warning): one occurrence in runs 001 to 012, no effect, closed (APR-0084).
- Cost control: 5 USD per day kill and 1 USD per day alert, stated done and verified by the CEO (APR-0083); the enforced 5 USD monthly project limit stays.
- Memory: state files are the agents' memory; memory search and dreaming stay off; ADR-0011 written (APR-0085).

- Handover 3 (runs 013 to 017): the delete gate failed (agents skipped the approval step; the COO claimed things it had not checked), the CFO could not reach the CoS, overlaps were refused without a log; privacy on request passed. Decisions APR-0092, instruction set v1.10 (P-42).

## 5. Open before Loop 2 can close
| Item | State |
|---|---|
| P-36, 04:00 daily reset check | History read (one daily reset confirmed); the 05:00 AST report runs from 2026-10-27 and must show the resets of the CHO, CoS and CFO (APR-0091) |
| Gateway kept running without a terminal | Done: systemd user service, restarts after a crash and at boot (APR-0091) |
| P-40 item 2, real calendar | The test on the CEO's primary calendar passed. Moving the cron to the real calendar is a separate CEO decision, not made. |
| Claude Code handover 2 outputs | In the repo: deploy/loop2/vm/ (service unit, reset report script) and the report (ops/) |
| P-42, instruction sets v1.10, v1.10.1 and v1.10.2 | All applied. D1 four passes in a row (027 to 029, 036); D2 4 of 5 (035: the COO skipped the seven-item request); regression passes. Open: the COO approval-request gap (CEO decision). Deletes on in the cron on the test calendar |

## 6. Deferred, with reasons
| Item | Decision | Reason |
|---|---|---|
| P-40 item 3, monthly journal archive job (APR-0072) | Deferred by the CEO (APR-0090) | The journal is under 100 lines; build it near 1,000 |
| P-41, memory beyond the state files | Deferred (APR-0085) | Not needed for Loop 2 |
| P-26, Slack files:read | Deferred | Needs privacy infrastructure that is not built |
| P-09 spikes, P-17 dashboard | Not started | Not part of the Loop 2 scenario |

## 7. Cost
- Per-run ceiling 0.05 USD (APR-0056, Loop 1). Per-run cost was not measured in Loop 2 (APR-0073 deferred it); the daily kill and alert are in place (APR-0083).

## 8. Not yet in the repo
- The 05:00 report cron line and the installed unit live on the VM only; the repo holds copies (deploy/loop2/vm/).
- The unrelated stress-ng cron line on the VM is the CEO's and stays.

## 9. Sign-off
Loop 2 closed by the CEO: NOT YET. To close, the CEO says so in his words and the assistant records a new APR entry that also ends APR-0073 and lists any remaining deferred items.
