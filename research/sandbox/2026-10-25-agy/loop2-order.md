# Proposed Execution Sequence for Loop 2 Open Items

**Status**: Proposal  
**Needs CEO**: yes  
**Reference Decisions**: APR-0071 (Loop 1 close), P-26, P-28, P-31, P-32, P-36, P-37  
**Proposals Recorded**: SD-008, SD-009, SD-010 in `sandbox/SANDBOX-DECISIONS.md`

---

## 1. Overview and Principles

With Loop 1 closed under APR-0071, all temporary suspensions from ADR-0018 and APR-0052 have expired. The OpenClaw gateway on the Oracle VM remains strictly stopped. Before Loop 2 operations can begin, several architectural, financial, and operational prerequisites must be established in strict dependency order.

The proposed sequencing follows three core engineering principles:
1. **Safety and Governance First**: No live agents or gateway processes run without legal APR authorization and an automated cost kill-switch.
2. **Determinism Before External Systems**: Agent memory invariants and prompt hygiene must be locked down before connecting external write sinks (Google Calendar).
3. **Privacy Wins Over Convenience**: Features requiring unbuilt privacy infrastructure (such as Slack file uploads) remain deferred.

---

## 2. Proposed Sequential Order

```
[Phase 0: Authorization]
  Step 1: Loop 2 Framework APR & P-37 Formal Close
      │
      ▼
[Phase 1: Financial Guardrails]
  Step 2: P-31 Cost Hard-Stop Kill Switch
      │
      ▼
[Phase 2: Agent Memory & Prompt Invariants]
  Step 3: P-32 Memory Invariants & COO Context Hygiene
      │
      ▼
[Phase 3: Lifecycle Verification]
  Step 4: P-36 Daily 04:00 AST Reset Verification
      │
      ▼
[Phase 4: External Systems Integration]
  Step 5: P-28 Calendar Sync Engine (Google Calendar)
      │
      ▼
[Phase 5: Deferred Capabilities]
  Step 6: P-26 Slack files:read Scope (Deferred)
```

---

## 3. Step-by-Step Breakdown and Prerequisites

### Step 1: Loop 2 Framework Authorization & P-37 Resolution
- **Target Items**: Loop 2 Runtime Authorization (SD-010) & P-37 Closure (SD-001).
- **Prerequisites**:
  - CEO review of `deploy/loop1/LOOP1-CLOSE-RECORD.md` and `sandbox/SUMMARY.md`.
  - Resolution of P-37 findings (`sandbox/P-37-findings.md`): P-37 is closed with zero code changes needed.
  - New APR entry establishing Loop 2 operational boundaries: whether Loop 2 continues on synthetic data, whether cloud-only exception is extended or hybrid local routing is tested, and un-suspending or continuing suspension of specific rules.
- **Deliverable**: New APR entry in `decisions/APPROVALS.md` authorizing gateway startup for Loop 2; P-37 marked closed in `decisions/PENDING.md`.

---

### Step 2: P-31 Cost Hard-Stop Kill Switch (APR-0056)
- **Target Item**: P-31 (Cost hard stop).
- **Why It Must Be Done Here**:
  - In Loop 1, cost tracking was deferred because the OpenAI usage dashboard lagged by 5–20 minutes (`deploy/loop1/STATE.md#L97`).
  - No autonomous or multi-agent runs should be executed in Loop 2 without a reliable, real-time stop mechanism enforcing the $0.05/run and $1.00/day limits.
- **Prerequisites**:
  - Step 1 complete.
  - Implementation of local token tallying via OpenClaw call logs / turn telemetry (`sandbox/P-31-cost-hard-stop.md`).
  - Implementation of gateway shutdown trigger and `COST_KILL_ACTIVATED.lock` mechanism.
- **Verification**: Offline unit test simulating token overrun triggering immediate process termination and lockfile generation.

---

### Step 3: P-32 Memory Design and Prompt Invariants (ADR-0011, APR-0061, APR-0063)
- **Target Item**: P-32 (Loop 2 memory architecture).
- **Why It Must Be Done Here**:
  - Run 014 proved that OpenClaw's internal session cache retains conversational memory across git state resets and compaction.
  - COO prompt reached ~35,000 tokens during scenario routing, creating cost and context pressure.
- **Prerequisites**:
  - Step 2 complete (cost guard in place).
  - Adoption of SD-005 (cloud embeddings and dreaming remain off; local embeddings only if needed).
  - Adoption of SD-006 (instruction invariant: agents must verify state files on disk before reporting state).
  - Adoption of SD-007 (COO shallow handoffs: summary routing without nested transcripts).
- **Deliverable**: Update workspace `AGENTS.md` instruction files with instruction set v2.0 reflecting state-grounding and shallow handoff rules.

---

### Step 4: P-36 Daily 04:00 AST Session Reset Verification
- **Target Item**: P-36 (04:00 AST reset drill).
- **Why It Must Be Done Here**:
  - Loop 1 used manual one-line compaction (`openclaw sessions compact`) between scenario runs because the daily reset had not been empirically verified.
  - Loop 2 requires automated long-running stability without manual operator intervention.
- **Prerequisites**:
  - Step 3 complete (agents running with instruction set v2.0).
  - Gateway running across a 04:00 AST boundary.
- **Action**: Run the verification procedure defined in `guides/loop1-baseline.md#L140-L150`: send an inbound message after 04:00 AST, compare session IDs before and after, and verify session rollover occurred cleanly without losing uncommitted state.
- **Deliverable**: Close P-36 in `decisions/PENDING.md`.

---

### Step 5: P-28 Calendar Sync Engine (Google Calendar Integration)
- **Target Item**: P-28 (Calendar journal to Google Calendar sync).
- **Why It Must Be Done Here**:
  - In Loop 1, all calendar operations wrote only to `state/calendar-journal.md`. Google Calendar writes (APR-0031) were suspended.
  - Sync must be handled by deterministic code running outside the model (ADR-0008, ADR-0011).
- **Prerequisites**:
  - Steps 1–4 complete.
  - Valid Google Calendar OAuth token on VM (`guides/calendar-gcalcli.md`).
  - Sync daemon implementation (`scripts/calendar-sync.py`, SD-003 direct REST client).
  - Implements S-06 (5-minute polling daemon), S-07 (token revocation hold and CIO alert), APR-0034 (search-before-write idempotency), APR-0057 (two-line moves), and APR-0044 (delete-pending-approval hold).
  - Implementation of SD-004 (monthly archival of events older than 14 days to `state/archive/calendar-YYYY-MM.md`).
- **Deliverable**: Live integration test proving journal append moves cleanly sync to Google Calendar with zero duplicate entries.

---

### Step 6: P-26 Slack `files:read` Scope (Deferred)
- **Target Item**: P-26 (Slack file attachments).
- **Status**: Deferred (SD-008).
- **Prerequisites**:
  - Implementation of in-code privacy gate (`src/lifeos/router/gate.py`, ADR-0003) and passing unit tests (`tests/unit/test_gate.py`).
  - Local OCR / vision processing model runtime (deferred under SPK-06 and APR-0070).
- **Action**: Maintain current configuration (no `files:read` scope). Instruct agents to inform users that file uploads are disabled for privacy protection until the local privacy gate is deployed.

---

## 4. Summary Table

| Step | Item | Primary Focus | Key Prerequisite | Blocking For |
|---|---|---|---|---|
| **1** | Loop 2 Auth & P-37 | Framework APR & P-37 close | CEO sign-off on Loop 1 close | All Loop 2 execution |
| **2** | P-31 | Cost hard-stop kill switch | Turn token accounting logic | Any live agent scenario |
| **3** | P-32 | Memory invariants & COO hygiene | SD-005, SD-006, SD-007 approval | Multi-turn scenario runs |
| **4** | P-36 | 04:00 AST reset drill | Instruction set v2.0 deployed | Unattended overnight ops |
| **5** | P-28 | Google Calendar sync engine | OAuth tokens + `calendar-sync.py` | Live external sync |
| **6** | P-26 | Slack `files:read` scope | ADR-0003 privacy gate (`gate.py`) | Multimodal attachments |
