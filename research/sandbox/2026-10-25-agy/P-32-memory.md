# P-32 Design: Loop 2 Memory Architecture

**Document**: `sandbox/P-32-memory.md`  
**Status**: Proposal (Draft)  
**Governing Approvals & Decisions**:  
- P-32 (`decisions/PENDING.md#L35-L40`)  
- APR-0061 (Memory search and dreaming turned off for Loop 1)  
- APR-0059 (Daily session reset at 04:00 AST)  
- APR-0063 (CEO addresses any agent; COO is normal routing door)  
- ADR-0003 (Privacy gate in code)  
- ADR-0011 (Append-only history, projected state)  
- ADR-0015 (Repo, runtime, seed separation)  
- Loop 1 Run 014 Findings (`tests/scenario/bad-sleep-reschedule.md#L62`, `deploy/loop1/STATE.md#L84`, `deploy/loop1/LOOP1-CLOSE-RECORD.md#L31`)  
**Verification Standard**: Every factual claim cites file and line or command output, or is labeled "not verified".

---

## 1. Executive Summary and The Run 014 Finding

During Loop 1, test run `loop1-scn-014` revealed a fundamental architectural discovery regarding agent memory:

### 1.1 The Run 014 Incident Analysis
- **Incident Record**: `tests/scenario/bad-sleep-reschedule.md#L62`:
  > "First attempt started during a gateway restart; the COO's wait failed. The run ID was then reused after a state reset. The CHO answered from its own session memory of run 013 ('already handled'), wrote no journal change, and logged an event ID (loop1-scn-014-cho-01) that health-plan.md does not contain. The COO's late reply gave the wrong sleep date (2026-10-23). A git state reset and a one-line session compaction do not clear agent memory."
- **Root Cause Identification**:
  1. **Decoupled State Layers**: `git checkout -- state/` resets workspace files tracked in git (`state/health-plan.md`, `state/calendar-journal.md`). However, OpenClaw stores conversational turn histories in SQLite databases (`~/.openclaw` or `~/loop1/state/openclaw.json` / SQLite session store).
  2. **Incomplete Compaction**: The reset command `openclaw sessions compact "agent:<id>:main" --max-lines 1` compacted only the primary interactive session string, but did not purge background session tables, child session transcripts, or KV-cache references.
  3. **Conversational Hallucination vs. Projected State**: When the run ID was reused, the CHO LLM looked into its conversational memory, saw that the sleep reschedule task had been executed in run 013, hallucinated that the task was "already handled", fabricated an event ID not present in `health-plan.md`, and skipped writing to disk.

### 1.2 Core Architectural Invariant for Loop 2
> **Rule**: Agent memory is distinct from filesystem state. Agents must NEVER treat conversational history as the source of truth. All domain facts, confirmations, and event deductions must be grounded strictly in append-only projected state files (`state/*.md`), verified via file reading tools. Reusing run IDs is strictly prohibited across all loops (`deploy/loop1/STATE.md#L36`).

---

## 2. Memory Tiering Architecture

LifeOS implements a four-tiered memory hierarchy that balances immediate operational context, local privacy, deterministic state tracking, and cost:

```
+-----------------------------------------------------------------------------------+
| Tier 1: Ephemeral Working Context (The Active Turn)                               |
| - In-memory conversation buffer, current task messages, active system prompt.      |
| - Controlled via APR-0059 (04:00 daily reset) and lean message payloads.         |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
| Tier 2: Domain Projected State Files (Deterministic Truth)                        |
| - Markdown state files: health-plan.md, calendar-journal.md, budget.md.           |
| - Append-only, tracked in workspace git; the ONLY source of truth for facts.      |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
| Tier 3: Curated Long-Term Memory (MEMORY.md)                                      |
| - Explicit, curated personal rules, preferences, and verified patterns.           |
| - Maintained via CKO/CSTO oversight; no autonomous rewriting or dreaming.         |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
| Tier 4: Immutable Audit & Event Log (Durable History)                             |
| - LLM Call Log (APR-0047), Gateway logs, File Event Bus (ADR-0008).              |
| - Append-only, audited weekly by CISO (APR-0049).                                 |
+-----------------------------------------------------------------------------------+
```

---

## 3. Resolving the P-32 Open Questions

### 3.1 What Each Agent Should Remember Beyond State Files
- Agents should NOT accumulate raw transcripts of past conversations.
- **What belongs in `state/*.md`**: Objective current operational facts (active workout schedule, unpushed calendar events, active budget balances).
- **What belongs in `MEMORY.md`**:
  - Stable user preferences (e.g. "CEO prefers workouts in the morning", "CEO takes Vitamin D with breakfast").
  - Architectural operational constraints (e.g. "Do not post in `#general`", "Event IDs must follow APR-0034").
  - Recurring patterns validated by the CEO.
- **What is explicitly excluded**: Ephemeral run IDs, temporary task payloads, speculative inferences, and unverified conversational claims.

### 3.2 Where Memory Lives
- **Storage Location**: Inside each agent's runtime workspace (`~/loop2/workspaces/<agent>/`).
- **File Hierarchy**:
  - `~/loop2/workspaces/<agent>/MEMORY.md`: Long-term curated knowledge.
  - `~/loop2/workspaces/<agent>/state/`: Append-only domain journals and state.
  - Runtime SQLite databases: Confined strictly to OpenClaw session mechanics; treated as volatile cache that can be blown away or reset at 04:00 AST without loss of LifeOS state.

### 3.3 Semantic Search, Embeddings, and the Privacy Gate (ADR-0003, APR-0061)
- In Loop 1, OpenClaw's `memory.search.enabled` sent 115 embedding requests directly to OpenAI (`decisions/APPROVALS.md#L515-L516`). This violated ADR-0003 because unredacted agent context bypassed the local privacy gate.
- Furthermore, OpenClaw's `dreaming` feature executes nightly unprompted LLM runs that rewrite memory files, directly violating the append-only history requirement of ADR-0011.
- **Loop 2 Mandate**:
  1. `memory.search.enabled` remains **false** for cloud providers.
  2. `plugins.entries.memory-core.config.dreaming.enabled` remains **false**.
  3. When semantic search is introduced in Loop 2, it MUST use a local embedding model (e.g. `nomic-embed-text` or `bge-small` running locally on the VM or host) behind the ADR-0003 privacy gate.
  4. Memory consolidation must be deterministic and append-only, curated by the Chief Knowledge Officer (CKO) and Chief System & Technology Officer (CSTO), never by opaque autonomous model dreaming.

### 3.4 Append-Only Invariant and State Reconstruction (ADR-0011)
- Under ADR-0011, agent state is a deterministic projection of historical events:
  $$\text{Current State} = \text{Fold}(\text{Initial State}, \text{Event Stream})$$
- When an agent initializes or starts a turn, it reads its `state/*.md` file. It does not rely on what it "remembers" saying three turns ago.
- All state updates append new lines to state files. Editing or deleting past history is prohibited.

---

## 4. COO Context Explosion and Token Hygiene (APR-0063)

### 4.1 The 35,000 Token Prompt Problem
In Loop 1 Slack runs (`guides/loop1-baseline.md#L185`, `decisions/PENDING.md#L39`), the COO's prompt reached **~35,000 tokens** on a single turn (out of a 272,000 token window).
- **Cause**: The COO acts as the central router (`decisions/APPROVALS.md#L535-L547`). Because it retained transcripts of all child agent conversations (CHO, CoS, CFO), its context ballooned rapidly. At cloud LLM pricing, 35,000-token prompts make repeated routing turns economically unsustainable ($0.047/run vs $0.05 limit, APR-0056).

### 4.2 Mitigation Rules for Loop 2
1. **Shallow Inter-Session Handoffs**:
   - When routing, the COO passes only the immediate objective and parameters inline (instruction set v1.5, APR-0066).
   - The COO does not retain the full multi-turn internal reasoning of the chiefs.
2. **Result Summaries Only**:
   - The receiving chief (e.g. CHO or CoS) executes the domain work, writes to its local state file, and returns a concise, single-sentence outcome with the Event ID to the COO (instruction set v1.4, APR-0065).
   - The COO receives only the summary line and reports it to the CEO.
3. **Delegation Over Ingestion**:
   - The COO never queries its own conversation history for domain answers. If asked "What is my sleep plan?", the COO routes the inquiry to the CHO rather than answering from stale routing memory.
4. **Scheduled 04:00 AST Session Hygiene (APR-0059)**:
   - All agent session contexts reset automatically every morning at 04:00 AST, preventing multi-day conversational bloat while state remains preserved in `state/*.md`.

---

## 5. Verification and Testing Plan

1. **State Reset Independence Drill**:
   - Replicate the run 014 failure mode in a synthetic harness:
     1. Seed a state file with an event.
     2. Run a query that references the event.
     3. Perform a git reset of the state file.
     4. Query the agent again with the same prompt and a fresh run ID.
     5. Verify that the agent inspects the state file, recognizes the event is absent, and acts on the current file rather than asserting prior completion.
2. **Embedding Privacy Leakage Audit**:
   - Monitor outbound network traffic during memory operations.
   - Assert 0 outbound HTTPS calls to external embedding endpoints (OpenAI / third-party), verifying compliance with ADR-0003 and APR-0061.
3. **COO Token Cap Canary**:
   - Measure COO prompt token counts across a 5-step scenario cascade.
   - Verify that COO turn prompts remain $< 10,000$ tokens throughout the workflow.
