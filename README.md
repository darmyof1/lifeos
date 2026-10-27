# LifeOS (Sovereign Life OS)

A personal operating system run by a team of AI agents (chiefs) for one person, the CEO. Each chief owns a domain (operations, health, finance, scheduling and more; design/roster.md). Private data is meant to stay on hardware the CEO controls; cloud models are used only where the privacy rules allow.

## Status (2026-10-27)
- Loop 1 (first agents on a VM, synthetic data) closed: APR-0071, deploy/loop1/LOOP1-CLOSE-RECORD.md.
- Loop 2 (four agents COO, CHO, CoS, CFO hand work to each other through Slack; the CoS journal is pushed to a Google test calendar by code; high-privacy entries become "busy"; deletes need the CEO's approval) closed: APR-0096, deploy/loop2/LOOP2-CLOSE-RECORD.md.
- Loop 3 is not defined yet. No real personal data is used until a Loop 3 approval says so.

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
