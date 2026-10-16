# ADR-0014 - OpenClaw is the initial runtime

Status: accepted
Date: 2026-10-16
Approval basis: APR-0029 (decision 2, approved by the CEO as a decision).

## Context
The agent hierarchy needs a runtime on the Oracle VM. The runtime must not lock the system to one vendor, and personal data must stay outside the framework's update path.

## Decision
OpenClaw is the initial agent runtime. It runs on the Oracle VM. Agent workspaces follow OpenClaw's directory convention (workspace-{agent}/). Personal records live in custom/ under the runtime root, which OpenClaw updates are meant not to touch (manifest, custom/ namespace).

## Rationale (manifest section 9c)
- Local-first: agent execution is file-system based, around local CLI tools and plain-text workspaces.
- No vendor lock-in: the standard directory layout means a migration to another framework is a file copy.

## Alternatives rejected
Not recorded in the sources available to this repository. The CEO should add any alternatives considered.

## Consequences
- OpenClaw updates follow ops/openclaw-update-policy.md, which must be checked against this decision before the first update.
- The workspace layout is the migration contract. If it changes, a new ADR supersedes this one.
- Spikes SPK-01 to SPK-04 are planned and have not run (P-09). Until they do, the runtime behaviour this decision relies on is unverified.
