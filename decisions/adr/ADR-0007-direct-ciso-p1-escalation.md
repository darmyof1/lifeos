# ADR-0007 — CISO escalates P1 security events directly to the CEO

Status: accepted
Date: 2026-10-12
Approval basis: APR-0008 (direct CISO to CEO).

## Context
A P1 security event (for example, an unexpected outbound connection or a compromised agent) must reach the CEO even if the COO is down, busy, or compromised.

## Decision
A P1 event goes from the CISO directly to the CEO. It bypasses the COO and the event bus. The CISO sends the message through its own channel, not through the COO.

## Alternatives rejected
- COO-mediated delivery: the COO can be the thing that failed.
- COO-mediated with a CISO fallback (option b in the review): rejected by the CEO in favour of a direct path.

## Consequences
- The CEO needs a direct channel from the CISO. The P1 criteria are defined in ops/notification-strategy.md (to be written).
- A P1 event must be logged in the audit trail, the same as any other event.
