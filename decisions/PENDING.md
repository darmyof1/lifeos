# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-08 (APR-0040), P-13 (APR-0041), P-18 (APR-0042), P-19 (APR-0043), calendar routing (APR-0044), Slack exemption (APR-0045), P-20 (APR-0046), P-21 (APR-0047), P-22 (APR-0048), P-24 (APR-0049), P-23 (APR-0050), P-25 (APR-0051), P-27 (APR-0062), P-30 (APR-0060), P-33 (APR-0063), P-29 (solved by a finding, guides/loop1-baseline.md section 7.10), P-34 (APR-0066), P-35 (APR-0068), P-38 (APR-0076), P-28 (APR-0080).

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

## P-31 - Cost hard stop (APR-0056)
Seen 2026-10-22: the OpenAI project page shows the 5 USD monthly limit as "Limit not enforced". OpenAI sends alerts but does not stop calls. The alerts on that page are monthly thresholds; APR-0056 asked for an alert at 1 USD per day.
Proposed: the health check reads the day's spend and stops the gateway (kill switch) above the APR-0056 limits. Until then the CEO checks the usage page after each test session.
Needs: CEO yes or no, and a check of whether OpenAI offers a daily alert.

Update 2026-10-23: the CEO set the OpenAI project limit to enforced (5 USD per month). Calls stop with 429 project_spend_limit_exceeded when it is reached; enforcement is not instant. No daily alert option was confirmed. Still open: the kill switch in the health check and the 1 USD per day alert (APR-0056).
CEO 2026-10-25: the kill switch can wait ("ignore for now", SD-002). The enforced 5 USD monthly project limit stays the only hard stop. Sandbox draft: research/sandbox/2026-10-25-agy/P-31-cost-hard-stop.md. It treats 1 USD per day as a kill; APR-0056 says an alert at 1 USD per day.
CEO 2026-10-25: cost limits for Loop 2 deferred (APR-0073). APR-0056 was for Loop 1.

## P-32 - Memory design before Loop 2
Open: the per-agent MEMORY.md files are empty templates and ADR-0011 (append-only history, projected state) is empty. OpenClaw's memory-core (memory search with embeddings, nightly dreaming) is off for Loop 1 (APR-0061).
Questions: what each agent should remember beyond its state files; where memory lives; whether recall may use a cloud embedding model or must be local (ADR-0003); how memory stays append-only (ADR-0011).
Needs: a design decision before Loop 2. Until then memory-core stays off.
Added 2026-10-24 (APR-0063): the CEO will mostly talk to the COO, who routes to the chiefs, and may address any agent at any time. Open: how much context the COO builds up when it routes everything, and what it must ask the chiefs for instead of keeping. First data: the COO's prompt on a Slack turn was about 35,000 tokens (window 272,000). Per-agent token counts per scenario run are still to measure.
Sandbox drafts 2026-10-25: research/sandbox/2026-10-25-agy/P-32-memory.md. CEO: SD-005 (local embeddings) later, after the local model work; SD-006 (check state files before answering) needs a token estimate; SD-007 (short COO handoffs) needs explaining.

## P-36 - 04:00 daily reset check (pending, not to be raised for now)
Status: pending. The CEO asked on 2026-10-25 not to bring this up for a while.
Needs: after the first inbound message past 04:00 AST, record the session IDs of the five main sessions and compare them with the list captured at 00:54 on 2026-10-25.
Method: section 7.7 of guides/loop1-baseline.md.

## P-37 - COO SQLite maintenance warning at scenario start (Loop 2)
Seen 2026-10-25 in runs 018 (01:31:10) and 019 (01:42:52): about 2 seconds after the scenario post, the gateway logs 'SQLite session write failed' on the COO database (operation session.maintenance.plan, error 'SQLite automatic maintenance activity changed before age consumption'), right after 'slow agent database reservation' (about 1.1 to 1.2 s, outcome ok). Also seen 2026-10-24 at 19:56 and 21:59.
No visible effect on any run.
Code reading (sandbox, 2026-10-25, OpenClaw 2026.10.5 dist): a maintenance plan rejected by a concurrent write is retried; after 3 rejections (MAX_MAINTENANCE_REJECTIONS) OpenClaw logs 'SQLite automatic session maintenance paused after repeated input changes'. That line appears 0 times in the gateway logs for 2026-10-24 and 2026-10-25, so the limit was never reached. Details: research/sandbox/2026-10-25-agy/P-37-findings.md.
CEO 2026-10-25: keep P-37 open until it is checked on a real Loop 2 run.
Needs: on the first Loop 2 runs, grep the gateway log for 'maintenance paused' and 'SQLite session write failed'.
Checked 2026-10-26: runs loop2-scn-001 and loop2-scn-002, on the gateway process that was ready at 23:46 AST on 2026-10-25: 0 occurrences of 'SQLite session write failed' and 0 of 'maintenance paused' in the gateway logs of 2026-10-25 and 2026-10-26 (the log rotates by local date, so a run that crosses midnight needs both files). Proposed: keep P-37 open for two or three more runs, as the CEO asked.
Seen 2026-10-26 01:55:50 AST: one 'SQLite session write failed' on the COO (operation session.maintenance.plan, pid 3403610, the gateway started after the v1.7 upgrade), at the post of run loop2-scn-003. Not in loop2-scn-004; 'maintenance paused' 0. No visible effect. Loop 2 tally: 1 occurrence in 4 runs (001, 002, 004: none).

## P-39 - The CHO did not write the health plan in run loop2-scn-005
Seen 2026-10-26 15:57 AST (run loop2-scn-005, v1.7): the CHO moved the workout through the CoS correctly, but state/health-plan.md stayed unchanged (change log empty). Run loop2-scn-004 logged two lines there (sleep note cho-01, move cho-02). Scenario criterion 2 (APR-0058) failed in run 005. The COO reply gave one event ID (loop2-scn-005-cho-01).
Instruction today: "Setup note: keep the current plan in state/health-plan.md. Append a line for each change with the run ID and event ID." It is a soft note, not a numbered rule.
The trajectory export hides exec code, so the CHO's tool calls cannot be read; the export shows 4 exec calls, 1 message and 1 sessions_send, and no mention of health-plan.
Run loop2-scn-006 (2026-10-26 16:33 AST): it repeats in part. The CHO logged the sleep line (cho-01) but not the move line (cho-02). Tally under v1.7: run 004 both lines, run 005 none, run 006 one of two. Run 003 was not checked.
Proposed, not decided: one more CHO rule (instruction set v1.8), added the way v1.7 was (deploy/loop1 upgrade script, gateway stopped, AGENTS.md only, own APR entry): "- Health plan log (instruction set v1.8): for every event ID you create, append one line to state/health-plan.md before you reply: run ID | event ID | change. A sleep note and a calendar move each get their own line. If an event ID is already in the log, do not add it again."
Needs: the CEO's yes or no on that rule. Nothing is changed without it.

## P-40 - Calendar: what must be decided before real data
Left over when P-28 was closed (APR-0080). Loop 2 runs on synthetic data (APR-0073); none of this is needed for that.
1. Privacy mark: the push job shows an entry as busy in Google only when its journal line carries privacy=high (APR-0079). The CoS does not write that mark. Who decides that an entry is high privacy (the privacy gate, ADR-0003) and how the mark reaches the CoS needs the CEO's yes, and an agent instruction change (new APR entry).
2. Real calendar: the cron pushes to the Google test calendar. Moving it to the real calendar is a one-line change in ~/loop1/gcal-sync/env on the VM, after the CEO's go.
3. Monthly archive job (APR-0072): not built.
4. Look at the busy block in the Google Calendar app (not checked yet).
Needs: the CEO's decisions on 1 and 2 before any real data enters Loop 2.
