# gate-plugin (design and test only, APR-0113)

Status: built and tested on a scratch folder. NOT installed in the live system. Do not wire it without a CEO approval.

What it does: before every agent run (`before_agent_run`) it labels the turn with a rules-based prefilter, treats the destination as cloud, asks the privacy gate (a line-by-line port of `src/lifeos/router/gate.py`) and either passes the turn or blocks it with a plain message. Any error blocks (fail closed). It never changes the text, never calls a model and never touches the network.

Files
- `index.js` the hook and the log writer. `gate.js` the gate. `prefilter.js` the prefilter.
- `privacy.yaml` and `prefilter_rules.json` are byte copies of `contracts/policy/privacy.yaml` and `src/lifeos/router/prefilter_rules.json`. A test fails if they differ. Copy again after any change.
- `gate-log.jsonl` (created at run time, mode 600, in this folder): labels, reason codes, a 16-hex hash of the text and milliseconds. Never the text.
- `tests/gate.test.js` (11 tests) and `tests/table.js` (runs the shared case table `tests/data/gate_cases.json`). The Python side is `tests/unit/test_gate_parity.py`, which runs the same table through both gates and compares every answer.

Run the tests: `node --test tests/gate.test.js` (needs the `openclaw` package in `node_modules`, only for the registration test, which skips if missing).

Known limits
- A medium label has no sensitivity value, so the gate denies it too. In practice only prefilter-low turns pass.
- Every turn needs a label. Cron, sessions_send and suite turns have no label source other than the prefilter.
- Parity is proven on the case tables, not on every possible Unicode input.

Scratch-test findings (2026-11-04)
- A non-bundled plugin may register `before_agent_run` only if the config says `plugins.entries.gate-plugin.hooks.allowConversationAccess: true`. Without it the gateway logs "typed hook before_agent_run blocked" and the gate never runs (it would fail OPEN by being absent). Any live wiring needs that key and a check that the hook is really registered.
- On CLI turns the context has no channel, so the log shows channel "absent".
- OpenClaw runs the plugin from a staged copy under its state folder, so `gate-log.jsonl` is written there, not in the source folder.
- Hook time was 1 to 4 ms per turn (limit 15 s).
