# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-08 (APR-0040), P-13 (APR-0041), P-18 (APR-0042), P-19 (APR-0043), calendar routing (APR-0044), Slack exemption (APR-0045).

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file), SPK-09 (see file). Partial: SPK-05 (see file).
Several need the OpenClaw runtime running on the VM. Run them when the system is up.

## P-17 - Dashboard or website for the owner (future)
Owner: CMO (roster: "produces the weekly life dashboard"). Proposed, not yet approved: the CKO supplies the memory data behind it.
Decision made: the owner must be able to reach it from the internet. It will be heavily protected. How it is protected is decided later.
Not now: no design until the agent loop is proven.
Needs: nothing today. A design item is opened when the loop is proven.

## P-20 - Who writes each agent's instructions (proposed: CSTO, from approved rules)
Proposal: Aurelius (CSTO) turns the approved rules into one instruction file per chief. The roster already gives the CSTO "defines SOPs for every other chief".
Limits on that work:
1. It is written only from approved APR entries. It adds no new rule.
2. Each rule in a file cites its APR number.
3. Each file is a draft until you approve it.
4. The CISO checks the tool permissions listed in each file before approval.
Before Aurelius writes, a rules index is generated from APPROVALS.md by a script, the same way the agent list is generated from the roster. Aurelius reads that index, not the whole ledger.
Open question: confirm that Aurelius writes the drafts, and that the CEO approves them.
Needs: yes or change.

## P-21 - LLM call log: exact requests and responses (proposed design, not built)
Proposal:
- A folder per day in the runtime (not in git) holds one file per call with the request body and the response body exactly as sent and received.
- Each call also records its SHA-256 hash, model alias, provider (local or cloud), route, privacy label, timestamps and status.
- Only authorization header values are left out. The API key is never written. Everything else stays raw, because redaction would alter the record.
- An append-only index lists every call, and a small command lists and shows them.
- Covers local and cloud calls alike. Cloud calls can be logged only after the privacy gate has passed them.
Build later. This is a design item, so it does not block the current fixes.
Needs: yes or change.

## P-22 - Slack channel model (proposed)
Proposal:
- One channel per chief, for requests from that chief. The request is posted in that channel, and the COO confirms in the same channel.
- The COO channel is private and holds only you and the COO.
- Slack is exempt from the titles-only rule while it is the channel, for private channels only (APR-0045, privacy.yaml channels block). Each post is logged under P-21.
Open choice: one Slack app with a display name per message (simpler, the posts come from one app), or one Slack app per agent (each agent is a real separate identity). I believe Slack supports per-message display names, but confirm in Slack's documentation before building.
Needs: choose the identity option, then yes or change.
