# ceo-plugin (APR-0102, handover 13): design and code, nothing installed
- design.md: design note (plugin shape, hook, ledger line, matching rule, failure modes, rollback).
- openclaw.plugin.json, package.json, index.js, ledger.js: the observe-only plugin (hook `message_received`).
- test/ledger.test.js: `cd ~/handover/ceo-plugin && node --test test/ledger.test.js` (10 tests; fake sender IDs only).
- gcal_sync.slack-ledger.patch, test_gcal_sync.slack-ledger.patch: unified diffs against the repo at HEAD a6b789d (`patch -p1` from the repo root); gcal_sync.py.new and test_gcal_sync.py.new are the full patched files. 17 new tests; 151 gcal unit tests OK with the patch.
- install-test-plan.md: plan for the install window. Not run.

## Handover 14 (APR-0103): approve_word, nothing installed
- ledger.js now writes `approve_word` (word lists in one place); test/ledger.test.js has 12 tests (`node --test test/ledger.test.js`).
- gcal_sync.approve-word.patch, test_gcal_sync.approve-word.patch: unified diffs against repo HEAD e803cbb (`patch -p1`); they sit on top of the handover 13 code that is already in the repo. gcal_sync.py.new and test_gcal_sync.py.new are the full new files (supersede the handover 13 `.new` files). 155 gcal unit tests OK.
- coo-reply-line-proposal.md: draft wording for the COO (v1.10.4). Not applied.
- install-test-plan.md updated (approve_word checks, "approve <event ID>", bare approve skips).
- The handover 13 patches (`*.slack-ledger.patch`) are kept as history; do not apply them again.
