# Handover 14 to Claude Code on the LifeOS VM (delete gate step A: approve-word flag and the COO reply line, code and drafts only)

Same Claude Code as handovers 1 to 13. The CEO chose (APR-0103): the plugin also records whether a message approves (an approve word with no negation), the job requires it, and the COO's request line will ask for "approve <event ID>". Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0103 ..." at the top, with the handover 13 commit below it; deploy/loop3/ceo-plugin/ must exist). If not, stop and tell the CEO.

## Hard limits (as before)
1. Nothing is installed: no plugin entry in the config, no gateway restart, no agent file change, cron unchanged and without `--require-ceo-ledger`. The COO line is a DRAFT file only.
2. Synthetic data only; no secrets, Slack IDs or tokens anywhere. Tests use fake sender IDs.
3. No agent message or `sessions compact` between 03:30 and 05:10 AST. No model cost needed.

## Task 1. Plugin: `approve_word`
In ledger.js add a boolean `approve_word` to each ledger line. Fail closed: true only when the text contains a whole-word approval (approve, approved, approving; case-insensitive) AND contains none of the blocking words (not, no, never, cannot, without, cancel, stop, keep, explain, dont, don't, do not, cant, can't, wont, won't, "hold off", "wait"). A message with both "approve" and "keep" (for example a pasted copy of the COO's reply line "approve, explain more, or keep") is false. The text is still not stored. Write your own word lists in one place, say in design.md that they are conservative on purpose (a false is safe, the CEO just writes the message again), and add tests: "approve loop2-x-01" true; "approved: loop2-x-01" true; "do not approve loop2-x-01" false; "Reply: approve, explain more, or keep" false; "please keep it" false; "no" false; "approve" alone true (the event-ID check is the job's); mixed case; punctuation; empty text.

## Task 2. Job: require it
In scripts/gcal/gcal_sync.py a Slack ledger entry counts only if `approve_word` is true (a missing field means false). Scenario-ledger entries (no event_tokens) are unchanged. Add tests next to the existing Slack-ledger tests (entry with the field false: no delete; field missing: no delete; true plus the event token: delete as before). Give the patch as a unified diff plus the full new files, as in handover 13.

## Task 3. Draft the COO reply line (do not apply)
Write ~/handover/ceo-plugin/coo-reply-line-proposal.md: the exact replacement for the last item of the seven-item approval request ("Reply: approve, explain more, or keep") so that it carries the event ID, for example "Reply: approve <event ID>, explain more, or keep". Quote the existing COO rules it changes (v1.10, v1.10.1, v1.10.3 lines), say which instruction-set version number is next (v1.10.4), and give the text to append in the same style as the earlier upgrade scripts (loop1-v1103-upgrade.sh). Do not write the upgrade script, do not touch any live file: the CEO approves the wording first (a new APR). Also state what the CEO should type: the exact message, and that a bare "approve" will not delete.

## Task 4. Update the install plan
Update ~/handover/ceo-plugin/install-test-plan.md: in the observe-only checks add messages that test approve_word (one true, one "do not approve" false, one with the pasted reply line false, each checked in the ledger by field only, never printing an ID); in step 5 the CEO's approval message becomes "approve <event ID>"; add the check that a bare "approve" skips the delete.

## Report (~/handover/REPORT-14.md)
Plain words first: what changed, what the lists are, what still cannot be proved (intent beyond the word lists). Then test counts (node and the repo unit tests). State that nothing is installed. Failures as they happened. Package with `tar czf ~/handover-14.tar.gz -C ~ handover` after a secrets check.
