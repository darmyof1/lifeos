# REPORT-22 (APR-0112): Loop 3 closed in one pass

Date: 2026-11-01, 21:30 to 22:10 AST. Synthetic data and the Google TEST calendar only. Pull showed APR-0112 at the top (the first pull ran before it was pushed; the second showed it). All repo work is in `~/work22` (a copy; `~/lifeos-ro` was not edited). One patch: `~/handover/loop3-final.patch` (16 files, not committed, not pushed, `git apply --check` is clean against repo HEAD). Full unit suite in `~/work22`: **328 tests OK**. Repo validator: **0 blocking**, 1 warning (planned/draft/zero-byte counts). Plugin node tests: 12 of 12.

## Files in the patch
contracts/identity-access.yaml, contracts/policy/privacy.yaml (status comment only), contracts/registry/artifacts.yaml (planned to draft for the filled files; two new test entries), design/identity-and-access.md, ops/incident/kill-switch.md, ops/openclaw-update-policy.md, ops/recovery/restore-drill.md, ops/success-metrics.md, research/hardware.md, research/threat-model.md, scripts/ops/kill-switch.sh, src/lifeos/router/gate.py, tests/unit/test_gate.py, tests/unit/test_gcal_sync.py (one test added), tests/unit/test_identity_access.py (new), tests/unit/test_kill_switch.py (new). No agent file, config, plugin, crontab or live wiring was changed. `design/generated/identity-table.md` has no generator in the repo (generators are not built), so it stays an empty placeholder.

## Item 1. Non-CEO sender test
**Unit level.** The plugin node tests (12 of 12) include: "another sender, no sender, a non-Slack channel or empty text write nothing", and "no CEO ID file or an empty one writes nothing". The job tests include `test_sender_not_ceo_or_future_time_or_bad_line_no_delete` (scenario ledger), `test_not_ceo_or_future_or_broken_entries_do_not_count` (Slack ledger), and `test_without_state_a_slack_entry_never_counts`. One test was missing and is added (tests only): `test_a_sender_that_is_missing_empty_lowercase_or_not_a_string_never_counts` (sender absent, empty, "ceo", " CEO", "CEO ", None, 0, a list, "Bot", a user-ID-like string: none deletes). 97 gcal tests OK.

**Live level.** Evidence: `non-ceo-test/`.
- A pending request for the 10-30 workout was made over the CLI (run loop3-p22-n1): the CoS wrote `delete-pending-approval | loop3-p22-n1 | seed-3 | CEO`.
- A post from another bot identity did not work: the CHO, CoS and CFO bots are not members of the COO's channel (`channel_not_found` for each).
- A post from the COO's own bot ("<@COO> approve seed-3") was sent and accepted by Slack, but the COO never ran on it (its channel session was not updated) and the plugin wrote no ledger line.
- Slack ledger lines before 26, after 26. Journal `deleted` lines for the run 0. Cron runs 21:35, 21:40, 21:45, 21:50: exit 0, `deleted 0` (`non-ceo-test/sync-log-excerpt.txt`). Used-approvals file unchanged (5 entries).
- Clean-up: request left unanswered; closing reset (`prep loop3-p22-n1-restore`): 3 events plus busy, journal 3 0; the cron line was restored.
**Verdict.** Nothing but the CEO's own user writes a ledger line, shown by 12 plugin tests, the job tests above and the new test. The live proof is partial: a bot message is not delivered to the COO (Slack/OpenClaw do not hand a bot's own post to the agent), so it shows "no ledger line, no agent run, no delete" for a bot sender, not for a second human. **Ask for the CEO** (seven items below): can one message be sent from a second Slack user, or a second test account, for a final live check.

## Item 2. Privacy gate in code (unwired)
Built: `src/lifeos/router/gate.py`, a pure function `decide(request, policy_path)`: no network, no model call, no file write, no extra library (it reads privacy.yaml with a small reader that is tested against PyYAML). It returns allow or deny, a reason code, the privacy level used, a CISO notice field, a budget-gate flag and a log record with labels and a hash of the request ID only (no content).
Rules as written (ADR-0003, privacy.yaml, APR-0007, APR-0045): high means cloud denied; medium means cloud only when the request says low sensitivity; low means allowed (budget gate flag set); privacy wins over complexity; a missing, unknown or unsure label counts as high; local destinations are always allowed; an override needs `override: true` plus a confirmation record confirmed by "CEO" with a confirmation ID, then it is allowed, logged and the CISO notice is returned (nothing is sent); the Slack channel exemption never reaches cloud model calls (and a policy that says otherwise is refused). Any malformed request or unreadable, weakened or duplicated-key policy denies everything.
Tests: `tests/unit/test_gate.py`, 20 tests, 29-row case table including critical complexity with high privacy, missing level, unknown level, override without confirmation, override with confirmation, the Slack channel, and a malformed policy file. `privacy.yaml` stays "draft" with a line saying the code exists and is unwired.
**Proposed implementation note for ADR-0003 (not applied; the CEO decides):** "Implementation status (2026-11-01): src/lifeos/router/gate.py and tests/unit/test_gate.py exist (APR-0112). The gate is not wired into any model call."

**Where a real gate could sit in OpenClaw 2026.10.5 (read only; docs in the installed package, plugins/hooks).**
| Hook | Kind | What it could do for the gate |
|---|---|---|
| `before_agent_run` | gate | Inspect the prompt and history before the model reads them; return `{outcome: "block", reason, message}` to stop the run. Runs on the embedded and CLI runners and at node admission. Times out after 15 s and fails closed (the run is blocked). Our agents run on the OpenClaw runtime (APR-0060), which is the embedded runner |
| `before_model_resolve` | modify | Change provider or model before the session loads: the natural place to send a high-privacy turn to a local model instead of denying it |
| `before_prompt_build` | modify | Add context or narrow the tools; not a block |
| `before_tool_call` | modify / gate | Block a tool call (for example one that sends data out) |
| `message_sending` | modify | Cancel an outgoing message |
| `llm_input` | observe | Log what goes to the provider (labels, not text) |
What wiring needs: (1) a triage label for every turn, which today does not exist (the local triage is too slow, 3.68 tokens per second, SPK-06, and rules-only triage is not built); (2) the gate in JavaScript inside a plugin (ours is Python): a port with the same case table as the tests, or a call out of the plugin; (3) the plugin to register `before_agent_run` and, if wanted, `before_model_resolve`: this is a plugin with a gating hook, not the observe-only ledger plugin, so it needs its own CEO approval, install test and rollback; (4) a local model that works, otherwise "high" can only mean "blocked".
What would break: a fail-closed gate with no label treats every turn as high, so every agent turn that would go to the cloud model is blocked: all four agents, the sessions_send turns between them, the cron-driven turns and the regression suites would stop until labels exist. The 15 s hook timeout is shorter than the current local triage (about 20 s), so a model-based label cannot be produced inside the hook without a faster local model or a cached/rules-based label. Hooks that need the final system prompt (node turns) may not see it.
**The gap, plainly: today the four agents call the cloud model directly, so the gate cannot protect them until it is wired.** Nothing was wired.

## Item 3. Security minimum
**a. Threat model:** `research/threat-model.md` (assets, boundaries, actors, 10 threats seen or closed, 8 residual risks, controls). **b. Update policy:** `ops/openclaw-update-policy.md` (pinned 2026.10.5; when, how in 7 steps with a scratch state folder, regression compare, CEO decides, rollback). 
**c. Kill switch:** `scripts/ops/kill-switch.sh` (default dry run; `--execute` stops the gateway service and pauses the calendar cron line, saves a crontab copy and a marker, mode 600; `--restore --execute` reverses it; never touches the stress-ng line or other lines; deletes nothing; prints no secrets) and `ops/incident/kill-switch.md`. 13 unit tests with a fake systemctl and fake crontab in a temp HOME. **Live drill** (21:52, outside the window; `kill-switch-drill/`): dry run printed both actions and changed nothing; `--execute` took 1.5 s (calendar line paused, gateway 0 processes, marker mode 600); `--restore --execute` took 5.0 s (includes a 5 s wait): gateway one process, crontab identical to before (`diff` empty, `crontab-compare.txt`); health check PASS 73, WARN 0, FAIL 0, INFO 4. The drill restarted the gateway once.
**d. Restore drill:** `ops/recovery/restore-drill.md`. Backups that really exist: the repo on GitHub; config `.bak` copies and a few named copies on the same disk; named crontab copies. **There is no off-VM backup of ~/loop1/state (329 MB) or of the four workspaces; the workspaces are git repos with no remote; the backup scripts in the repo are empty files.** Whether a boot-volume backup exists at Oracle is unknown from the VM. Drill on a copy (259 files: the four workspaces plus the config with token-like fields replaced by "<redacted>", 1 field): gpg symmetric AES256 with a 24-character throwaway passphrase (never written to a file), wrong passphrase refused with no output, restore into a new folder: **all 259 sha256 equal**; copy 0.1 s, encrypt 1.1 s, decrypt and extract 0.4 s, total 1.5 s; archive 158,913 bytes; the temporary folder and archive were deleted. The session state and the plugin folder were not in the drill (`restore-drill/result.txt`).

### Item 3e: decisions (seven items each)
**Isolation (SPK-03)**
| | |
|---|---|
| What | Turn on agent isolation (sandbox) so one agent cannot read another's workspace or files |
| Used for | Limiting what a confused or manipulated agent can reach |
| Why now | Isolation-on was deferred (APR-0070); the isolation-off canary was never obtained, so we do not know whether one agent can read another's files today. Real data is not connected yet |
| Risk if approved | Needs Docker on the VM (deferred), more moving parts, slower runs; a sandbox mistake can stop the agents |
| Risk if not | An agent that is steered wrong could read or change another agent's files (today the guard is instructions plus the push job) |
| Recommendation | Approve a test, not a switch: run SPK-03 isolation-on on a scratch state folder before any real data; do not turn it on live yet |
| Reply | approve, explain more, or keep |
**Public repo**
| | |
|---|---|
| What | Decide whether the repo may be public |
| Used for | Sharing the design; the repo is the rebuild source |
| Why now | The repo must be safe to publish before real data and before outsiders see it. Current visibility: unknown (gh is not installed on the VM; the remote is on GitHub) |
| Risk if approved | Anyone reads the design, agent instructions, approvals and handover reports; a missed secret or ID becomes public and cannot be un-published |
| Risk if not | Fewer eyes on the design; no sharing |
| Recommendation | Keep it private until a secrets/ID scan of the whole git history passes and the CEO has read the approvals ledger for personal content; decide then |
| Reply | approve, explain more, or keep |

### Other proposals from item 3
**Weekly encrypted off-VM backup**
| | |
|---|---|
| What | A weekly job that encrypts a token-free copy of the four workspaces and the config with the archive public key and stores four copies off the VM |
| Used for | Recovering from VM loss; today nothing off the VM holds the workspaces |
| Why now | The restore mechanism is proven (SPK-07 and this drill); real data must not enter without a restore path |
| Risk if approved | One more cron job and a public key to manage; a wrong archive scope could leave a secret in the copy |
| Risk if not | VM loss loses the agents' history and state; only the repo survives |
| Recommendation | Approve; build as its own handover with the CEO's public key, a test and a quarterly restore with the CEO's key |
| Reply | approve, explain more, or keep |

## Item 4. Identity-access contract
Written: `contracts/identity-access.yaml` (draft; nine identities, delete rule, calendar-write rule, files and modes, channel placeholders) and `design/identity-and-access.md`. Blocker P-04: it was answered by APR-0023 (the ADR list), so the blocker is gone. Test `tests/unit/test_identity_access.py` (12 tests) checks the YAML against: the send lists in `deploy/loop1/health-check.py` and the CFO send-list diff (`ops/cfo-send-list-diff-2026-10-26.txt`), the "You may send to" text in the four `agent-files/*/AGENTS.md` (the text may not list more than the contract), the 48-hour limit and `--require-ceo-ledger` in the job, the health check's two-ledger test, the plugin's modes 700/600 and its single hook, "only the CoS writes the journal / only the job writes Google / only the CEO approves a delete", no ID/token shapes, channel placeholders, and that every cited APR exists. **Finding the test records:** the CFO instruction text lists only the COO, while the config also lets the CFO send to the CoS (set 2026-10-26). `design/generated/identity-table.md` was not regenerated: the repo has no generator for it.

## Item 5. Metrics and hardware
`ops/success-metrics.md`: 12 metrics with real baselines (137 runs in 47 suites) and thresholds marked "proposed, not decided"; the health-feed design (source, fields, privacy level, readers, storage, gate treatment, retention) and four preconditions for real data. Key baselines: mean cost 0.0064 USD per run (highest 0.0167); mean 13.3 turns per run; pass rates since Handover 18: D1 4 of 4, D2 9 of 9, D3 2 of 5, overlap 5 of 5; wrong deletes 0 since the gate; 5 live approvals used; stale-memory first replies 3 of 5 uncompacted first requests.
`research/hardware.md`: VM measured (4 ARM cores, 23 GiB memory, no GPU, 3.68 tokens per second for an 8B model), three options with rough prices from public pages (sources and date in the file; the VM's own cost and the Hetzner GEX44's current availability are unknown), recommendation as a proposal.

## Item 6. P-43 close-out table
| Step | Status | Evidence | What remains | The CEO must decide |
|---|---|---|---|---|
| 1 Rebuildable repo, parity check, regression suite | Done | Handover 8 and later; health-check parity lines; `regression-suite.sh` | Three agent files hold Slack channel IDs and stay out of the repo (placeholders; APR-0098) | nothing new |
| 2 Structure test (one agent versus four) | Done | Handover 10 comparison: 36 of 42 versus 31 of 42; cost 0.0061 versus 0.0019 USD | The open question "when a chief is its own agent" | Tiered approvals / when a chief is its own agent (PENDING) |
| 3 Privacy gate in code | **Built and tested, NOT wired** | gate.py, 20 tests, this report item 2 | A triage label for every turn; a plugin with a gating hook; a usable local model; the live test | Wire the gate or not (and when); approve the ADR-0003 implementation note |
| 4 Security minimum | Partly done | Threat model, update policy, kill switch (drilled once), restore drill (config and workspaces only) | A routine off-VM backup (none exists); full-state restore not timed; isolation not proven; repo visibility unknown | Isolation (above); public repo (above); weekly backup (above) |
| 5 Identity-access contract | Draft written and machine-checked | contracts/identity-access.yaml and its test | CEO acceptance; no generator for the identity table | Accept the contract (it is a precondition for real data) |
| 6 Success metrics, one real feed, hardware, real data | Metrics and hardware proposed; **health feed is a design only** | ops/success-metrics.md, research/hardware.md | Metrics adoption; hardware choice; feed not connected; no real data anywhere | Adopt the metrics; hardware option; a separate yes for real data after the four preconditions |
Not finished, plainly: the gate is unwired; the health feed is a design only; there is no off-VM backup; isolation is unproven; a second human sender was not tested live; stale-memory replies in the COO's Slack channel session are contained, not fixed.

### Proposal: wire the gate
| | |
|---|---|
| What | Build a second plugin with a `before_agent_run` gate hook that calls the privacy gate and blocks a turn the gate denies |
| Used for | Making the privacy rule real for the four agents |
| Why now | It is the biggest open risk; every other control assumes synthetic data |
| Risk if approved | Fail-closed means all turns are blocked until labels exist; a gating plugin is more powerful than the ledger plugin; the 15 s hook limit |
| Risk if not | Real data cannot be allowed; the gate stays a unit test |
| Recommendation | Approve a design-and-test handover first: labels by a rule-based prefilter, plugin on a scratch state folder, no live wiring; then a separate approval to wire |
| Reply | approve, explain more, or keep |
### Proposal: a second-human live test
| | |
|---|---|
| What | One message from a second Slack user (or a CEO-less test account) in the COO channel: "@COO approve seed-3" while a delete is pending |
| Used for | Closing the one untested live case of the delete gate |
| Why now | Item 1 could not do it with a bot |
| Risk if approved | Needs another person for two minutes; nothing real is deleted (test calendar) |
| Risk if not | The proof rests on unit tests |
| Recommendation | Approve; do it in the next handover |
| Reply | approve, explain more, or keep |
### Proposal: clear the COO channel session
| | |
|---|---|
| What | Decide how the COO's Slack channel session is cleared (a compaction before a request, or a rule) so it does not answer "already handled" from old memory |
| Used for | Fewer wrong first replies (3 of 5 uncompacted) |
| Why now | It cost three tries in Handover 21 |
| Risk if approved | A compaction loses recent context in that channel |
| Risk if not | Wrong first replies stay; no wrong delete (the job reads files) |
| Recommendation | Approve a handover to measure it with a compact before each real request; no instruction change yet |
| Reply | approve, explain more, or keep |

## End state (22:02 AST)
- Gateway: one process (restarted once, by the kill-switch drill, at 21:52; and once earlier today for COO v1.10.7).
- Crontab: equals the start of this handover (`crontab-final.txt`, diff empty); calendar line active with both ledger options; stress-ng and 05:00 lines unchanged; no kill-switch marker.
- Google test calendar: 3 seed events plus busy (list rc 0). CoS journal 3 0.
- Plugin enabled, hook-only (shape non-capability); hash prefixes ee4e490ab5108b30, 767ca80faa71b970, a97a8993eb9d3bd9, 1b98f60e4fbff9cc.
- Slack ledger 26 lines (no change). Health check PASS 73, WARN 0, FAIL 0, INFO 4.
- Costs: this handover's agent calls were one CLI request (well under 0.05 USD); no suites were run. The day's total stays far below 1 USD.
- Not changed: any agent file, instruction, config, plugin or the cron line (only the suites' pause/resume and the kill-switch drill, both restored).
- A note on the clone: `~/lifeos-ro` shows one untracked 24-byte file named `0` (unknown origin, dated 10-26); it was left alone and is not in the patch.
