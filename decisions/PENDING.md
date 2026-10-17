# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-08 (APR-0040), P-13 (APR-0041), P-18 (APR-0042), P-19 (APR-0043), calendar routing (APR-0044), Slack exemption (APR-0045), P-20 (APR-0046), P-21 (APR-0047), P-22 (APR-0048), P-24 (APR-0049).

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file), SPK-09 (see file). Partial: SPK-05 (see file).
Several need the OpenClaw runtime running on the VM. Run them when the system is up.

## P-17 - Dashboard or website for the owner (future)
Owner: CMO (roster: "produces the weekly life dashboard"). Proposed, not yet approved: the CKO supplies the memory data behind it.
Decision made: the owner must be able to reach it from the internet. It will be heavily protected. How it is protected is decided later.
Not now: no design until the agent loop is proven.
Needs: nothing today. A design item is opened when the loop is proven.

## P-23 - What the CEO sees of agent-to-agent communication (proposed)
Proposal: you see every message that changes something in the real world, and every failure. You do not see routine checks.
- Every cross-agent request that changes a real thing (calendar add, budget change, delete) is posted in the sender's channel and in the receiver's channel. The COO announces each calendar add in the COO channel (APR-0044).
- A reply to the requester is posted in the requester's channel. Example: CoS writes the calendar change, then posts in CHO's channel that the change is done, and posts the same in its own channel.
- Every failure, escalation and retry limit (for example S-06 after 5 attempts) is posted to the COO channel.
- Routine reads, status checks and retries under the limit are not posted. They stay in the call log (P-21), which you can open at any time.
Reason: a full feed would bury the messages that matter. The log keeps the detail for when you want it.
Needs: yes or change.
