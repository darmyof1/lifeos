# REPORT 14 - delete gate step A: approve word, job requirement, COO reply line draft (APR-0103)

Pulled first: HEAD e803cbb "APR-0103 ..." with the handover 13 commit (4c5ba43) below it; `deploy/loop3/ceo-plugin/` exists. No agent message, no compaction, no gateway restart, no model cost. **Nothing is installed**: the config has no ceo-ledger entry (openclaw.json unchanged since 2026-10-27 22:57), the cron has 0 `--require-ceo-ledger` lines, `~/loop1/ceo-slack-id` does not exist, `~/loop1/ceo-ledger/` holds only the scenario ledger, and the COO line is a draft file only.

## In plain words
- **What changed:** each Slack ledger line now carries `approve_word`, true or false. The job deletes only if it is true and the line also names the event ID. So the CEO must write `approve <event ID>`. A bare "approve" is recorded as true but names no event, so the delete waits.
- **The lists** (all in `ledger.js`, said in design.md section 3):
  - Approve words, whole word, any case: approve, approved, approving.
  - Blocking words: not, no, never, cannot, without, cancel, stop, keep, explain, dont, don't, cant, can't, wont, won't, wait; phrases "do not" and "hold off".
  - Any blocking word makes it false, even next to "approve". A pasted copy of the COO line "Reply: approve <id>, explain more, or keep" is false.
  - The lists are conservative on purpose: a false is safe, the CEO just writes the message again.
  - Accepted side effects: an event ID with a piece like `no` or `stop` (the ID is split at hyphens) makes the message false; "approval", "approves" and "disapprove" are false.
- **What still cannot be proved:** intent beyond the word lists. "I might approve loop2-x-01 later" counts as an approval. A message that approves a different thing but also names the event ID counts. The job also still cannot tell that the message answers this request, and an approval made more than 5 minutes before the job first saw the pending line is rejected (fails closed). Details in design.md section 4.
- **COO line:** `coo-reply-line-proposal.md` has the exact new last item "Reply: approve <event ID>, explain more, or keep", the v1.10, v1.10.1 and v1.10.3 lines it touches, the next version (v1.10.4) and the text to append, and what the CEO should type. Not applied, no script written. It needs a new APR for the wording.

## Files (`~/handover/ceo-plugin/`)
- `ledger.js` (approveWord, APPROVE_WORDS, BLOCK_WORDS, BLOCK_PHRASES; field `approve_word` last in the line), `test/ledger.test.js`.
- `gcal_sync.approve-word.patch`, `test_gcal_sync.approve-word.patch`: diffs against repo HEAD e803cbb (which already holds the handover 13 code), `patch -p1`, verified to give files identical to `gcal_sync.py.new` and `test_gcal_sync.py.new` (full new files).
- `coo-reply-line-proposal.md`, `install-test-plan.md` (updated, not run), `design.md` (updated), `README.md`.

## Test results
- Plugin: `node --test test/ledger.test.js` 12 of 12 pass (10 before; the field-list test was updated, 2 new). The new tests cover: "approve loop2-x-01", "approved: loop2-x-01", "approve" alone, mixed case, punctuation, quotes, new lines, "I am approving" (true); "do not approve", "don't"/"don’t approve", "Reply: approve, explain more, or keep", "please keep it", "no", empty text, null/undefined, "disapprove", "approval", "approves", "approve ... but wait", "hold off, approve" (false); and the field in the written line, with the text still not stored.
- Push job: 4 new tests in `SlackLedgerTests` (field false, missing, a string "true" and null: no delete; true plus token: delete; a later approving message after a non-approving one: delete; scenario entries need no `approve_word`). The existing entry helper now sets `approve_word: true`, so the earlier 17 tests are otherwise unchanged. `python3 -B -W error::ResourceWarning -m unittest discover -s tests/unit -p "test_gcal*.py"` in a temp copy of HEAD with the new files: 155 tests, all OK (151 before).

## Failures as they happened
- My first draft of the job test was a placeholder with a meaningless assertion; I replaced it with the real tests before running anything.
- Running the gcal tests with `-W error::ResourceWarning` prints two `unclosed ssl.SSLSocket` warnings. They are identical on the unpatched repo (2 before and after), so they do not come from this change; the run still ends OK. Not investigated.
- Nothing else failed.

## Install plan changes
Observe-only checks gained three messages (true, "do not approve" false, pasted reply line false), read by field only. Step 5 now uses exactly "approve <event ID>" and adds the bare "approve" and "do not approve <event ID>" skips. Acceptance includes them.

## Not done on purpose
No install, no config, no restart, no cron change, no agent file change, no upgrade script, no push to the repo (the clone is read-only; the files are in `~/handover/`). The repo shows one untracked file named `0` that was there at the start; I did not touch it.

## Needs the CEO
A new APR for the COO wording (v1.10.4), then a separate yes (new APR) for the install, with the CEO typing the Slack ID into `~/loop1/ceo-slack-id`.
