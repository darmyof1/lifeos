# ADR-0015 - Repo, runtime, and seed are separate namespaces

Status: accepted
Date: 2026-10-16
Approval basis: APR-0029 (decision 3, approved by the CEO as a decision). Related: APR-0005 (sanitized seed set), APR-0010 (local encrypted archive until Phase 2).

## Context
The repo is public design memory. The runtime holds personal records. The seed holds the CEO's private identity files. Mixing them would let personal data enter git.

## Decision
Five namespaces, each with one purpose:
- repo: this repository. Public design memory. No personal data. Checked by validator checks 8 (personal emails and IP addresses) and 10 (secrets).
- runtime: ~/.openclaw on the VM. Agent workspaces and personal records under custom/. Not in git.
- seed: the CEO's private identity and constitution files, used by Genesis. Never in git.
- workbench: the AI working environment used for design and audit rounds.
- ops-logs: ~/lifeos-ops/logs on the VM. Command test logs. Not in git.

Rules:
- Only sanitized summaries enter the repo. ops/install-log.md is the model.
- Seed files are never copied into the repo.

## Alternatives rejected
Not recorded in the sources available to this repository. The CEO should add any alternatives considered.

## Consequences
- PATHS.md must be checked against this list. Not yet checked.
- Any new file that holds personal data must go to runtime or seed, never to repo.
