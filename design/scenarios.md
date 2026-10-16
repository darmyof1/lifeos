# Scenario catalogue (draft, P-19)

Status: approved (APR-0043). S-21 waits on P-17.
Purpose: each row names a situation the system must handle, the behavior it should have, and how to tell it passes. A row that cites an approval is decided. A row marked "Decision needed" has no approved behavior yet.
Pass criterion: a test or a check that can fail. A row without one is not finished.

| ID | Situation | Expected behavior | Pass criterion | Basis | Status |
|---|---|---|---|---|---|
| S-01 | The local triage model is not running. | No request reaches a cloud model. The request is held and the CIO reports it in its Slack channel. | A high-privacy request never reaches a cloud adapter; the CIO's Slack channel receives a notice. | APR-0001, APR-0007, APR-0043 | Decided (APR-0043) |
| S-02 | A critical-complexity request has high privacy. | Stays local. Override only by explicit CEO confirmation, which is logged. | No cloud call in the log; an override record exists only if one was used. | APR-0007, ADR-0003 | Decided |
| S-03 | Triage is unsure about privacy. | Treated as high privacy. | An unsure label routes to the local path. | ADR-0003 consequences (marked "to confirm") | Decided (APR-0043) |
| S-04 | A prompt tells the model to ignore privacy. | The gate result does not change. | The same request gives the same route with and without the instruction. | ADR-0003 | Decided. Test not written (gate.py empty). |
| S-05 | Cloud budget or API key is exhausted. | Local fallback for requests that allow it. No silent move to a more expensive tier. | No cloud call after the limit; a log entry records the fallback. | ADR-0006, APR-0018, APR-0021 | Decided (APR-0043) |
| S-06 | Google Calendar cannot be reached. | The event is kept local and not written to Google. It is retried every 5 minutes until it completes. After 5 failed attempts the problem goes to the COO, who has the CEO check it. Retries continue until it completes. | Retries happen at 5-minute intervals; no partial write; no duplicate event after success; the COO receives the report at attempt 5. | APR-0030, APR-0031, APR-0043 | Decided (APR-0043, changed) |
| S-07 | The Google token is revoked or no longer valid. | Calendar writes stop. This is an alert that must be fixed. The CIO reports it in its Slack channel. Events are held local until the token is fixed. | No calendar write while revoked; the CIO's Slack channel receives the alert. | APR-0041, APR-0043, guides/calendar-gcalcli.md | Decided (APR-0043, changed) |
| S-08 | Two events are booked for the same slot. | The CoS decides (roster: CoS resolves conflicts). The decision is logged. | One event kept or both flagged; a log entry exists. | Manifest section 2.2 (CoS resolves department conflicts) | Decided (APR-0043) |
| S-09 | Two events on the same date get the same counter. | The second create is refused, and the counter moves on. | No two events on one date share a number. | APR-0034, APR-0035 | Decided. Check not written. |
| S-10 | A high-privacy event is created. | Google shows "busy" only. Details stay local. | Google holds title, start, end, and busy status only. | APR-0032 | Decided |
| S-11 | The CISO raises a P1 security event. | It goes straight to the CEO, bypassing the COO. | The CEO receives it; the COO is not in the path. | APR-0008, ADR-0007 | Decided. Whether the COO is copied: not stated. |
| S-12 | A COO plan is vetoed by the CSTO. | The plan stops until the CEO decides. | Nothing runs while the veto stands. | ADR-0002 (APR-0042) | Decided |
| S-13 | A model's digest differs from the pinned digest. | That alias refuses to run. | Startup check fails for the mismatched alias. | APR-0027 | Decided. Check not written. |
| S-14 | A roster entry has no agent folder. | The agent does not start. The CIO reports it in its Slack channel. | The agent does not start while its folder is missing; the CIO's Slack channel receives a notice. | APR-0039, APR-0043 | Decided (APR-0043) |
| S-15 | The VM is lost. | Rebuild from repo, seed, and archive. | A restore drill passes. | ops/recovery/host-loss.md (empty), APR-0010, SPK-07 (not run) | Decided (APR-0043) |
| S-16 | The seed is missing at Genesis. | Genesis stops before any agent starts. | No partial agent workspace exists. | APR-0005, APR-0022 | Decided (APR-0043) |
| S-17 | Genesis is interrupted halfway. | Resume from the last completed step. | A restart creates no duplicate workspace. | bootstrap/genesis-runbook.md | Decided (APR-0043) |
| S-18 | An append-only log is corrupted. | The projection is rebuilt from the log and the last snapshot. | The rebuilt state matches the snapshot. | APR-0013, ADR-0011 (empty) | Decided as a rule. ADR-0011 not reviewed for this row. |
| S-19 | A request arrives during quiet hours. | Non-urgent requests wait until the quiet hours end. P1 is not deferred. | A deferral is logged; P1 is delivered at once. | APR-0015, APR-0008 | Decided (APR-0043) |
| S-20 | A local archive write fails (Phase 1). | The write stops and the CIO reports it in its Slack channel. No partial archive is kept. | The archive verify step fails closed; the CIO's Slack channel receives a notice. | APR-0010, APR-0043 | Decided (APR-0043) |
| S-21 | The owner opens the dashboard from the internet. | Access is allowed and protected. Method decided later. | Not applicable until designed. | P-17 | Pending P-17 |

## Decisions
All rows except S-21 are decided. S-21 waits on P-17. Changes: APR-0043 (S-06, S-07).
