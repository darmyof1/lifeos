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

## APR-0019 — Local primary model is llama3.1:8b
Status: approved
Decided by: CEO
Your answer: "approve llama3.1:8b to be the local"
Evidence: research/spikes/SPK-06-local-model-on-vm.md (model ran on the VM, about 5.3 GB resident)
Supersedes: the size part of APR-0004 (12–14B). The new primary is 8B. APR-0004 is not edited.
Applies to: contracts/models/aliases.yaml (local-primary, triage)

## APR-0020 — Local backup model is Qwen 2.5 14B
Status: approved
Decided by: CEO
Your answer: "qwen2 as backup to it"
Applies to: contracts/models/aliases.yaml (local-backup)
Open: the exact tag must be confirmed (PENDING P-08).

## APR-0021 — Cloud-cheap can be switched by a provider field (Haiku 5.5 toggle)
Status: approved
Decided by: CEO
Your answer: "CEO: yes" to the proposal in P-01
Applies to: contracts/models/aliases.yaml (cloud-cheap, options list). Default stays gemini-3.8-flash-medium (APR-0018).

## APR-0022 — Minimum Genesis seed set
Status: approved
Decided by: CEO
Your answer: "CEO: yes" to the proposal in P-02: ceo-soul, ceo-identity, 2026-vision, constitution, genesis-interview-answers, health-baseline. Everything else is generated.
Applies to: bootstrap/genesis-primer.md, bootstrap/genesis-runbook.md (when written); APR-0005
CEO: Approved

## APR-0023 — ADRs required before Genesis
Status: approved
Decided by: CEO
Your answer: "CEO: yes" to the proposal in P-04: ADR-0003 (privacy), ADR-0004 (triage), ADR-0007 (CISO escalation), ADR-0016 (per-domain access). The rest follow after Genesis.
Applies to: decisions/adr/
CEO: Approved
## APR-0024 — Model IDs for Opus, GPT, and Gemini are correct
Status: approved
Decided by: CEO
Your answer: "CEO: yes, all correct" (P-06)
Applies to: aliases.yaml (genesis-brain, cloud-reasoning-high: claude-opus-5-5; cloud-code: GPT-6-Luna; cloud-cheap: gemini-3.8-flash-medium)
Note: no provider probe is recorded in research/spikes/ for these three yet. Only SPK-06 (local) has evidence.

## APR-0025 — Local backup model is qwen3.5:latest (digest 6488c96fa5fa)
Status: approved
Decided by: CEO
Your answer: installed models, "llama3.1:8b is ok", "these are my current local models i might change them later"
Evidence: `ollama list` output recorded in contracts/models/aliases.yaml
Supersedes: APR-0020 (the qwen2.5 14B tag). APR-0020 is not edited.
Applies to: contracts/models/aliases.yaml (local-backup)

## APR-0026 — gemma4:latest (digest c6eb396dbd59) is installed, not assigned to a route
Status: approved
Decided by: CEO
Your answer: installed; no role assigned yet
Applies to: nothing routed. It may be evaluated later under a new spike, and assigned only by a new APR entry.

## APR-0027 — Local model tags are pinned by digest in the aliases file
Status: approved
Decided by: CEO
Your answer: "i might change them later as I do upgrades"
Rule: a model change is a new APR entry plus an edit to aliases.yaml. Tags such as :latest move, so the digest is what the record uses.

## APR-0028 — CoS owns the combined calendar view
Status: approved
Decided by: CEO
Your answer: "the answer is CoS" (P-03, option a)
Meaning: CoS builds and holds the single combined calendar. It reads family events from CFA and personal events from CLO. It is the one place where conflicts across domains are checked.
Not decided here: which agent may WRITE a calendar entry (see P-10).
Applies to: design/ (calendar section, when written); agent-files/executive/cos/

## APR-0029 — The three draft ADRs are approved as decisions
Status: approved
Decided by: CEO
Your answer: "approve" (P-07)
Decisions:
  1. Per-domain access instead of universal symlinks (ADR-0016)
  2. OpenClaw is the initial runtime (ADR-0014)
  3. Repo, runtime, and seed are separate (ADR-0015)
Applies to: decisions/adr/ADR-0014, ADR-0015, ADR-0016 (the text is still to be written)

## APR-0030 — CoS is the only agent that writes calendar entries
Status: approved
Decided by: CEO
Your answer: "ok cos handles my calendar, approve" (P-10, option a)
Meaning: only CoS creates, changes, or deletes calendar entries. Other agents send CoS a request.
The COO is the front door: it receives your request, routes it, and relays the result. It does not write calendar entries.
Reason for the split: the COO holds conversation context and is already the single point of failure (see design/). Scheduling conflicts need the full picture, which belongs to CoS.
Applies to: decisions/adr/ (none directly); agent-files/executive/cos/ and agent-files/executive/coo/ (when written)

## APR-0031 — Google Calendar is the calendar store
Status: approved
Decided by: CEO
Your answer: "google calendar" (P-11)
Open consequence: calendar entries are personal data stored with a cloud provider. What may be stored there is a separate decision (PENDING P-12).
Applies to: design/ (calendar section, when written); contracts/channels.yaml or a calendar contract (when written)
