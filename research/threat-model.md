# Threat model - LifeOS Loop 3 (one page)

Status: draft, written 2026-11-01 under APR-0112 from facts in the repo and a read-only look at the VM. Synthetic data only so far (APR-0073 in P-40). Changeable: yes; a change is a new approval.

## Assets
| Asset | Where | Why it matters |
|---|---|---|
| The CEO's approval (delete, privacy override) | Slack messages from the CEO's own user; CEO ledger on the VM | A delete or a privacy override must come from the CEO only |
| Journals (calendar journal, state files) | CoS and other workspaces (git repos on the VM) | Append-only truth for the agents (ADR-0001, ADR-0011) |
| The real calendar and, later, real life data | Not connected. The job writes to a Google TEST calendar | Real data needs the gate wired and a separate CEO yes |
| Secrets: gateway token, Slack bot and app tokens, Google client secret, OpenAI key | VM files and environment, never in the repo | Whoever holds them can act as the system |
| The CEO's Slack user ID (ledger identity) | A VM file, mode 600 | Names who counts as "the CEO" for the gate |
| The repo (design, scripts, tests) | GitHub (private or public: see the report) and the VM clone (read-only) | Rebuilds the system; must hold no secrets |
| The pinned OpenClaw version (2026.10.5) | VM npm install | A silent upgrade changes behaviour under test (APR-0060) |

## Trust boundaries
| Boundary | Crossing | Control today |
|---|---|---|
| CEO to Slack | Message with an @mention of one bot | The ledger plugin sees only messages from the CEO's user ID; text is hashed, not stored |
| Slack to the OpenClaw gateway | Socket mode, one app per agent | Each agent has its own bot; the allowed-send list limits agent-to-agent calls |
| Gateway to agents and to the model provider | Agent prompts and replies go to a cloud model (OpenAI) | Synthetic data only. The privacy gate (ADR-0003) exists as code but is NOT wired (APR-0112): today nothing stops a high-privacy request from reaching the cloud model |
| Agents to files and to Google | Agents write journals; only the push job writes to Google | The push job is code, runs every 5 minutes, and deletes only after a CEO approval record |
| VM to the internet | Slack, OpenAI, Google, GitHub | One user (ubuntu), gateway bound to the VM; no public service of ours |
| Claude Code on the VM to the repo | Reads and runs scripts; delivers files by tarball | The repo clone is read-only; the CEO pushes |

## Actors
CEO (trusted); the four agents (COO, CHO, CoS, CFO) - semi-trusted, they are models and can be wrong or confused; the sync job and the ledger plugin (our code, trusted after tests); Claude Code on the VM (trusted operator, bound by the handover limits); the model provider (sees all agent traffic); other Slack members (untrusted: their messages must never count); anyone who obtains a token or the VM account (attacker).

## Threats seen or closed
| Threat | What happened or could happen | Status |
|---|---|---|
| Delete without approval | Before the gate, 2 of 6 four-agent runs (Handover 10, D3) deleted the Google event without a CEO approval. Since APR-0101 an agent can still write a `deleted` line, but the push job refuses it ("no CEO approval record"; Handovers 17 to 21) | Closed at the job: delete needs a pending line plus a CEO ledger approval |
| Approval by the wrong person | Anyone in the channel could type "approve" | Closed by the plugin: only the CEO's own Slack user writes a ledger line; another sender, no sender, an empty ID file or a non-"CEO" sender write or count nothing (unit tests, and a live bot post in Handover 22 item 1) |
| Bare or negated approval | "approve" with no target, or "do not approve" | Closed: the `approve_word` rule; a plain approve counts only if exactly one delete is waiting (APR-0110); live test in Handover 21 |
| Stale approval | An old approval used later for another delete | Closed: each message ID is used once; the approval must be newer than the pending line; 48 hours at most |
| Stale memory claims | The COO's Slack channel session said "already handled" or "already approved" from old memory (Handovers 19 and 21) | Open, contained: nothing is deleted because the job reads files, not claims; a session compact clears it; not fixed in the instructions |
| Two gateways | Two processes would double every message | Closed by a health check (exactly one gateway) and the kill switch; the "3 processes" reading in Handover 19 was a counting error in the report (fixed, APR-0109) |
| Token revocation | A leaked Google client secret had to be reset (install log) | Closed by the owner; tokens are never copied into reports (secrets scans before every tarball) |
| Secrets in the repo | A secret or a Slack ID committed by mistake | Controlled by the validator and the secrets scan before every package |
| Silent upgrade | A new OpenClaw version changes hooks or the harness | Controlled: version pinned, health check fails on another version; see ops/openclaw-update-policy.md |
| Data to the cloud model without the gate | A request with health or finance content sent to OpenAI | OPEN: gate built, not wired (see below) |

## Residual risks (not closed)
1. The privacy gate is not wired. Four agents call the cloud model directly. Safe today only because all data is synthetic.
2. No automatic backup of the VM state or the workspaces (ops/recovery/restore-drill.md): the workspaces are git repos with no remote.
3. Intent beyond the word lists: "approve" in a sentence that means something else can still pass the word rules (design.md of the ledger plugin).
4. The agents can still write a `deleted` line themselves (D3); only the job stops it. A change to the job would remove that control.
5. The model provider sees everything the agents see. A local model is too slow on this VM (SPK-06).
6. Isolation between agents on the VM is not proven (SPK-03: isolation-off canary not obtained, isolation-on deferred).
7. A second CEO-less sender was tested only with a bot (Slack did not deliver it), so the live proof for a second human is the unit tests.
8. One operator account (ubuntu) holds all secrets and can edit the crontab and the config.

## Controls that exist
| Control | Where |
|---|---|
| CEO ledger plugin (observe-only, hook-only, fail closed) | deploy/loop3/ceo-plugin; installed on the VM; hash-checked by the health check |
| Delete gate in the push job (`--require-ceo-ledger` on both ledgers in the cron line) | scripts/gcal/gcal_sync.py; health check |
| Allowed-send lists and agent allowlist | OpenClaw config; health check |
| Pinned OpenClaw version | Health check |
| Health check (73 PASS, 0 WARN, 0 FAIL on 2026-11-01) | deploy/loop1/health-check.py |
| Regression suite (D1, D2, D3, overlap, and others) | deploy/loop3/vm/regression-suite.sh |
| Privacy gate code (unwired) | src/lifeos/router/gate.py, tests/unit/test_gate.py |
| Kill switch (drilled once) | scripts/ops/kill-switch.sh, ops/incident/kill-switch.md |
| Secrets scan before every handover package | Handover practice |
