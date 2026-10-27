# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-08 (APR-0040), P-13 (APR-0041), P-18 (APR-0042), P-19 (APR-0043), calendar routing (APR-0044), Slack exemption (APR-0045), P-20 (APR-0046), P-21 (APR-0047), P-22 (APR-0048), P-24 (APR-0049), P-23 (APR-0050), P-25 (APR-0051), P-27 (APR-0062), P-30 (APR-0060), P-33 (APR-0063), P-29 (solved by a finding, guides/loop1-baseline.md section 7.10), P-34 (APR-0066), P-35 (APR-0068), P-38 (APR-0076), P-28 (APR-0080), P-39 (APR-0082), P-31 (APR-0083), P-37 (APR-0084), P-32 (APR-0085).

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file), SPK-09 (see file). Partial: SPK-05 (see file).
Several need the OpenClaw runtime running on the VM. Run them when the system is up.
Runbook: guides/vm-spike-runbook.md. Order: SPK-07, SPK-01, SPK-02, SPK-03, SPK-04. SPK-07 done (research/spikes/SPK-07-gpg-restore-drill.md). SPK-01 done for the mechanism; limits recorded in its file (research/spikes/SPK-01-egress-interception.md). SPK-02 done: state honours the override (setup, status, gateway); logs do not (research/spikes/SPK-02-openclaw-state-dir.md). SPK-03 partial: agents and workspaces set up; isolation-off canary not obtained on this VM; isolation-on deferred (research/spikes/SPK-03-agent-isolation.md). SPK-04 Part A done: two Slack identities; each agent posts as its bound account (research/spikes/SPK-04-slack-multi-identity.md). Part B and the leakage check open. Cleanup verified 2026-10-19 (top-level tokens removed; gateway token saved). Model: utility and main set to openai/gpt-6-luna; served and billed gpt-6-luna after the change. Billing re-check 2026-10-20 (life-os chip set): gpt-6-luna about $0.04 for the day, gpt-5_6-luna $0. Billing confirmed for the test. Channel allowlist, event subscription and spk04-b binding verified 2026-10-20. Part B (local model) paused: /new refused as control-command-unauthorized; a thread turn used openai/gpt-6-luna; Tool calling checked 2026-10-21 on AWS with qwen35-32k: a direct call and one OpenClaw call worked after tools.toolSearch was turned off (guides/local-model-setup.md, section 4). Part B closed for the test. Open: /new refused; image downloads need files:read (not added). Send back the results; the spike files are filled in after each run.

## P-17 - Dashboard or website for the owner (future)
Owner: CMO (roster: "produces the weekly life dashboard"). Proposed, not yet approved: the CKO supplies the memory data behind it.
Decision made: the owner must be able to reach it from the internet. It will be heavily protected. How it is protected is decided later.
Not now: no design until the agent loop is proven.
Needs: nothing today. A design item is opened when the loop is proven.

## P-26 - Slack files:read scope (deferred)
Proposed: do not add files:read. Attachments would reach the cloud model with no privacy gate (ADR-0003). Revisit after the privacy gate exists.
CEO 2026-10-25: defer (SD-008). Revisit after the privacy gate exists.
Needs: nothing until the privacy gate exists.

## P-36 - 04:00 daily reset check (in progress, APR-0090)
History read 2026-10-26 (APR-0091): one daily reset confirmed on the COO channel session (10-24 18:41); a reset is a marker inside a channel session, not a new session ID; main sessions get new IDs but the prep compactions hide the daily reset there; the CHO, CoS and CFO channel sessions show no marker yet. The 05:00 AST report (cron, posts to the COO channel and ~/loop1/reset-check/report.log) runs from 2026-10-27.
Status: in progress. The CEO lifted the "not to be raised" request on 2026-10-26: Claude Code looks at past nights first, then a 05:00 AST cron script posts a read-only report to Slack. A lazy reset (applied at the first message after 04:00) is expected.
Needs: after the first inbound message past 04:00 AST, record the session IDs of the five main sessions and compare them with the list captured at 00:54 on 2026-10-25.
Method: section 7.7 of guides/loop1-baseline.md.

## P-40 - Calendar: what must be decided before real data
Left over when P-28 was closed (APR-0080). Loop 2 runs on synthetic data (APR-0073); none of this is needed for that.
1. Privacy mark: done. Decided (APR-0086), built (APR-0088), applied on the VM (v1.9, then v1.9.1 after run 009, APR-0089) and verified by runs 011 and 012 (busy in the test calendar).
2. Real calendar: the test on the CEO's primary calendar PASSED (2026-10-26, Claude Code, APR-0090; ops/handover-2026-10-26-claude-code-report-2.md): create, move in place, raise privacy to busy (mandated title gone), delete by key; 5 non-LifeOS events before and after, no test event left, no personal title shown or saved. The cron stays on the test calendar; switching it to the real calendar is the CEO's decision and is NOT made. The cron pushes to the Google test calendar. Moving it to the real calendar is a one-line change in ~/loop1/gcal-sync/env on the VM, after item 1 passes: first a read-only look at the real calendar, then one fake event created and removed, then the change. Needs the CEO's go.
3. Monthly archive job (APR-0072): deferred by the CEO (APR-0090). Build it when the journal reaches about 1,000 lines (it is under 100 now).
4. Busy block in the Google Calendar app: done (APR-0087).
Needs: item 2 (the CEO's go for the real calendar) before any real data enters Loop 2.

## P-41 - Memory beyond the state files (deferred from P-32)
Open when the COO prompt grows (it was about 35,000 tokens of 272,000 on a Slack turn) or a second real use appears. Not needed for Loop 2 (APR-0085).
Questions: local embeddings after the local model work (SD-005, ADR-0003); checking state files before answering, which needs a token estimate (SD-006); short COO handoffs (SD-007); how much context the COO builds up when it routes everything and what it must ask the chiefs for instead of keeping. Per-agent token counts per scenario run are still to measure.
Sandbox draft: research/sandbox/2026-10-25-agy/P-32-memory.md.
