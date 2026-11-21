# REPORT 37 - P-51 send-log plugin built, proved in scratch, installed live (APR-0136)

## Part 1. Build (done; repo patch handover37.patch, 8 files, applies to a fresh clone)
- deploy/after-loop7/send-log-plugin/: openclaw.plugin.json (id send-log, empty config schema, onStartup), package.json, index.js (exactly two hooks: after_tool_call, message_received), log.js (no OpenClaw imports), tests/log.test.js (13 node tests), design.md (one page).
- Line formats exactly as approved: `time | send | from -> to | run ID or none | ok` (error adds `| error | masked text`); `time | ceo-message | <agent> channel | 8 hex`. Month file send-log-YYYY-MM.md in the COO workspace state folder, header once, one appendFileSync per event, failures swallowed and counted, handlers return nothing.
- deploy/loop1/health-check.py: 3 new lines (send-log hook-only, 4 files equal to repo copy, no conversation access); COO tool line untouched. tests/unit/test_send_log_plugin.py runs the node tests and checks the shape.
- Evidence: h37/node-tests.txt (13 pass), h37/strict-suite.txt (538 OK under -X dev -W error). Validator: the 7 blocking lines are all "tracked file not in registry" for the new files, because contracts/registry/artifacts.yaml is excluded from the patch by instruction; the planning chat registers them (h37/validator.txt). Before git add the validator showed 0 blocking.

## Part 2. Scratch proof (own state, own HOME, ports 19937 to 19939, no Slack, header-only state; all deleted)
1. Same scenario with and without the plugin (h37/scenarios/): same outcome (CFO logged the item with an event ID and run ID; same Slack-unavailable note). With the plugin the log got `coo -> cfo ... ok` and the CFO reply `cfo -> coo ... error`, no text (h37/scratch-lines/).
2. Error path seen for real. The CFO's reply into the COO session returns: `Session "<id>" changed while starting work. Retry.` with code SESSION_WORK_START_CHANGED (once or twice per run). The content still arrives. This confirms the earlier "session-change error" hypothesis. Masking and the withheld rule are also covered by unit tests.
3. CEO line: not testable without Slack in scratch; unit tests, then proved live (Part 3).
4. Restart loss: a normal stop right after the reply lost nothing (last line present). SIGTERM during a send: the gateway waited about 75 s for the run to end; the log held the send as `error | agent.wait unavailable during gateway restart` (the COO told the user the send was unconfirmed). No line was lost, but that send is recorded as error; the CFO reply line did not exist.
5. Startup: without send-log 12.1 s; with send-log 12.1 s, 16.6 s, 15.1 s (varies run to run, h37/startup-*.txt). Scratch had two fewer plugins than live (no ceo-ledger or gate-plugin), so this is "with versus without send-log".
6. COO read tool in scratch only (tools.alsoAllow read, fs.workspaceOnly true; tool calls seen by a throwaway probe, h37/probe/): (a) routed request same as without: PASS. (b) status question: same behaviour as v1.10.11 (asked the CFO, named it, run ID, no path or file name): PASS; it did not read the log by itself. Asked to read its send log: it could not find it (about 50 guessed read calls, no folder listing tool): the later instruction must give the exact file name pattern. (c) absolute path to a chief's file and a ../ path: both refused (read error, and the fallback exec also failed): PASS. (d) write a file: refused, no file created: PASS. Note: the COO also has the code-mode exec wrapper in all runs; it gave no way around the refusals here. Scratch only: nothing live changed for the COO.

## Part 3. Live install (done)
- Before: hashes, crontab, counts in h37/hashes-before.txt, crontab-before.txt, state-counts-before.txt (calendar events not listed: the listing prints event content; the journal counts are used instead).
- Gateway stopped, config backed up (~/loop1/state/openclaw.json.pre-send-log), plugin folder ~/loop1/state/extensions/send-log (4 files byte-equal to repo; node_modules link as for ceo-ledger), one config entry plugins.entries.send-log.enabled true (config otherwise equal to the backup, checked), gateway started: one process, new PID 382589 (was 308500). Slack probe 5 of 5. `openclaw plugins inspect send-log --runtime --json`: shape hook-only, capability mode none, 2 hooks (after_tool_call, message_received), no tools, services, commands, routes (h37/plugin-inspect-send-log.txt).
- Installed health-check.py replaced (backup ~/loop1/health-check.py.pre-h37, sha256 equal to repo copy).
- Proof 1: COO asked to send a synthetic item to the CFO: live log gained a `coo -> cfo | <run ID> | ok` line (the CFO reply line did not appear this time). Counts: CFO budget file 11 -> 12 lines.
- Proof 2: the CEO sent "@COO ping" and "@CFO ping": log gained `ceo-message | coo channel | <8 hex>` and `ceo-message | cfo channel | <8 hex>`, no text; CEO ledger 64 -> 66 (+2). A plain "ping" without @mention produced no event for either plugin (Slack mention rule), so the earlier "ping" left nothing.
- Proof 3: a synthetic show request went to the CLO only (`coo -> clo ... ok`; CLO lifestyle +1; CHO and CoS files unchanged). Journal and ledger counts as above; no plugin error in the gateway log.
- End state: crontab diff empty; config differs from start only by the send-log entry; all AGENTS.md and the ceo-ledger and gate-plugin files unchanged (hashes-before/after, only the config line differs); live log is 5 lines: header, 2 send, 2 ceo-message (metadata only).
- Health check (against the work copy that holds the plugin files): PASS 87, WARN 2, FAIL 0. WARN 1 is the compaction WARN (clears after the 05:25 run). WARN 2 "log: tools policy" counts 48 lines written by my scratch COO read-tool gateway (same log file, first line 01:21 AST, not the live gateway); it ages out of the 4000-line window. Against the plain repo copy the send-log hash line FAILS until the patch is pushed (files not in the repo yet).

## Rollback (exact)
systemctl --user stop openclaw-loop1-gateway
cp ~/loop1/state/openclaw.json.pre-send-log ~/loop1/state/openclaw.json
rm -rf ~/loop1/state/extensions/send-log
systemctl --user start openclaw-loop1-gateway
cp ~/loop1/health-check.py.pre-h37 ~/loop1/health-check.py
(the log file under the COO workspace may stay: metadata only.) Revert the repo patch.

## Not in this handover
COO read tool and instruction v1.10.12 are NOT installed live (scratch only). The COO workspace now has a state folder with the log file (new, untracked in the COO workspace git).

## Package
No token, Slack ID, session ID, session key, WirePusher ID, live log line or real item is in the package: evidence uses scratch lines only and shapes/counts for live; session IDs are replaced by <sid>.
