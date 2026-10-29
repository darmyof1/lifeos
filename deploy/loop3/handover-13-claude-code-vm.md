# Handover 13 to Claude Code on the LifeOS VM (delete gate step A: the CEO ledger plugin, design and code only)

Same Claude Code as handovers 1 to 12. The CEO approved building and testing the plugin code (APR-0102). He did NOT approve installing it: nothing in this handover is installed in the gateway. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0102 ..." at the top, with the handover 12 commit below it). If it is missing, stop and tell the CEO.

## Hard limits (as before, plus)
1. No change to any agent file, config, binding, cron or the gateway. No gateway restart. The plugin is NOT loaded into the gateway in this handover.
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, tokens, calendar ID or VM address in ~/handover/ or the repo. The CEO's Slack user ID lives only in a local file `~/loop1/ceo-slack-id` (mode 600) that you do not create with a real value; tests use a fake ID.
3. TIME WINDOW: no agent message or `sessions compact` between 03:30 and 05:10 AST. Cost near zero (no agent runs are needed).
4. Journals and git history append-only.

## Read first
APR-0100, APR-0101, APR-0102; ops/handover-2026-10-28-claude-code-report-11.md (Task 1 answer, the `message_received` hook, the transcript fields); ops/delete-gate/; the OpenClaw docs on plugins and hooks on this VM (docs/plugins/hooks/messages.md and the plugin authoring pages); scripts/gcal/gcal_sync.py (`ceo_approval_recorded`).

## Task 1. Design note (~/handover/ceo-plugin/design.md)
Answer, from the docs and the source on this VM, with evidence:
1. Plugin shape: where a plugin lives, how it is declared, loaded and removed, what permissions it needs, and whether it can run in observe-only mode (it must NOT be able to change, block or reply to a message).
2. What `message_received` gives (sender ID, channel, conversation, message ID, text, session or run correlation) and whether it fires for Slack messages in all four agent channels and for CLI messages.
3. What the ledger line holds. Proposal to confirm or improve: {"time","channel":"slack","conversation","message_id","sender":"CEO","text_sha256","event_tokens":[...]} where event_tokens are the tokens of the message that look like event IDs or run IDs (letters, digits and hyphens, at least one hyphen and one digit, 3 to 64 chars). The plugin stores the hash and the tokens, not the message text.
4. How the push job matches a deleted line to a Slack ledger entry. The CEO's approval text does not always carry the event ID (the D2 scenario message does not). The COO layout asks the CEO to cite it. Propose the matching rule and its failure modes: (a) the event ID must appear in event_tokens; (b) ordering: the journal has no time column, so propose how to know the approval came after the pending line (for example the job records the first time it saw the pending line in its state dir; an entry older than that, or older than N hours, does not count); (c) one approval covers one event once (no reuse); (d) what happens if the CEO approves in a different channel than the one the request came from.
5. Failure modes of the plugin itself: it crashes, the ledger directory is unwritable, the gateway restarts, a message arrives twice. The default must be "no ledger line, so no delete" (fail closed).
6. Rollback: how to remove the plugin and what that leaves (the check stays off in the cron, so deletes behave as before this work).

## Task 2. Code, tested away from the gateway
In ~/handover/ceo-plugin/: the plugin source, the ledger writer, and unit tests that feed fake `message_received` payloads (fake sender ID, never a real one): CEO message writes one line; another sender writes nothing; a duplicate message ID writes once; an unwritable directory writes nothing and does not throw into the gateway; tokens are extracted correctly; the text is not stored. Also the extension of `ceo_approval_recorded` in scripts/gcal/gcal_sync.py (as a patch for me to turn into a fix script, with tests in the style of the existing CeoLedgerTests) for the Slack ledger matching rule you propose. Keep the existing scenario-ledger path working.

## Task 3. Test plan for the install (do not run it)
Write ~/handover/ceo-plugin/install-test-plan.md: the exact steps for the install window (outside 03:30 to 05:10), the one gateway restart, how to check the plugin loaded and is observe-only, one test message from the CEO and one from a non-CEO sender, a regression run before and after (D1, D2, D3 three each), and the rollback commands. The CEO will read it and give a separate yes (new APR) before anything is installed.

## Report (~/handover/REPORT-13.md)
Answer Task 1 first in plain words (can the plugin be observe-only and fail closed; what the matching rule is and what it cannot prove). Then files and test results. Failures as they happened. Nothing installed; say so. Package with `tar czf ~/handover-13.tar.gz -C ~ handover` after a secrets check.
