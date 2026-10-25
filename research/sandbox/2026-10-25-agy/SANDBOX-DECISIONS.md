# Sandbox Decisions (Proposals & APR Reconciliation)

These entries record architectural questions, reconciliation against governing approvals (APRs), and proposals for CEO review.
Per directive: Where an APR already decides the question, it is cited as binding and proposals on settled matters are stopped.

---

## SD-001 - Resolution of P-37 (COO SQLite maintenance warnings)
- **Status**: Proposal (Open question)
- **APR Check**: APR-0071 moved P-37 to Loop 2 (`decisions/APPROVALS.md#L641`). No APR has decided whether to modify code, config, or accept diagnostic warnings.
- **Question**: How should the COO SQLite maintenance warning and slow reservation warning (P-37) be handled for Loop 2?
- **Options**:
  - Option A (Recommended): Accept as normal OpenClaw background optimistic concurrency retry behavior. Close P-37 with no changes to config or code.
  - Option B: Attempt to suppress the warning or modify OpenClaw's internal maintenance scheduling/reclamation logic.
- **Choice**: Option A.
- **Why**: Code analysis of OpenClaw 2026.10.5 in `session-accessor.sqlite-entry-DLM4ONjh.mjs` and `openclaw-agent-write-admission-CBidmy8j.mjs` shows:
  1. "slow agent database reservation" is a diagnostic log emitted whenever write admission execution time $\ge 1000$ ms; it completed with outcome `ok` and does not retry.
  2. "SQLite automatic maintenance activity changed before age consumption" is a deliberate optimistic concurrency check: when active messages write to SQLite while background maintenance is planning, the maintenance job aborts with `SqliteReclamationInputsChangedError` and executes immediate retries (`await runPendingMaintenance(...)`, verified at lines 426–438) up to `MAX_MAINTENANCE_REJECTIONS = 3` before applying a 1-second quiet backoff. No messages or states are lost.
- **Needs CEO**: yes

---

## SD-002 - Cost Hard-Stop Mechanism and Kill-Switch Architecture (P-31 / APR-0056)
- **Status**: **Already decided in part by APR-0056 — Stop proposing limits.**
- **APR Citations**:
  - `APR-0056` (`decisions/APPROVALS.md#L453-L462`):
    - *Line 458*: "Each scenario run has a ceiling of 0.05 USD. A run that reaches it stops and is recorded as a failure." (**Decided: 0.05 USD run ceiling and run-stop rule**).
    - *Line 459*: "Provider alert at 1 USD per day; monthly limit of 5 USD for the life-os project." (**Decided: 1.00 USD/day alert and 5.00 USD/mo limit**).
- **Where APR-0056 already decides**: The financial limits ($0.05/run, $1.00/day, $5.00/month) and the mandate that a run reaching $0.05 stops as a failure are binding decisions. We stop proposing alternate thresholds.
- **Remaining Open Question (P-31)**: How should spend be monitored and stopped in code given that the OpenAI usage dashboard/API lags by 5–20 minutes?
- **Implementation Proposal**:
  - Implement two-tier tracking: (1) real-time local token counting via APR-0047 call logs / OpenClaw turn telemetry for instant per-run ($0.05) abort and daily ($1.00) enforcement; (2) asynchronous provider usage API polling for reconciliation. At $0.05/run, abort the scenario run; at $1.00/day, kill the gateway process and write `COST_KILL_ACTIVATED.lock`.
- **Needs CEO**: yes (on implementation mechanism only; thresholds are approved)

---

## SD-003 - Google Calendar Sync Driver (P-28)
- **Status**: **Already decided in part by APR-0031, APR-0041, APR-0043, APR-0044, APR-0057 — Stop proposing parameters.**
- **APR Citations**:
  - `APR-0031`: Google Calendar is the calendar store.
  - `APR-0041`: Google Calendar OAuth token lives at `~/.local/share/gcalcli/oauth` on the VM (mode 600).
  - `APR-0043`: Scenario S-06 mandates 5-minute retries and escalation to COO/CEO after 5 failures. Scenario S-07 mandates CIO alert on token revocation.
  - `APR-0044`: CoS is the only writer; adds go straight to CoS; deletes require CEO approval.
  - `APR-0057`: Calendar moves are two lines (not deletes).
- **Where APRs already decide**: S-06 (5-minute retry, 5-failure escalation), S-07 (CIO alert), APR-0044 (delete approvals), and APR-0057 (two-line moves) are binding approved rules. We stop proposing changes to sync cadence, retry counts, or move/delete logic.
- **Remaining Open Question (P-28)**: Should the background calendar sync engine (`calendar-sync.py`) interact with Google Calendar via the `gcalcli` CLI wrapper or via direct Google Calendar API (REST / Python client)?
- **Choice**: Direct Google Calendar REST API via Python client using stored OAuth credentials (`~/.local/share/gcalcli/oauth`).
- **Why**: Direct API calls provide structured JSON responses containing precise Google event IDs, status codes (401, 409, etc.), and error payloads without brittle regex scraping of terminal formatting.
- **Needs CEO**: yes (on driver mechanism only)

---

## SD-004 - Active Calendar Journal Archival Window (P-28)
- **Status**: Proposal (Open question)
- **APR Check**: APR-0054 and APR-0058 established the append-only journal in `state/calendar-journal.md`. Archival retention threshold is an open question.
- **Question**: What retention window should determine which completed events remain in the active `calendar-journal.md` before being moved to monthly archives?
- **Choice**: Option A (Recommended): Keep all future events, any unpushed/unconfirmed events, and completed events from the past 14 days. Archive older completed entries monthly to `state/archive/calendar-YYYY-MM.md`.
- **Why**: Keeps active journal small (< 200 lines / ~3,000 tokens), preventing token bloat when CoS reads its state on every calendar turn, while preserving complete history in git.
- **Needs CEO**: yes

---

## SD-005 - Semantic Memory and Embedding Privacy in Loop 2 (P-32 / APR-0061)
- **Status**: **Already decided by APR-0061, ADR-0003, and ADR-0011 — Stop proposing cloud embeddings or dreaming.**
- **APR Citations**:
  - `APR-0061` (`decisions/APPROVALS.md#L510-L521`): "memory.search.enabled is false and plugins.entries.memory-core.config.dreaming.enabled is false. Memory search sends agent text to OpenAI for embeddings (115 requests on 2026-10-23), a cloud path outside the privacy gate (ADR-0003). Dreaming is a nightly model sweep that rewrites agent memory, which conflicts with append-only history (ADR-0011)."
  - `ADR-0003`: "A high-privacy request cannot reach a cloud adapter... No cloud adapter may be enabled until gate.py exists and its unit tests pass."
  - `ADR-0011`: All history is append-only; projected state.
- **Where APRs already decide**: Enabling OpenClaw cloud embeddings or autonomous model dreaming is **ALREADY REJECTED AND FORBIDDEN**. We stop proposing cloud embeddings or dreaming.
- **Remaining Open Question (P-32)**: How long-term recall should be implemented in Loop 2.
- **Implementation Proposal**: Keep cloud embeddings and dreaming disabled. If semantic search is needed in Loop 2, deploy a local embedding model behind the ADR-0003 privacy gate. Maintain memory consolidation via CKO/CSTO oversight.
- **Needs CEO**: yes (on local embedding roadmap)

---

## SD-006 - State Grounding Invariant (Run 014 Finding / ADR-0011)
- **Status**: Proposal (Open question)
- **APR Check**: APR-0054/0058 established that domain state is stored in state files. Run 014 proved that OpenClaw's internal session cache retains memory across state resets. Adding an explicit instruction invariant to `AGENTS.md` is an open proposal for instruction set v2.0.
- **Question**: How should agent instructions ensure agents do not answer from stale conversational memory after a state reset?
- **Choice**: Option A (Recommended): Add an explicit instruction invariant to all agents: agents must always verify facts and status by reading their domain `state/*.md` files before answering, and must never assert state changes based solely on conversation history or prior turns. Prohibit run ID reuse.
- **Needs CEO**: yes

---

## SD-007 - COO Context Hygiene and Routing Boundaries (P-32 / APR-0063)
- **Status**: **Routing role decided by APR-0063; context accumulation open in P-32.**
- **APR Citations**:
  - `APR-0063`: The CEO may message any agent in its own channel at any time, but normally talks to COO who routes. "How much context the COO builds up when it routes everything is a design question, kept open in P-32."
  - `APR-0064` & `APR-0066`: COO waits for reply and answers once; COO carries whole task in handoff.
- **Remaining Open Question (P-32)**: How should the COO prevent token context explosion (~35,000 tokens per prompt) during routing?
- **Choice**: Option A (Recommended): Enforce shallow handoffs: COO transmits only the immediate request parameters to chiefs, chiefs execute domain logic in their state files and return single-sentence summaries with Event IDs to the COO, and COO does not retain internal multi-turn transcripts of chiefs. Daily 04:00 reset (APR-0059) clears accumulated routing history.
- **Needs CEO**: yes

---

## SD-008 - Slack `files:read` Scope (P-26)
- **Status**: **Cloud scope without privacy gate already forbidden by ADR-0003, APR-0007, APR-0045 — Stop proposing cloud scope.**
- **APR Citations**:
  - `APR-0007`: "Privacy wins over complexity. A critical-complexity request with high privacy stays local."
  - `ADR-0003`: "The privacy gate is a function in src/lifeos/router/gate.py... A high-privacy request cannot reach a cloud adapter... No cloud adapter may be enabled until gate.py exists and its unit tests pass."
  - `APR-0045`: Slack exemption allows posting to private Slack channels only; "It does not allow sending that data to a cloud model: the privacy gate still applies (APR-0007)."
  - `decisions/PENDING.md#L18`: "Proposed: do not add files:read. Attachments would reach the cloud model with no privacy gate (ADR-0003). Revisit after the privacy gate exists."
- **Where APRs already decide**: Adding `files:read` to cloud models without an in-code privacy gate directly violates ADR-0003, APR-0007, and APR-0045. We stop proposing Option B (granting scope to cloud models).
- **Proposal**: Keep `files:read` deferred (Option A). Revisit only after an in-code privacy gate (`gate.py`) and local sanitization pipeline exist.
- **Needs CEO**: yes (to confirm continued deferral)

---

## SD-009 - Loop 2 Implementation Sequence and Open Item Order
- **Status**: Proposal (Open question)
- **APR Check**: APR-0071 moved open items (P-26, P-28, P-31, P-32, P-37) to Loop 2. The dependency execution order was not specified.
- **Choice**: Option A (Recommended): Follow dependency-ordered sequence:
  1. Loop 2 Framework Authorization & P-37 Close (SD-001, SD-010)
  2. P-31 Cost Hard-Stop Kill Switch (APR-0056)
  3. P-32 Memory Invariants and COO Context Hygiene (SD-005, SD-006, SD-007)
  4. P-36 Daily 04:00 AST Session Reset Drill
  5. P-28 Calendar Sync Engine (Google Calendar REST, SD-003, SD-004)
  6. P-26 Slack `files:read` Scope (Deferred, SD-008)
- **Why**: Establishes safety, financial boundaries, and deterministic memory before enabling external synchronizations or autonomous runs.
- **Needs CEO**: yes

---

## SD-010 - Loop 2 Runtime Authorization and Exception Framework
- **Status**: **Already decided by APR-0071 — Stop proposing gateway restart without an APR entry.**
- **APR Citations**:
  - `APR-0071` (`decisions/APPROVALS.md#L638-L643`):
    - "Loop 1 is closed on 2026-10-25. The close record is deploy/loop1/LOOP1-CLOSE-RECORD.md."
    - "APR-0052 and ADR-0018 expire now. The entries APR-0052 suspended apply again (APR-0018, APR-0021, APR-0051, APR-0031, APR-0047, APR-0049, and the router path of ADR-0003 and ADR-0004), unless a new APR entry changes them."
    - "The Loop 1 agents ran on openai/gpt-6-luna only under that exception, so the Loop 1 gateway stays stopped. Running the agents again needs a new APR entry."
- **Where APR-0071 already decides**: Running agents or restarting the gateway without a new APR entry is **ALREADY STRICTLY FORBIDDEN**.
- **Proposal**: CEO drafts a new APR entry establishing Loop 2 parameters (synthetic vs personal data scope, cloud model exception status, active rules) before gateway startup is authorized.
- **Needs CEO**: yes
