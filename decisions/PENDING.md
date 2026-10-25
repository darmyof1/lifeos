# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-08 (APR-0040), P-13 (APR-0041), P-18 (APR-0042), P-19 (APR-0043), calendar routing (APR-0044), Slack exemption (APR-0045), P-20 (APR-0046), P-21 (APR-0047), P-22 (APR-0048), P-24 (APR-0049), P-23 (APR-0050), P-25 (APR-0051), P-27 (APR-0062), P-30 (APR-0060), P-33 (APR-0063), P-29 (solved by a finding, guides/loop1-baseline.md section 7.10), P-34 (APR-0066).

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
Needs: nothing in Loop 1.

## P-28 - Calendar journal and Google Calendar (Loop 2)
Proposed: the CoS keeps a journal of every calendar entry it means to write, with a status (pending, written, failed) and an attempt count. A scheduled job (code, not the model) retries pending entries every 5 minutes (S-06). Before a retry it searches Google for the entry's unique name (APR-0034) so that a write which succeeded but looked failed is not repeated. After 5 failures the COO is told and the CEO checks. If the Google token is revoked (S-07), all writes pause and the CIO alerts in its channel. Google stays the calendar of record (APR-0031); the journal is the hold and the audit trail.
Loop 1 results (2026-10-22): the journal is append-only (APR-0058) and a move is two lines (APR-0057). The health check fails on any removed journal line (git diff --numstat shows deletions above 0).
Added: keep the active journal small, because the CoS reads all of it on every check and cost grows with it. Keep future entries, the last 14 days and anything not yet pushed. Move older lines each month to state/archive/calendar-YYYY-MM.md. The workspace git keeps the full history.
Added: for Loop 2 the status set grows to requested, written, pushed, failed (with attempt count and last error), conflict, moved and delete-pending-approval, plus the Google event ID once pushed. Pushes and retries run in code, not in the model (ADR-0008, ADR-0011).
Needs: CEO yes or no.

## P-31 - Cost hard stop (APR-0056)
Seen 2026-10-22: the OpenAI project page shows the 5 USD monthly limit as "Limit not enforced". OpenAI sends alerts but does not stop calls. The alerts on that page are monthly thresholds; APR-0056 asked for an alert at 1 USD per day.
Proposed: the health check reads the day's spend and stops the gateway (kill switch) above the APR-0056 limits. Until then the CEO checks the usage page after each test session.
Needs: CEO yes or no, and a check of whether OpenAI offers a daily alert.

Update 2026-10-23: the CEO set the OpenAI project limit to enforced (5 USD per month). Calls stop with 429 project_spend_limit_exceeded when it is reached; enforcement is not instant. No daily alert option was confirmed. Still open: the kill switch in the health check and the 1 USD per day alert (APR-0056).

## P-32 - Memory design before Loop 2
Open: the per-agent MEMORY.md files are empty templates and ADR-0011 (append-only history, projected state) is empty. OpenClaw's memory-core (memory search with embeddings, nightly dreaming) is off for Loop 1 (APR-0061).
Questions: what each agent should remember beyond its state files; where memory lives; whether recall may use a cloud embedding model or must be local (ADR-0003); how memory stays append-only (ADR-0011).
Needs: a design decision before Loop 2. Until then memory-core stays off.
Added 2026-10-24 (APR-0063): the CEO will mostly talk to the COO, who routes to the chiefs, and may address any agent at any time. Open: how much context the COO builds up when it routes everything, and what it must ask the chiefs for instead of keeping. First data: the COO's prompt on a Slack turn was about 35,000 tokens (window 272,000). Per-agent token counts per scenario run are still to measure.

## P-35 - SESSION_WORK_START_CHANGED on agent replies
Seen 2026-10-24 in runs 010, 012 and 013: when the CoS replies to a CHO that is waiting for it, the reply is delivered ("sent before error") and the CHO gets the result, but the acknowledgement fails with SESSION_WORK_START_CHANGED. The CoS then reports a FAILURE to the COO.
Question: treat it as benign (no FAILURE when the content was delivered), or find the cause first.
Run 014 (v1.5, not a valid move test): the CHO answered from its own memory of run 013; no journal change.
Run 015 (v1.5, pass on content): the CoS logged a session-start error on its reply to the CHO (gateway log, 2026-10-24 22:08:00); the CHO handled the content anyway, and the COO's answer showed no FAILURE. SESSION_WORK_START_CHANGED count stayed at 2.
Log check (2026-10-25): the words SESSION_WORK_START_CHANGED and 'session-start error' appear only in the agents' own replies, not as gateway error lines. The earlier grep counted those replies, so a count of 2 does not show that no gateway error happened. Nearest gateway lines: 'SQLite session write failed ... Activity recap lifecycle or utility model changed' (2026-10-24 21:54:43, during a gateway stop) and 'SQLite automatic maintenance activity changed before age consumption' (19:56 and 21:59). Not yet tied to a run.
Runs 010 and 012: the CoS sent the COO a FAILURE note. Runs 015 and 016: no FAILURE note.
Decided (APR-0067): the CoS reports these as 'delivered; acknowledgement error', not FAILURE (instruction set v1.6). The cause is still open.
Run 017 (v1.6, 2026-10-25 01:18-01:20): the CoS reported 'logged as delivered, but its acknowledgement failed (P-35); CHO has not replied with the content'. The CHO replied with the content about a minute later, so this looks like a timing race, not a lost message. The COO's reply had no FAILURE note. The gateway log has no error line for the acknowledgement; the nearest is 'slow agent database reservation' at 01:18:55 (1056 ms, outcome ok). The v1.6 wording works. The cause is still open.
Needs: one more run with a wider log capture (acknowledg, slow, SQLite, error, fail, deliver), then a CEO decision on P-35.

## P-36 - 04:00 daily reset check (pending, not to be raised for now)
Status: pending. The CEO asked on 2026-10-25 not to bring this up for a while.
Needs: after the first inbound message past 04:00 AST, record the session IDs of the five main sessions and compare them with the list captured at 00:54 on 2026-10-25.
Method: section 7.7 of guides/loop1-baseline.md.
