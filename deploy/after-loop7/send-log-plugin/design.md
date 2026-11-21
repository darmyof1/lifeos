# send-log plugin (APR-0136, option A)

Purpose: a log written by code, not by agents, so a status question becomes a lookup. Metadata only, never message text.

Hooks (exactly two, observe-only, handlers return nothing): `after_tool_call` (only for sessions_send) and `message_received` (only the CEO, Slack). `before_tool_call` is never used: it fails closed and could block a send. No conversation access, no tool, command, service or route.

File: `~/loop1/workspaces/coo/state/send-log-YYYY-MM.md` (month in AST), header `# send log (written by code, no message text) - YYYY-MM` written once, then one line per event, appended with one appendFileSync call. Never rewritten.

Lines (fields separated by " | "):
- `2026-11-21 01:08 | send | coo -> cfo | coo-20261121-0108 | ok` (run ID token only, `none` if absent; to = agent id parsed from the target session key, `unknown` if not parsable)
- on error: `... | error | <masked error text>`: whitespace collapsed; session keys, mixed letter-digit runs of 9 or more, 6 or more digits and token-looking strings become `<id>`; cut to 80 characters; if any 20 characters of the message remain in it, only `error (text withheld)`.
- `2026-11-21 01:09 | ceo-message | cfo channel | 9f2c41ab` (agent of the Slack account that received it, first 8 hex of sha256 of the text). Written only when the sender equals the id in `~/loop1/ceo-slack-id`; no file or empty file writes nothing (same fail-safe as ceo-ledger).

Failure: every error is swallowed, counted in memory and logged as a code only; no line then means unknown. The CEO id file is read on each message.

Not covered: messages sent with `openclaw agent --agent <x>` (no hook fires), Slack thread behaviour (to be seen live).

Tests: `node --test` here (13 tests) and `tests/unit/test_send_log_plugin.py`.
Install (APR-0136 handover 37): copy the 4 files + log.js to `~/loop1/state/extensions/send-log` (index.js, log.js, openclaw.plugin.json, package.json, plus a node_modules/openclaw link as for ceo-ledger), add `plugins.entries.send-log.enabled true` only, restart the gateway.
