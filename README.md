# LifeOS (Sovereign Life OS)

A personal operating system run by a team of AI agents (chiefs) for one person, the CEO. Each chief owns a domain (operations, health, finance, scheduling and more; design/roster.md). Private data is meant to stay on hardware the CEO controls; cloud models are used only where the privacy rules allow.

## Status (2026-10-27)
- Loop 1 (first agents on a VM, synthetic data) closed: APR-0071, deploy/loop1/LOOP1-CLOSE-RECORD.md.
- Loop 2 (four agents COO, CHO, CoS, CFO hand work to each other through Slack; the CoS journal is pushed to a Google test calendar by code; high-privacy entries become "busy"; deletes need the CEO's approval) closed: APR-0096, deploy/loop2/LOOP2-CLOSE-RECORD.md.
- Loop 3 (rebuildable repo, delete gate in code, privacy gate built but not wired, security documents, identity contract) closed: APR-0115, deploy/loop3/LOOP3-CLOSE-RECORD.md.
- Loop 4 (backup and recovery: encrypted weekly backup to a private repository, restore proven on another machine) closed: APR-0118, deploy/loop4/LOOP4-CLOSE-RECORD.md. No real personal data is used until a separate approval.
- Loop 5 (calendar privacy toggle, privacy gate in shadow mode, a real-calendar setting that is not authorized) closed: APR-0120, deploy/loop5/LOOP5-CLOSE-RECORD.md. The privacy gate runs in shadow mode (blocks nothing); the real calendar is not authorized.
- Loop 6 (hardening: CFO send list COO only, COO morning compaction) approved: APR-0121, deploy/loop6/LOOP6-SCOPE.md.

## Where to start
- decisions/APPROVALS.md: every decision, in the CEO's words (append-only).
- decisions/PENDING.md: open questions.
- deploy/loop1/STATE.md: what runs on the VM now and how to work on it.
- design/: the target architecture. Many design files are planned and still empty (contracts/registry/artifacts.yaml lists each file's status).
- contracts/: machine-readable rules (agents, privacy, calendar, budget).
- scripts/gcal/: the calendar push job. scripts/verify/validate_repo.py: the repo validator.
- tests/scenario/: the scenarios and their run logs. tests/unit/: unit tests.
- guides/: tested procedures. ops/: handover reports and evidence.

## How changes arrive
Changes are made by numbered fix scripts, run and pushed from the CEO's Mac. Each runs the unit tests and the validator before it commits. Agent behaviour changes only with a new approval entry.
