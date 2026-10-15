# ADR-0016 — Per-domain access, not a universal symlink

Status: accepted
Date: 2026-10-12
Approval basis: APR-0029 (decision 1).

## Context
An earlier design gave every agent workspace a symlink to the whole domains/ folder. Then any agent could read any domain, which causes context pollution (the COO would hold health, finance, and career data) and breaks the privacy model.

## Decision
Each agent gets access only to the domain paths it needs. Access is declared per agent in contracts/identity-access.yaml and deployed by the deploy map. There is no universal domains/ symlink in any agent workspace.

## Alternatives rejected
- Universal symlink: every agent sees every domain. Rejected for context and privacy reasons.
- Copy the data into each workspace: duplicates personal data and drifts out of sync.

## Consequences
- contracts/identity-access.yaml and deploy/deploy-map.yaml must be written before Genesis (currently planned).
- Each new domain needs an access rule before its agent is spawned.
