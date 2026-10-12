# Approvals ledger

Only entries with `Status: approved` are binding. Quotes are the CEO's own answers from the
decision review (2026-10-10). Open items are in `decisions/PENDING.md`.
Each ADR cites these IDs. A change to an approved decision needs a new entry, not an edit.

## APR-0001 — Triage runs locally
Status: approved
Decided by: CEO
Your words: "triage is local, it has always been"
Applies to: ADR-0004; contracts/models/aliases.yaml (triage)

## APR-0002 — Cloud code model is GPT-6 Luna
Status: approved
Decided by: CEO
Your answer: "change to GPT-6 Luna"
Applies to: contracts/models/aliases.yaml (cloud-code)

## APR-0003 — Genesis model is Opus 5.5
Status: approved
Decided by: CEO
Your answer: "b" (move to claude-opus-5-5)
Applies to: contracts/models/aliases.yaml (genesis-brain, cloud-reasoning-high). Model ID still needs a probe (PENDING P-06).

## APR-0004 — Local model is a smaller model, about 12–14B
Status: approved
Decided by: CEO
Your answer: "a" (smaller local model, about 12–14B)
Applies to: contracts/models/aliases.yaml (local-primary). The exact model is not yet chosen (PENDING P-05).

## APR-0005 — Genesis inputs are a sanitized seed set you approve
Status: approved
Decided by: CEO
Your answer: "b"
Applies to: bootstrap/genesis-primer.md (when written); ADR-0017

## APR-0006 — Genesis Slack posts use a bounded, Genesis-only token
Status: approved
Decided by: CEO
Your answer: "b" (bounded Genesis-only scope)
Applies to: bootstrap/genesis-runbook.md (when written). The token is revoked when Genesis ends.

## APR-0007 — Privacy wins over critical complexity
Status: approved
Decided by: CEO
Your answer: "a" (privacy always wins; the CEO can override with explicit confirmation)
Applies to: contracts/policy/privacy.yaml; ADR-0003

## APR-0008 — CISO escalates P1 directly to the CEO
Status: approved
Decided by: CEO
Your answer: "a" (direct CISO to CEO)
Applies to: contracts/policy/escalation.yaml (when written); ADR-0007

## APR-0009 — The COO is the event dispatcher
Status: approved
Decided by: CEO
Your answer: "b" (COO)
Applies to: design/event-bus.md (when written); ADR-0008

## APR-0010 — Archive is local and encrypted until Phase 2; no AWS in the pilot
Status: approved
Decided by: CEO
Your answer: "b" (local encrypted archive until Phase 2)
Applies to: contracts/policy/archive.yaml (when written); ADR-0012

## APR-0011 — Archive uses S3 Object Lock (Compliance) with lifecycle to Glacier
Status: approved
Decided by: CEO
Your answer: "Object Lock Compliance with lifecycle to Glacier"
Applies to: contracts/policy/archive.yaml (when written); ADR-0012. Phase 2 only (see APR-0010).

## APR-0012 — One ADR per core decision
Status: approved
Decided by: CEO
Your answer: "one per core decision"
Applies to: decisions/adr/ (the ADR set)

## APR-0013 — Append-only logs plus state snapshots
Status: approved
Decided by: CEO
Your answer: "b" (state snapshots plus append-only logs)
Applies to: design/memory-and-data.md (when written); ADR-0011

## APR-0014 — Heartbeat files are renamed without spaces
Status: approved
Decided by: CEO
Your answer: "yes"
Applies to: agent-files/**/HEARTBEAT-*.md

## APR-0015 — Quiet hours use AST
Status: approved
Decided by: CEO
Your answer: "ast"
Applies to: ops/notification-strategy.md (when written)

## APR-0016 — Transient specialists are prompt templates
Status: approved
Decided by: CEO
Your answer: "prompt template"
Applies to: agent-files/transient/*/PROMPT.md; ADR-0010

## APR-0017 — CKO heartbeat is part of Phase 1
Status: approved
Decided by: CEO
Your answer: "yes from phase 1"
Applies to: agent-files/executive/cko/ (HEARTBEAT); design/agent-lifecycle.md

## APR-0018 — Cloud cheap model is gemini-3.8-flash-medium
Status: approved
Decided by: CEO
Your answer: "gemini-3.8-flash-medium" (the Claude Haiku 5.5 toggle is NOT approved; see PENDING P-01)
Applies to: contracts/models/aliases.yaml (cloud-cheap)
