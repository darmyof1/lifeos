# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Closed since the last version: P-08 (APR-0040), P-13 (APR-0041), P-18 (APR-0042), P-19 (APR-0043), calendar routing (APR-0044), Slack exemption (APR-0045), P-20 (APR-0046), P-21 (APR-0047), P-22 (APR-0048), P-24 (APR-0049), P-23 (APR-0050).

## P-09 - Spikes not yet run
Planned: SPK-01 to SPK-04 and SPK-07. Done: SPK-06 (see file), SPK-09 (see file). Partial: SPK-05 (see file).
Several need the OpenClaw runtime running on the VM. Run them when the system is up.

## P-17 - Dashboard or website for the owner (future)
Owner: CMO (roster: "produces the weekly life dashboard"). Proposed, not yet approved: the CKO supplies the memory data behind it.
Decision made: the owner must be able to reach it from the internet. It will be heavily protected. How it is protected is decided later.
Not now: no design until the agent loop is proven.
Needs: nothing today. A design item is opened when the loop is proven.

## P-25 - CHO communication scenarios (draft: design/cho-scenarios.md)
Scenarios C-01 to C-06 show each step, who does it, and when, for wake-up changes, therapy logs, meal plans, supplements, the dashboard nutrition section, and conflicts.
Open questions:
1. Therapy log: log in the CHO channel, or another route?
2. Therapy owner: CHO (proposed) or CSP?
3. Therapy calendar reminders: show the therapy name, or "busy"?
4. Alarm: which device, and which chief owns it (proposed: CIO)?
5. Supplements: CHO changes timing freely; a dose change always needs a doctor or pharmacist check (proposed).
6. Meal plan: is it acceptable that the local model drafts it?
Needs: answers to 1 to 6, or yes to the proposed answers.
