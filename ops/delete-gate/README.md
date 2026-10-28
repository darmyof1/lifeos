# delete-gate files (APR-0100, handover 11)
- gcal_sync.ceo-ledger.patch: unified diff for scripts/gcal/gcal_sync.py (`patch -p1`, run from the repo root). Adds `--require-ceo-ledger PATH`, off by default.
- test_gcal_sync.ceo-ledger.patch: unified diff for tests/unit/test_gcal_sync.py (adds class CeoLedgerTests, 12 tests including the 5 inherited DeleteTests that run without the flag).
- gcal_sync.py.new, test_gcal_sync.py.new: the full patched files, for a fix script that copies instead of patching.
- rule-A-proposal.md: instruction rule, not applied.
Checked: both patches apply cleanly to the current repo copies (HEAD 6804ad3) and give files identical to the .new files; `python3 -B -m unittest discover -s tests/unit -p "test_gcal*.py"` 127 tests OK (was 115 without the new class).
Ledger line: {"time":"2026-10-28T01:02:03Z","run":"<run>","event":"<event>","channel":"slack|cli","sender":"CEO","text_sha256":"<64 hex>"}
