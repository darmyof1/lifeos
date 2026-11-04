# Success metrics (proposed, not decided)

Status: draft proposal, written 2026-11-01 under APR-0112. Every threshold below is "proposed, not decided"; the CEO decides. Baselines come from real run files (137 regression runs in 47 single- or multi-scenario suites, 2026-10-27 to 2026-11-01, files in ~/handover/regression on the VM and in the handover packages) and from the handover reports. Synthetic data only.

## Metrics
| # | Metric | Baseline today | Proposed threshold (not decided) |
|---|---|---|---|
| 1 | Scenario pass rate, four-agent set (per scenario, last 10 runs) | See table below | Each scenario at least 9 of 10; D3 judged by metric 5 and 6 as well |
| 2 | Cost per run and per day | Mean 0.0064 USD per run (n 137), highest 0.0167; Handover 20 day about 0.09 USD; Handover 21 day about 0.03 USD | Under 0.05 USD per run and 1 USD per day (the limits already in force) |
| 3 | Turns per run (all agents together) | Mean 13.3 (n 116 runs with metrics) | Report it; flag a 50 percent rise over the 10-run mean |
| 4 | Delete-gate refusals versus deletes | Refusals: 11 runs where an agent wrote a `deleted` line and the job skipped it ("GATE held"). Deletes after a CEO approval: 5 live Slack approvals so far (the used-approvals file holds 5 entries) | Every delete has a pending line and a CEO ledger approval before it; refusals are logged, not hidden |
| 5 | Wrong deletes (a Google event removed without a CEO approval) | 0 since the gate went on (APR-0101). Before it: 2 of 6 four-agent runs in Handover 10 (D3) | 0, always. One wrong delete stops the work until the cause is found |
| 6 | Agent-written `deleted` lines (the D3 fault) | Of 19 runs that printed a gate verdict, 11 had an agent-written `deleted` line that the job skipped; D3 passed 2 of 5 since Handover 18 | Falling trend; the job's refusal must stay 100 percent |
| 7 | Time to restore | Kill switch: stop 1.5 s, restore 5.0 s plus about 20 s until the gateway answers. Config and workspaces from an encrypted archive: 1.5 s for 259 files, all equal. Full state: not timed | Kill switch under 1 minute; restore drill every quarter; full-state restore time measured once |
| 8 | Gateway uptime and restarts | Gateway up from 10-29 07:43 to 11-01 05:11 (69 h), then two planned restarts on 11-01 (the v1.10.7 install; the kill switch drill) | Restarts only when planned and written in the report; one gateway always |
| 9 | Reset proof | The 04:00 reset was proven for the four main sessions (Handover 17) and for the four Slack channel sessions (Handover 18); the 05:00 reset report runs daily | Report reads "1 process (OK)" and shows resets every day; a missed reset is an incident |
| 10 | Stale-memory first replies (the COO answers "already handled" or "already approved" from old memory) | 3 of 5 first requests in a Slack channel session that had not been compacted (Handover 19 step a; Handover 21 steps a and a2). The 2 correct ones followed a compaction | 0 of 10. Needs a decision on how the channel session is cleared (a proposal, not made here) |
| 11 | Acknowledgement-error rate (P-35, content still delivered) | The suite checker noted it in 9 of 137 run files; the replies mentioned it in 5 of the 10 Handover 20 runs | Track; not a failure by itself; below 1 in 5 runs |
| 12 | Health check | PASS 73, WARN 0, FAIL 0 (2026-11-01) | No FAIL; WARN explained in the report |

### Baseline for metric 1 (pass of all criteria of a run)
| Scenario | Before Handover 18 | Since Handover 18 (post, cron, Handover 20 and 21 suites) |
|---|---|---|
| 1 bad-sleep reschedule | 11 of 15 | not run |
| 2 D1 (delete asked by the CEO) | 17 of 18 | 4 of 4 |
| 3 D2 (question, then approval) | 13 of 18 | 9 of 9 |
| 4 D3 (delete asked by a chief) | 9 of 18 | 2 of 5 (the failures are the agent-written `deleted` line; the job skipped each one) |
| 5 CFO entry | 13 of 15 | not run |
| 6 overlap | 10 of 15 | 5 of 5 |
| 7 privacy request | 12 of 15 | not run |
The instruction sets changed between these (v1.10.1 to v1.10.7), so the two columns are not the same system.

## Health feed (design only; nothing is connected)
One real feed, health, would come in this way. No real data and no connection is made by this document.
| Item | Design |
|---|---|
| Source | One export the CEO chooses (for example a weekly file from a wearable app), delivered by the CEO; no live API at first |
| Fields | Date, sleep hours, resting heart rate, steps, workout minutes. Nothing with a name, an address or a free-text note |
| Privacy level | high (health). The privacy gate must treat it as high and keep it local |
| Who may read | The CHO (owner of health), the COO only as a summary with no raw numbers; the CEO |
| Where it is stored | A file in the CHO workspace on the VM, mode 600, inside the encrypted backup; never in the repo, never in Slack, never in a report |
| How the gate treats it | A request that contains it is labelled high at triage and is denied for cloud models by the gate; only a local model may read it. Today there is no usable local model on this VM (SPK-06), so the CHO could store it but not analyse it with an LLM |
| Retention | 90 days raw, then weekly summaries only; deletion by the CEO's word |
| Test first | Synthetic file of the same shape; the same regression suite |
Real data needs the CEO's separate yes. Preconditions, all four: (1) the privacy gate wired into the path to every model call and tested live (today it is not wired); (2) the kill switch drilled (done once on 2026-11-01); (3) the restore drilled for the full state, not only the config and workspaces; (4) the identity-access contract accepted by the CEO (design/identity-and-access.md, draft).
