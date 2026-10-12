# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Resolved in this round: P-01, P-02, P-04, P-05, P-06 (see APPROVALS.md, APR-0019 to APR-0024).

## P-03 — Calendar owner (still open)
What it means: one place that shows all your events together (family, personal, work). Someone has to own building that combined view.
Options:
  a) CoS builds the combined calendar, reading family events from CFA and personal events from CLO. (recommended)
  b) CFA owns it.
  c) CLO owns it.
Needs: a, b, or c.

## P-07 — Draft ADRs not yet approved
Proposed by the audit, not approved by you: per-domain access instead of universal symlinks; OpenClaw as the initial runtime; repo, runtime, and seed separation. Keep as drafts until each is approved.
Needs: yes or no for each.

## P-08 — Exact model tags to confirm
1. Local primary: you approved "llama3.1:8b". The PENDING note said "llama3:8b". Which one?
2. Local backup: "qwen2" was approved. Confirm the exact tag. Candidate: qwen2.5:14b-instruct-q4_K_M.
3. Haiku 5.5 API model ID (needed for the APR-0021 toggle) is not yet verified. Needs a probe.
Needs: confirmation of 1 and 2, and a probe result for 3.
