# ADR-0004 — Triage runs on the local model

Status: accepted
Date: 2026-10-12
Approval basis: APR-0001 (triage is local), APR-0019 (the local model is llama3.1:8b), APR-0004 (size, superseded in part by APR-0019).

## Context
Every query is classified before any privacy or routing decision. The classifier itself reads the raw query. If the classifier were a cloud model, the raw text would leave the machine before the gate runs, and the gate would depend on a classification that has already been sent out.

## Decision
Triage always runs on the local model. The alias `triage` points to `local-primary` (llama3.1:8b, APR-0019). No raw query is sent to a cloud model for classification. The local model is recorded by digest in contracts/models/aliases.yaml.

## Alternatives rejected
- Cloud triage (for example Gemini): sends raw text off the machine before the privacy gate runs.
- Rules-only triage: too brittle for free-text requests. Kept only as a deterministic prefilter in front of the local model.

## Consequences
- Triage quality is limited by an 8B model. Misclassification is possible.
- The validator (blocking check 7) fails the build if the triage alias points at a non-local provider.
