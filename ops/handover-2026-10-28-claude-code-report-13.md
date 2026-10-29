# REPORT 13 - delete gate step A: the CEO ledger plugin (design and code only, APR-0102)

Pulled first: HEAD a6b789d "APR-0102 ..." with the handover 12 commit below it. Work 20:33 to 20:50 AST. No agent message, no compaction, no gateway restart, no model cost. **Nothing is installed**: the gateway, `openclaw.json`, the cron and every agent file are unchanged (checked: no ceo-ledger entry in the config, cron has no `--require-ceo-ledger`, repo clean).

## Task 1 answer in plain words
- **Can the plugin be observe-only?** By construction, yes; the host does not enforce it. The hook it uses, `message_received`, is an observe hook: the host ignores what it returns and runs it fire-and-forget, so it cannot change, block or answer a message. The plugin registers that one hook and nothing else (a unit test fails if it registers anything else; `plugins inspect` must show hook-only at install). But native plugins run inside the gateway process with no sandbox, so the guarantee is the small, reviewable code plus a hash pin, not a host permission.
- **Does it fail closed?** Yes. Any error (unwritable directory, disk full, crash in the handler, missing CEO ID file) is caught, logged without text or IDs, and writes no line. No line means the push job does not delete. If the plugin fails to load, there are no lines, so no deletes. The only way to fail open is a cron without the flag, which is why the flag and the plugin should go in together, and a health-check line for both should be added at install.
- **Where it fires:** Slack channel messages (the normal inbound path, all four agent channels share it; from source reading, to be confirmed by the live test) and Control UI chat. Not for `openclaw agent -m` and not for agent-to-agent messages, so the scenario runner keeps writing the CLI ledger (APR-0101).
- **The matching rule** (implemented in the patch): a deleted line needs its pending line, and a ledger entry from the CEO whose `event_tokens` contain the deleted line's event ID, not older than the first time the job saw the pending line (less a 5 minute grace), not older than 48 h, and not already used for an earlier delete (the message ID is recorded after the delete). The channel is recorded, not required. The old scenario-ledger rule still works; the option can be given once per ledger.
- **What it cannot prove:** intent (a CEO message that merely names the event ID, even "do not delete X", counts, because no text is kept); approvals that do not cite the event ID (such as D2's "Yes, I approve") do not count and the delete waits; it cannot show that the message answered this particular request. Options for the CEO in design.md section 4.
- **Needed from the CEO before an install:** a separate yes (new APR); the CEO's Slack ID typed into `~/loop1/ceo-slack-id` by the CEO; a gateway restart (one) plus a plugin trust entry in the config; a choice on intent (word-list heuristic or accept the ID alone) and on events cited without an ID.

## Files (`~/handover/ceo-plugin/`)
- `design.md` (all six points with evidence), `install-test-plan.md` (not run), `README.md`.
- Plugin: `openclaw.plugin.json`, `package.json`, `index.js`, `ledger.js`; tests `test/ledger.test.js`.
- Push job: `gcal_sync.slack-ledger.patch`, `test_gcal_sync.slack-ledger.patch` (diffs against HEAD a6b789d, apply cleanly with `patch -p1`, give files identical to `gcal_sync.py.new` and `test_gcal_sync.py.new`).
- Ledger line written by the plugin: {time, channel slack, account, conversation (hashed, `c-` + 16 hex), message_id, sender CEO, text_sha256, event_tokens}. The text is not stored.

## Test results
- Plugin: `node --test test/ledger.test.js` 10 of 10 pass (Node 24). They cover: one CEO message gives one line with the fixed fields; another sender, no sender, a non-Slack channel, empty text or no CEO ID file write nothing; a duplicate message ID writes once, also after a restart; an unwritable directory writes nothing, does not throw and logs no text or IDs (a throwing logger also does not throw); file mode 600, directory 700; the text and raw IDs are not in the file; token extraction; and the plugin entry (loaded with the real OpenClaw package of this VM through a temp symlink) registers only `message_received`. Fake IDs only.
- Push job: 17 new tests (`SlackLedgerTests`) next to the 67 existing; `python3 -B -W error::ResourceWarning -m unittest discover -s tests/unit -p "test_gcal*.py"` runs 151 tests, all OK, with the existing scenario-ledger tests unchanged.

## Failures as they happened
- First run of the plugin tests with `node --test test/` (a directory argument) failed with MODULE_NOT_FOUND on this Node version; `node --test test/ledger.test.js` works and is the command written down.
- My first run of the gcal tests in a temp copy showed 4 failures and 3 errors, all in `test_gcal_sync_cron`. They also appear on the unpatched files in that copy: the copy lacked `gcal_sync_cron.sh`. With the .sh copied, 151 of 151 pass.
- My first version of two new tests left files open (ResourceWarning); fixed before the patch was made.

## Not done, on purpose
No install, no plugin load, no gateway restart, no config change, no CEO ID file, no cron flag, no live Slack test. The design assumes the hook fires for all four channels because they share one dispatch path; that and "a non-CEO sender writes nothing" live are in the install plan as checks.
