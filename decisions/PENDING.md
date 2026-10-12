# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.

## P-01 — Haiku 5.5 toggle for cloud-cheap
Your answer was partial: "there must be something i can toggle".
Proposal: keep one `provider` field per alias in contracts/models/aliases.yaml. Switching to Haiku 5.5 is then a one-line change.
Needs: your yes or no.

## P-02 — Minimum Genesis seed set
Your answer was: "need help later".
Proposal: five hand-written documents only (ceo-soul, ceo-identity, 2026-vision, constitution, genesis-interview-answers) plus health-baseline. Everything else is generated.
Needs: your yes or no.

## P-03 — Calendar owner
Your answer was: "need help on what is this".
Proposal: CoS aggregates the calendar. CFA (family) and CLO (lifestyle) supply their events.
Needs: your yes or no.

## P-04 — How many ADRs must exist before Genesis
Your answer was: "dont understand this part".
Proposal: ADR-0003 (privacy), ADR-0004 (triage), ADR-0007 (CISO escalation), ADR-0016 (per-domain access). The rest can follow after Genesis.
Needs: your yes or no.

## P-05 — Exact local model
The size is approved (APR-0004). The exact model is not. Candidate: qwen2.5:14b-instruct-q4_K_M. Needs a test on the VM (research/spikes/SPK-06).

## P-06 — Verify model IDs against each provider's own CLI or API
Needs probes for: claude-opus-5-5 (genesis-brain), GPT-6-Luna (cloud-code), gemini-3.8-flash-medium (cloud-cheap), and the local model tag. Record the results in research/spikes/.

## P-07 — Draft ADRs not yet approved
The following were proposed by the audit, not approved by you: per-domain access instead of universal symlinks; OpenClaw as the initial runtime; repo, runtime, and seed separation. Keep them as drafts until you approve each one.
