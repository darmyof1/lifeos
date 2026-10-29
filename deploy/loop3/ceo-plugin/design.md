# CEO ledger plugin, design note (APR-0102, handover 13)

Status: design and code only. Nothing is installed, the gateway is not changed, the cron has no `--require-ceo-ledger`. Evidence paths are on this VM (OpenClaw 2026.10.5): docs under `~/.npm-global/lib/node_modules/openclaw/docs/plugins/`, types in `.../dist/config-contracts-*.d.ts`, source in `.../dist/*.mjs`.

## 1. Plugin shape, loading, removal, observe-only
- Shape: a native, **hook-only** plugin (docs `sdk-entrypoints.md`, "Plugin shapes"). Directory with `openclaw.plugin.json` (id `ceo-ledger`, empty config schema, `activation.onStartup`), `package.json` (`openclaw.extensions: ["./index.js"]`), `index.js` (entry), `ledger.js` (logic, no OpenClaw imports). About 110 lines in total, no dependencies, no network.
- Install and remove (docs `manage-plugins.md`): `openclaw plugins install <dir>` (copies) or `--link <dir>`; `openclaw plugins enable|disable ceo-ledger`; `openclaw plugins uninstall ceo-ledger [--dry-run]`; `openclaw plugins inspect ceo-ledger --runtime --json` shows what loaded. Changes need `operator.admin`. Enabling records an explicit trust entry in the config (`plugins.entries.ceo-ledger`). That is a config change, so it belongs to the install window.
- Permissions: there is no permission list for a native plugin. Docs (`architecture.md`, "Execution model"): native plugins run in-process with the gateway and are not sandboxed; a bug can destabilise the gateway and malicious code equals arbitrary code in the process. So "observe-only" is a property we establish, not one the host enforces:
  1. By hook type: `message_received` is an **Observe** hook (`hooks/reference.md`): handlers run concurrently, return values are ignored, and the type is `AsyncPluginHook<Event, Context>` with result `void` (d.ts `PluginHookHandlerMap`). It cannot rewrite, cancel, claim or answer a message. The modify/claim/gate hooks (`message_sending`, `before_dispatch`, `reply_dispatch`, `before_agent_run`, `inbound_claim`) are not registered.
  2. By code: `index.js` registers exactly one hook and nothing else (no tool, command, service, route). A unit test passes a fake `api` whose other register functions throw and asserts the only call is `message_received`.
  3. By inspection at install time: `plugins inspect ceo-ledger --runtime --json` must show shape hook-only and one hook.
  4. By size and review: the whole plugin is short enough for the CEO or Claude to read in minutes; pin it with sha256 of its four files (the install plan records them).
  Residual risk, stated plainly: the host does not stop this plugin from doing more if the code were changed. Keep the installed copy outside `~/handover` and owned read-only, and compare hashes at every check.

## 2. What `message_received` gives, and where it fires
- Event (d.ts `PluginHookInboundMessageFacts` + `from`): `content`, `timestamp`, `messageId`, `senderId`, `threadId`, `sessionKey`, `runId`, `replyTo*`, `media`, `metadata`. Context (`PluginHookMessageContext`): `channelId`, `accountId`, `conversationId`, `sessionKey`, `runId`, `messageId`, `senderId`.
- The same sender field is what the transcripts show under `__openclaw.senderId` for Slack messages (handover 11, Task 1), set by the channel plugin, not by an agent.
- Where it fires (source search of `emitMessageReceivedHooks` call sites): the auto-reply dispatch path `dispatch-from-config` (all channel inbound turns, so Slack, once per accepted turn, with an inbound de-duplication cache in front) and `chat-send-handler` (Control UI chat). It is skipped when `ctx.SuppressMessageReceivedHooks` is set. Telegram has its own call. It is **not** called by the `agent` gateway method that `openclaw agent -m` uses, nor for inter-session (`sessions_send`) messages. So: Slack yes; CLI no (the scenario runner keeps writing the CLI ledger, APR-0101); messages from other agents no.
- All four agent channels: the four agents are bindings of one Slack account, which share the dispatch path, so they should all fire. This is from reading the source, not observed; the install plan tests a CEO message in each of the four channels.
- Delivery: fire-and-forget (`fireAndForgetHook(... "message_received plugin hook failed")`). An error or a slow handler is logged and the message flow continues. A timeout does not cancel the handler (`reference.md`, failure table: "Other asynchronous hooks: log and continue").

## 3. The ledger line (implemented)
`{"time","channel":"slack","account","conversation","message_id","sender":"CEO","text_sha256","event_tokens":[...],"approve_word":true|false}`, one per line, file `~/loop1/ceo-ledger/slack-ledger.jsonl` (directory 700, file 600, O_APPEND).
- Changes to the proposal: added `account`; `conversation` is `c-` plus 16 hex of sha256 of the conversation ID, so no Slack ID is written; `message_id` is the Slack timestamp id, used for de-duplication and for "used once".
- `event_tokens`: pieces of the text split on anything but letters, digits and hyphens, stripped of edge hyphens, lower-cased, kept if 3 to 64 chars with at least one hyphen and one digit, unique, at most 30. This also keeps dates such as `2026-10-30`; they never match an event ID, so they are harmless.
- `approve_word` (APR-0103): true only if the text has a whole word approve, approved or approving (any case) and none of the blocking words. Lists, all in `ledger.js` (`APPROVE_WORDS`, `BLOCK_WORDS`, `BLOCK_PHRASES`): blocking words not, no, never, cannot, without, cancel, stop, keep, explain, dont, don't, cant, can't, wont, won't, wait; phrases "do not" and "hold off". Matching is whole-word after lower-casing, curly apostrophes folded, and splitting on anything but letters, digits and apostrophes. **The lists are conservative on purpose**: a false is safe (the CEO writes the message again), a wrong true is not. Side effects that are accepted: a hyphenated event ID with a piece such as `no` or `stop` makes the message false; "disapprove", "approval" and "approves" are false; a pasted copy of the COO line "Reply: approve <id>, explain more, or keep" is false because of "explain" and "keep". The text is still not stored.
- The text is not stored, only its hash, the tokens and the flag. Tokens can still reveal an event ID, which is the point.
- The CEO's identity: the plugin compares `senderId` with the content of `~/loop1/ceo-slack-id` (mode 600, created by the CEO at install, read on every message). No file, empty file, other sender, other channel, empty text: no line.

## 4. How the push job matches a deleted line (implemented in the patch)
`gcal_sync.py --require-ceo-ledger PATH` may be given once per ledger (scenario ledger and Slack ledger). A `deleted` line still needs `--allow-deletes` and the earlier `delete-pending-approval` line with the same event ID. Then some ledger must hold an approval:
- Scenario entry (no `event_tokens`): unchanged: same run and event, sender CEO, time not later than now.
- Slack entry: sender CEO, time not later than now, and
  - (0) `approve_word` is exactly `true` (APR-0103; missing, false or any other value counts as false);
  - (a) the deleted line's event ID is in `event_tokens` (case-insensitive, whole token);
  - (b) ordering: the job records the first time it saw each pending line in `<state-dir>/ceo-ledger-seen.json` (key run|event). The entry must not be older than that moment minus 300 s (the cron interval, so a quick reply that lands before the first job run counts) and not older than 48 h;
  - (c) used once: after the delete ran, its `message_id` goes into `<state-dir>/ceo-ledger-used.json`; the same message cannot approve another delete (event IDs such as `seed-3` are reused);
  - (d) the channel is recorded but not required: a CEO message in any channel the gateway delivers counts. A stricter rule (the conversation must be one of the four agent channels) is a one-line change if wanted.
- With a Slack entry and no state dir, nothing counts. A missing, unreadable or damaged ledger approves nothing.

What this cannot prove:
1. Intent beyond the word lists (APR-0103 narrowed this, it did not remove it). A message such as "approve nothing but explain loop2-x-01" is caught only if a blocking word is in it; "I might approve loop2-x-01 later" would count. Before APR-0103: a CEO message that merely contained the event ID ("why is loop2-scn-021-cho-01 pending?", or "do NOT delete loop2-scn-021-cho-01") counts. The plugin keeps no text, so it cannot tell. Mitigation options for the CEO to choose: (i) the COO layout asks for "approve <event ID>" and the plugin stores a boolean `approve_word` found by a simple word list with negations excluded (a heuristic, not built); (ii) accept that the CEO's own message naming the event is enough.
2. Approval with no event ID ("Yes, I approve", as in scenario D2). It does not count; the delete waits. The COO layout (v1.10.1) already asks the CEO to cite the ID. A looser rule (exactly one pending line and a CEO message with no tokens after it) is possible but weaker; not built.
3. That the message answers this request: the job knows only the ID, the time and the sender.
4. Anything before the job saw the pending line (more than 5 minutes earlier), or while the job was not running for hours: the approval is rejected and the CEO must approve again. This fails closed.
5. A compromised CEO Slack account, or someone with OS access to the VM (the ledger file is owned by the same OS user as the gateway; the tool policy, not file permissions, keeps agents out).

## 5. Failure modes of the plugin (default: no ledger line, so no delete)
- Handler throws, disk full, ledger directory unwritable (tested: EACCES): the error is caught, counted, logged without text or IDs, nothing reaches the gateway. No line, no delete.
- Plugin fails to load or is disabled: the gateway runs normally, no lines, no deletes (if the cron has the flag). The health check should assert that the plugin is loaded and that the cron line carries the flag; propose adding both to `health-check.py` in the install handover (not done now).
- Gateway restart: the in-memory set is lost; the handler scans the last 256 KB of the ledger for the message ID, so a redelivered message does not write twice (tested). Messages that arrive while the gateway is down are not recorded unless Slack redelivers them: fail closed.
- Duplicate delivery: written once (memory set, then ledger tail).
- Failing open is only possible by leaving the flag out of the cron. That is why the flag, and the plugin, go in together in a separate decision.

## 6. Rollback
1. Take `--require-ceo-ledger` out of the cron arguments first if it was added. Without the plugin and with the flag on, every real delete is refused (safe but blocking).
2. `openclaw plugins disable ceo-ledger`, then `openclaw plugins uninstall ceo-ledger`, one gateway restart, restore `openclaw.json` from the backup if the config entry remains. 
3. What is left: the append-only ledger files (evidence, harmless), the job's two state files in its state dir, and the code of the check in `gcal_sync.py` (off unless the flag is given). Deletes then behave as before this work: gated by the instructions and the pending/deleted line rule only.
