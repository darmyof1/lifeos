# ceo-plugin (APR-0102, handover 13): design and code, nothing installed
- design.md: design note (plugin shape, hook, ledger line, matching rule, failure modes, rollback).
- openclaw.plugin.json, package.json, index.js, ledger.js: the observe-only plugin (hook `message_received`).
- test/ledger.test.js: `cd ~/handover/ceo-plugin && node --test test/ledger.test.js` (10 tests; fake sender IDs only).
- gcal_sync.slack-ledger.patch, test_gcal_sync.slack-ledger.patch: unified diffs against the repo at HEAD a6b789d (`patch -p1` from the repo root); gcal_sync.py.new and test_gcal_sync.py.new are the full patched files. 17 new tests; 151 gcal unit tests OK with the patch.
- install-test-plan.md: plan for the install window. Not run.
