# Scenario catalogue (draft, P-19)

Status: draft. Nothing here is approved until P-19 is answered.
Purpose: each row names a situation the system must handle, the behavior it should have, and how to tell it passes. A row that cites an approval is decided. A row marked "Decision needed" has no approved behavior yet.
Pass criterion: a test or a check that can fail. A row without one is not finished.

| ID | Situation | Expected behavior | Pass criterion | Basis | Status |
|---|---|---|---|---|---|
| S-01 | The local triage model is not running. | No request reaches a cloud model. The request is held and the owner is told. | A high-privacy request never reaches a cloud adapter; the owner receives a notice. | APR-0001, APR-0007 | Decision needed: how the owner is told |
| S-02 | A critical-complexity request has high privacy. | Stays local. Override only by explicit CEO confirmation, which is logged. | No cloud call in the log; an override record exists only if one was used. | APR-0007, ADR-0003 | Decided |
| S-03 | Triage is unsure about privacy. | Treated as high privacy. | An unsure label routes to the local path. | ADR-0003 consequences (marked "to confirm") | Decision needed: confirm this rule |
| S-04 | A prompt tells the model to ignore privacy. | The gate result does not change. | The same request gives the same route with and without the instruction. | ADR-0003 | Decided. Test not written (gate.py empty). |
| S-05 | Cloud budget or API key is exhausted. | Local fallback for requests that allow it. No silent move to a more expensive tier. | No cloud call after the limit; a log entry records the fallback. | ADR-0006, APR-0018, APR-0021 | Decision needed: exact fallback |
| S-06 | Google Calendar cannot be reached. | The CoS keeps the event pending and reports it. Nothing is written partially. | Retry happens; no duplicate event; no details leave the machine. | APR-0030, APR-0031 | Decision needed: retry policy |
| S-07 | The Google token is revoked. | Calendar writes stop. The owner is told to re-run init. | No writes while revoked; a notice is sent. | APR-0041, guides/calendar-gcalcli.md | Decision needed: how the notice is sent |
| S-08 | Two events are booked for the same slot. | The CoS decides (roster: CoS resolves conflicts). The decision is logged. | One event kept or both flagged; a log entry exists. | Manifest section 2.2 (CoS resolves department conflicts) | Decision needed: rule for same-slot conflicts |
| S-09 | Two events on the same date get the same counter. | The second create is refused, and the counter moves on. | No two events on one date share a number. | APR-0034, APR-0035 | Decided. Check not written. |
| S-10 | A high-privacy event is created. | Google shows "busy" only. Details stay local. | Google holds title, start, end, and busy status only. | APR-0032 | Decided |
| S-11 | The CISO raises a P1 security event. | It goes straight to the CEO, bypassing the COO. | The CEO receives it; the COO is not in the path. | APR-0008, ADR-0007 | Decided. Whether the COO is copied: not stated. |
| S-12 | A COO plan is vetoed by the CSTO. | The plan stops until the CEO decides. | Nothing runs while the veto stands. | ADR-0002 (proposed, P-18) | Decision needed: P-18 |
| S-13 | A model's digest differs from the pinned digest. | That alias refuses to run. | Startup check fails for the mismatched alias. | APR-0027 | Decided. Check not written. |
| S-14 | A roster entry has no agent folder. | The agent does not start while its folder is missing. | The start check is not written yet. | APR-0039 | Decision needed: how the owner is told |
| S-15 | The VM is lost. | Rebuild from repo, seed, and archive. | A restore drill passes. | ops/recovery/host-loss.md (empty), APR-0010, SPK-07 (not run) | Decision needed: restore procedure |
| S-16 | The seed is missing at Genesis. | Genesis stops before any agent starts. | No partial agent workspace exists. | APR-0005, APR-0022 | Decided for the seed set. Stop rule: decision needed. |
| S-17 | Genesis is interrupted halfway. | Resume from the last completed step. | A restart creates no duplicate workspace. | bootstrap/genesis-runbook.md | Decision needed |
| S-18 | An append-only log is corrupted. | The projection is rebuilt from the log and the last snapshot. | The rebuilt state matches the snapshot. | APR-0013, ADR-0011 (empty) | Decided as a rule. ADR-0011 not reviewed for this row. |
| S-19 | A request arrives during quiet hours. | Non-urgent requests wait until the quiet hours end. P1 is not deferred. | A deferral is logged; P1 is delivered at once. | APR-0015, APR-0008 | Decision needed: what counts as urgent |
| S-20 | A local archive write fails (Phase 1). | The write stops and the owner is alerted. No partial archive is kept. | The archive verify step fails closed. | APR-0010 | Decision needed: alert channel |
| S-21 | The owner opens the dashboard from the internet. | Access is allowed and protected. Method decided later. | Not applicable until designed. | P-17 | Pending P-17 |

## Decisions needed (for P-19)
S-01 how the owner is told; S-03 the unsure-privacy rule; S-05 fallback; S-06 retry; S-07 notice; S-08 same-slot rule; S-12 tie-break (P-18); S-14 block or warn; S-15 restore procedure; S-16 Genesis stop rule; S-17 resume rule; S-19 what is urgent; S-20 alert channel.
