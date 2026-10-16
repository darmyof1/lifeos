# ADR-0002 - Dual authority: operational (COO) and constitutional (CSTO)

Status: accepted
Date: 2026-10-16
Approval basis: APR-0042 (CEO approved the text, including the tie-break). Source: MANIFEST / SOVEREIGN_LIFE_OS.md sections 2.2 and 3.2.

## Context
The system has two kinds of authority. Daily execution needs one owner for routing and coordination. The rules everything runs by need a separate owner. Without a clear split, a routing decision could change the rules, or a rule could block daily work with no one answerable for it.

## Decision (proposed)
- Operational authority belongs to the COO. It directs daily execution, task routing, reporting lines, and session coordination across chiefs.
- Constitutional authority belongs to the CSTO (Aurelius). It holds the system constitution, defines SOPs, audits memory, and enforces structural and philosophical rules. The CSTO may veto a plan that violates those rules.
- Neither authority outranks the other. They are orthogonal.
- The CEO holds final authority and veto over both.
- Exception: the CISO reports operationally to the COO but may escalate critical security events directly to the CEO (ADR-0007, APR-0008).
- The CoS has decision authority for conflicts between departments (manifest section 2.2).

## Tie-break (approved, APR-0042)
When the CSTO vetoes a COO plan, the plan stops and the CEO decides. Nothing runs until the CEO answers.

## Alternatives rejected
Not recorded in the sources available to this repository. The CEO should add any alternatives considered before approving.

## Consequences
- A plan that changes both routing and rules needs both authorities to agree, or the CEO decides.
- The CSTO veto has no written procedure yet. design/authority-and-roles.md is empty.
- Scenario S-12 in design/scenarios.md tests this rule.
