# ADR-0003 — Privacy gate is enforced in code

Status: proposed
Date: 2026-10-12
Approval basis: APR-0007 (precedence: privacy wins). The mechanism "enforced in code, not in prompts" is not yet approved. Approve it before this ADR becomes accepted.

## Context
Some queries contain high-privacy data (health, finance, family, journal). A prompt instruction such as "do not send health data to the cloud" can be ignored or misread by a model. The gate must not depend on the model's behaviour.

## Decision
The privacy gate is a function in src/lifeos/router/gate.py. It runs after triage and before any adapter is called. It reads the privacy level from the triage output and the rules in contracts/policy/privacy.yaml. A high-privacy request cannot reach a cloud adapter, and no prompt text can change that.

## Precedence (approved, APR-0007)
Privacy wins over complexity. A critical-complexity request with high privacy stays local. The CEO can override only with an explicit confirmation, which is logged.

## Alternatives rejected
- Prompt-only instruction: the model can be wrong, and the failure is silent.
- Gate after the cloud call: data has already left the machine.

## Consequences
- The gate is testable with unit tests (tests/unit/test_gate.py).
- A wrong triage label can still send data incorrectly. Mitigation to confirm: when triage is unsure, treat the query as high privacy.
