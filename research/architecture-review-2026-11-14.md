# LifeOS architecture review (2026-11-14)

Status: FOR LATER REVIEW. Stored as received. No decision is recorded and nothing here is approved (see decisions/APPROVALS.md). The "Proposed entries" at the end are suggestions only, not APR or P entries.

Origin: independent review requested by the CEO on 2026-11-14, written by Fable from the build briefing of the same date (claude/fable-briefing-2026-11-14.md in the LifeOS project). Repo files marked "verify" in the briefing were not opened; the claims rest on the briefing and the published sources checked. Copy of the CEO's document "LifeOS architecture review (2026-11-14)".

## Verdict

Collapse LifeOS to one agent with three typed tools and a deterministic calendar writer. The five-agent split is not justified by a workload of log, look up and schedule for one user, and seven of the nine logged problems are consequences of that split rather than bugs inside it.

Keep the audit log, the delete gate and the backups. Replace loop closure by test count with one metric: real requests completed end to end in a week. Rebuild estimate: 3 to 5 working days, then a 7-day measurement.

## Source check

The briefing's facts hold; the review prompt and one citation need correcting.

| Item | Finding | Action |
|---|---|---|
| MAST percentages in the prompt (42 / 37 / 21) | Figure 4 subset (210 traces). The full dataset (1,642 traces) gives 44.2 / 32.3 / 23.5. | State which figure is cited. |
| MAST venue | Confirmed: NeurIPS 2025 Datasets and Benchmarks Track. Taxonomy built from 150 hand-annotated traces; MAST-Data holds 1,600+ traces over 7 frameworks. | Drop the "verify venue" flag. |
| "Compounding error decay" and "runaway loops" in the prompt | Not claims of the MAST paper. | Keep as engineering concerns, not citations. |
| Anthropic citation | Two posts conflated. 27M vs 6.5M tokens (266 vs 21 findings, 45 agents) is from the Frontier Red Team post of 2026-08-13. "Interdependent work does poorly" and "about 15x tokens" are from the earlier research-system post. The swarm comparison is not like-for-like: budgets and search scope differed. | Split into two citations. |
| Prompt template placeholders | The `[Insert ...]` fields were unfilled. Filled in the review from the briefing. | None. |
| "Model: OpenClaw 2026.10.5 gateway" | Names the gateway, not the model. Section 3 of the briefing implies Claude. | State the model in the briefing. |
| Medium article (raghunitb) | Not fetched by the briefing author; not used here. | Remove from sources. |

Sources:
- Cemri et al., arXiv 2503.13657 (v3): https://arxiv.org/abs/2503.13657v3
- NeurIPS 2025 poster: https://neurips.cc/virtual/2025/poster/121528
- Anthropic, Patterns and problems in emerging multiagent systems (summary): https://ai-tldr.dev/releases/anthropic-multiagent-patterns-problems/
- Anthropic research-system post (summary): https://blog.bytebytego.com/p/how-anthropic-built-a-multi-agent

## MAST mapping of the known problems

System design dominates: 6 to 7 of 9 problems. Verification accounts for 3. The inter-agent misalignment seen in handoffs is downstream of incomplete specs, not a coordination problem in its own right.

| # | Problem (briefing section 4) | MAST mode | Category |
|---|---|---|---|
| 1 | COO routed TV log + appointment to CHO; CLO missing from routing table; nothing written | 1.1 disobey task spec, 1.2 disobey role spec; 3.2 no verification of the write | Design (root), Verification |
| 2 | CLO calendar requests stuck "queued" live; CLO had no handoff rule | 2.4 information withholding, caused by a missing spec | Design, shows as Misalignment |
| 3 | CHO and CoS sessions at 183 and 300 messages; COO needed compaction (4/6 vs 6/6) | 1.4 loss of conversation history | Design |
| 4 | 04:00 reset fires only on human inbound; agent-to-agent traffic never resets | 1.5 unaware of termination conditions | Design |
| 5 | Regression checks test wording; 4 false failures on correct answers | 3.3 incorrect verification | Verification |
| 6 | Privacy is prompt text and labels; gate in shadow mode | 1.1 spec that cannot be enforced; a security gap outside MAST | Design |
| 7 | Isolation is one flag (fs.workspaceOnly); A2A route leaked CoS journal to CLO | Trust boundary at the wrong layer | Design |
| 8 | CEO relays between planning chat, Claude Code and Slack; two secret leaks | Human as the message bus; outside MAST | Design |
| 9 | Loops closed on test counts; first real request failed after Loop 7 "ready" | 3.2 no or incomplete verification of the outcome | Verification |

Do not compare these counts with the paper's percentages: n = 9 from one system says where this system's leverage is, and it is in the architecture. The paper's own intervention study found that better role specs and orchestration gave modest gains and that the failures need deeper solutions. For this system, the deeper solution is removing the coordination surface, not tuning it.

## Multi-agent vs single agent

One agent with typed tools is enough for this work, and safer. The evidence:

- The workload is three verbs (log, look up, schedule) over small, sequential, dependent requests. Multi-agent pays off only when work is separable and parallel; Anthropic's own data shows gains for breadth-heavy search and losses for interdependent tasks. "Log this episode and book Tuesday" is one request with two dependent writes.
- Every observed failure sits at a boundary between agents: COO to CHO, CLO to CoS, agent-to-agent reset, agent-to-agent journal leak. Remove the boundaries and the failure class disappears instead of being mitigated.
- Each hop re-reads a 180- to 300-message channel session, so one request is paid for two or three times at full context.
- The chiefs are personas, not capabilities. No chief needs a different model, different tools or a different trust level, except the calendar push, which is already a job and not an agent.

What collapsing sacrifices:

| Lost | Weight | Replacement |
|---|---|---|
| Per-domain Slack identities | Cosmetic | One app; domain shown in the reply |
| Blast-radius separation between domains | Real, but today it is one flag | Tool-level scoping and field allowlists (Privacy section) |
| Option to run domains on different models | No evidence of need | Model per tool call is still possible in one agent |
| Domain specialisation | None lost | Tool namespaces and system-prompt sections |

Keep the multi-agent option only as "a second agent that never shares a session with the first" for a workload that is really parallel. None exists today.

## Smallest reliable architecture

One Slack app, one deterministic handler, one model call per request with three strict tools, a code verifier, and a cron job that pushes approved events. No agent talks to an agent.

Request path (8 components, 1 model call):

    Slack (one app)
      -> request handler (Python, deterministic): fresh context = request text + retrieved state slice
      -> Claude (one call, tool use, at most N tool rounds)
           tools (strict JSON schema):
             log_item(kind: enum, fields...)       -> SQLite, append-only
             lookup(kind, filter)                  -> read-only query
             propose_event(title, start, end, cal) -> PENDING queue
      -> verifier (code): did the write land? does the event parse? then reply
      -> push job (cron, no model): approved PENDING -> Google TEST calendar

The model only reads and proposes; every write that matters is done or checked by code, and nothing in the picture talks to another model.

Keep:
- APPROVALS.md audit log, now written by the handler, not by agents.
- Delete gate: any destructive tool call requires a Slack approval button.
- Encrypted weekly backup with the proven restore.
- The privacy gate, promoted from prompt text into code (next section).

Remove:
- COO, CHO, CoS, CFO and CLO as agents, and their four extra Slack apps.
- All agent-to-agent routes.
- Channel-session memory and the 04:00 reset machinery. Each request gets a fresh context assembled from the store, so problems 3 and 4 vanish by construction.
- fs.workspaceOnly as the isolation mechanism: one process, one folder, nothing to isolate.
- Text-heuristic regression checks, replaced by state assertions ("after request R, row X exists with fields Y").
- Most of the ~150 fix scripts become dead. Keep the registry only as a data schema.

Four hardening fixes:

1. External, schema'd state. Markdown append-only files become SQLite with one schema per `kind` and an idempotency key per request (the Slack message `ts`). Retries cannot double-write; lookups are queries, not model reads of a 300-line file.
2. Hard turn caps, no agent-initiated turns. At most 6 tool rounds per request, one model chain per Slack message, zero model calls without a human inbound. This is also the runaway-cost guard.
3. Deterministic verification loop. After the model finishes, code checks the postcondition (row exists, event queued, lookup returned at least one row) and only then replies "done". Otherwise it replies "failed" with the reason. This fixes problem 9.
4. Side effects out of the model's hands. The model only proposes events; the cron job pushes. The calendar ID is a constant in the push job's config, and a startup assertion refuses to run unless it is the TEST id.

## Privacy without a local model

The model sees the current request and the smallest state slice needed to answer it. History, aggregates and secrets never enter any model context, and the rule is enforced by code on both sides of the model call.

| Data | Model sees | Enforced by |
|---|---|---|
| Current request text | Yes | Outbound filter (secrets, e-mail, phone patterns) |
| State slice for the asked `kind`, last 7 days | Only fields tagged `model_visible` | Field allowlist in `lookup()` |
| Full health, food, money history | No | Store never passed to the model; `local_only` fields shown to Slack by the handler directly |
| Other kinds' data when not asked | No | `lookup()` takes one `kind` |
| Slack, gateway, Google tokens | No | Outbound filter blocks `xoxb-`, `ya29.`, bearer patterns; blocks, does not label |
| Tool results | Filtered | Inbound filter, same rules |

Three changes to the current gate:
- Classify fields, not turns. The shadow gate would have blocked every medium-privacy turn because it judged whole turns. "Log 2 eggs" is fine; the 90-day food history is what stays home.
- Block, do not label. Every block is logged with the pattern that fired, so false positives are visible within a day.
- Raw values the CEO wants to read (a weight, a balance) go from the store to Slack through the handler. The model is told "3 entries found", not the values.

Boundary to state plainly: everything typed into Slack is already in Slack's cloud. The privacy win is keeping history and aggregates out of model context, not keeping single requests secret.

## One-week success metric

Pass if 18 of 20 real requests complete end to end in 7 days with no CEO action other than tapping an approval.

- Mix: 8 log, 6 lookup, 6 schedule, of which at least 4 compound ("log X and book Y").
- A request passes only when the correct state is observable in the store or the TEST calendar.
- Side conditions, all must hold: 0 secrets in any chat or log; 0 model calls without a human message; p95 reply under 60 s.
- Below 16 of 20: stop building, read the failing traces, fix, rerun the week.

Record each request as one row in `ops/success-metrics.md`: date, request, kind, pass or fail, reason.

## Timeline and cost

Rebuild in 3 to 5 working days, measure for 7. Token spend should fall by roughly 5x to 15x against the current design; the exact figure needs the gateway logs, which the briefing does not include.

| Phase | Days | Deliverable |
|---|---|---|
| Handler, SQLite schema, three tools | 1 to 2 | Requests write and read state |
| Verifier, filters, turn caps | 1 | "done" only on a checked postcondition |
| Push job with TEST-calendar assertion, approval button | 1 | Events land in the TEST calendar |
| State-assertion tests, backup wired to new store | 1 | Old text-heuristic checks retired |
| Metric week | 7 | 20 real requests scored |

Cost per day, new design: about 10 requests, 1 model call each, roughly 4k to 8k input and 0.5k output tokens per call. Multiply by the gateway's per-token price; list prices are not quoted here.

Cost per day, current design: the same requests, 2 to 3 hops each, every hop re-reading a 180- to 300-message session. That is the 5x to 15x multiplier, before counting the CEO's relay time, which is the larger cost.

Open item: pull input and output token totals for the last 7 days from the gateway logs and divide by requests served, so both figures become numbers.

## Dangers not in the briefing

The first item is urgent and independent of any architecture decision.

1. Leaked tokens in a public repo window. Two Slack tokens and a gateway token were pasted into chat while the repo was public (APR-0114). Treat all three as compromised: rotate today, search git history for them, and check whether APPROVALS or ops logs captured chat text.
2. Calendar ID is one config value from production. "Test only" is a human promise today. Make it a code assertion (hardening fix 4).
3. No cost ceiling. Agent-to-agent traffic never resets sessions, so nothing stops two agents talking all night. Add a daily token budget that stops the gateway process.
4. Append-only markdown as a database. No schema, no idempotency, no concurrent-write safety, and the model reads it in full. Duplicate or lost writes are already likely.
5. Synthetic-data habits. CFO and CLO were built on synthetic data; the moment real money data enters, the not-yet-coded privacy filter is the only barrier. Admit no real data before the Privacy section ships.
6. Build-count theatre. 516 tests and about 1,440 registry entries closed seven loops while the first real request failed. The one-week metric should replace loop closure as the definition of done.

## Proposed entries for decisions/ (suggestions only, nothing recorded)

For APPROVALS.md, pending the CEO's decision:
- [ ] APR: Rotate the gateway token and both Slack tokens; purge from git history. Owner: CEO. Due: today.
- [ ] APR: Adopt the single-agent architecture in this review; retire COO, CHO, CoS, CFO, CLO as agents.
- [ ] APR: Definition of done for Loop 8 = the one-week metric (18 of 20), replacing test counts.
- [ ] APR: TEST-calendar ID enforced by startup assertion in the push job.

For PENDING.md:
- [ ] P: Token totals for the last 7 days from gateway logs, to put numbers on the cost comparison.
- [ ] P: Decide whether the repo stays public during the rebuild.
- [ ] P: Field-level privacy tags for the current registry (which of ~1,440 entries are `local_only`).

## Notes added when filing (not part of the review)

- The review lists the leaked-token item as urgent. The tokens were pasted in chat, not in the repo; the history scans were clean. Rotation is the CEO's call.
- The CEO has not decided on any item above. Loop 7 stays open until the CEO says "close Loop 7".
