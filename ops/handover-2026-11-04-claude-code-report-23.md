# Report 23 (APR-0113, APR-0114)

Work was done in a scratch copy. Result: ONE patch, handover23.patch (no commit, no push). Unit suite: 383 tests, all pass. Validator: 0 blocking. Plugin tests: 11 pass (gate plugin), 12 pass (ledger plugin). History scan: clean. Evidence files are in h23/.

## Item 3 comes first: it needs a person (WAITING)
Missing: a second person and the CEO at the same time. Everything else is finished. Exact steps for the CEO to relay are in h23/item3-instructions.md and repeated here:
1. Tell me "ready". I check: calendar at the seed, crontab active, Slack ledger has 26 lines (26 now).
2. The CEO types in the COO channel: "Can you remove the workout on 2026-10-30 (CHO - Workout - 10302026-0001) from the calendar?" and waits for "waiting for approval of seed-3".
3. The second person types in the same channel: @COO approve seed-3
4. Wait three cron runs (about 15 minutes). Expected: no ledger line (sender is not the CEO) and nothing deleted.
5. The CEO types @COO approve seed-3 (or only @COO approve). Expected: one delete at the next cron run. I restore the seed and report ledger counts before and after each message (fields only), the cron results and the gate verdict.
Status: not run. Not skipped.

## Item 1: weekly encrypted backup (done; destination decision open)
- Files: scripts/ops/backup-weekly.sh, ops/recovery/backup-weekly.md, tests/unit/test_backup_weekly.py (13 tests, throwaway keys).
- Not installed: the cron line; no credential; no destination chosen. Options table and recommendation: Proposal 1 below.
- Live check (h23/backup-live.txt). The CEO's key file was absent, so a throwaway key was used in a separate keyring. Dry run changed nothing. --execute once: archive 174,657 bytes, 259 files, 0.12 s, 10 MB memory. Decrypted with the matching private key: exit 0. Archive sha256 line OK. FILES.sha256 inside the archive: 259 of 259 OK. All 258 live workspace files compared by sha256 to the extracted copies: 0 differ. The config copy has the token replaced and the real token value does not appear. The restore step that uses FILES.sha256 is therefore verified. Then the archive, the public key file, the fingerprint file, the key in the VM keyring and the private throwaway key were deleted.
- Caveat: the whole run took 0.12 s because the workspaces are small (under 1 MB). Timing will grow with the workspaces, not with the script.

## Item 2: gate wiring, design and test only (done on a scratch state folder; NOT wired)
- (a) gate.py: an override confirmation must carry request_hash equal to the request's hash and be 0 to 600 seconds old. Reason codes: override_confirmation_not_for_this_request, override_confirmation_expired (future time or missing clock: also denied). 29 tests in test_gate.py. Honest note: I changed the fixture of 3 older override tests (added request_hash and confirmed_at, passed a fixed clock). The logic they test did not change.
- (b) prefilter: src/lifeos/router/prefilter.py. Deviation: the rules are one JSON file, prefilter_rules.json, not a block at the top of prefilter.py, so Python and JS read the same data (no copy to drift). 51 test sentences (tests/data/prefilter_cases.json), 19 prefilter tests. Any doubt gives high.
- (c) plugin deploy/loop3/gate-plugin/: index.js, gate.js (line-by-line port), prefilter.js, openclaw.plugin.json, package.json, README.md, tests/gate.test.js (11 tests), tests/table.js. Parity: tests/unit/test_gate_parity.py runs the SAME 83-case JSON table (tests/data/gate_cases.json) through both gates and compares every answer, and the 51 sentences through both prefilters: all identical. The plugin folder holds byte copies of privacy.yaml and prefilter_rules.json; a test fails if they differ. Parity limits: float request IDs and exotic Unicode whitespace are not in the table.
- (d) scratch test (h23/gate-scratch.txt, gate-scratch-log.txt): own state folder, own port 18999, config copied with no tokens and no Slack, a local small model (no cloud call, cost 0). Results:

| Turn | Result |
|---|---|
| High (doctor and medicine) | Blocked: privacy_high_cloud_denied, plain message |
| High (salary and bank balance) | Blocked |
| Low (capital of France) | Passed the gate. The small local model then timed out at 83 s (CPU model, not the gate) |
| Low (capital of Italy) | Passed the gate, same timeout |
| Medium (schedule a meeting) | Blocked: medium_not_low_sensitivity |
| Missing label (no rule matched) | Blocked: treated as high |
| Rules file missing (hook error path) | Blocked |
| A real exception thrown inside the hook | Blocked: gate_plugin_error; log line "hook_error_blocked" |
Hook time: 1 to 4 ms per turn (limit 15 s). The scratch gateway kept running after every block and answered the next turn. It was stopped after the test, the scratch folder deleted. Live check afterwards: config sha256 and the four ceo-ledger plugin hashes identical before and after (h23/live-hashes-before.txt, live-hashes-after.txt); live gateway pid 3792080 unchanged, 0 restarts, port 18999 closed.
- Finding that matters for wiring: a non-bundled plugin may use before_agent_run only with plugins.entries.gate-plugin.hooks.allowConversationAccess set to true. Without it the gateway logs "blocked" and the gate silently does not run. The log is written in OpenClaw's staged copy of the plugin, not the source folder. CLI turns have no channel (logged as absent).
- (e) numbers. Prefilter on the 51 sentences: 34 truly high, 0 leaked as non-high. Of 17 truly non-high sentences, 4 were wrongly blocked (pay, weight, stock, partner): false-block rate 4 of 17 (24 percent), by design on near misses. Through the gate only 8 of those 17 pass (the 5 medium ones are blocked too). The 83-case gate table: 17 allow, 66 deny.
- What would still break if wired live: every turn needs a label, and only the prefilter gives one; medium turns are blocked; CHO and CFO turns are always blocked; cron, sessions_send and suite turns have no label source; the COO plus CoS routine would nearly all stop. See Proposal 2.

## Item 4: COO channel session measure (done; h23/d2/)
Route: openclaw agent --agent coo --session-key <the COO Slack channel session>, no delivery to Slack. Honest limit: this is the channel SESSION but the message does not come from Slack, so the ledger plugin sees nothing (fine for a delete REQUEST, which writes the pending line). Prep reset the state each run; 12 new run IDs loop3-h23-m1 to m12, alternating, about 2 minutes apart, finished well before the 02:30 limit. The instruction was unchanged.

| Arm | Runs | Pending line on the first try | Cost |
|---|---|---|---|
| No compact (odd runs) | m1, m3, m5, m7, m9, m11 | 4 of 6 (failed: m5, m11) | 0.0009 to 0.0029 USD each |
| Compact first (even runs) | m2, m4, m6, m8, m10, m12 | 6 of 6 | 0.0007 to 0.0038 USD each |
Total about 0.023 USD. Failing replies (IDs redacted):
- m5: "Nothing changed: CoS checked state/calendar-journal.md and confirms the workout remains recorded as pushed under event ID seed-3. CoS made no journal changes; the entry was not deleted. There's a discrepancy: CoS previously reported a pending-approval line for this entry under run loop3-h23-m4, but now reports no such line. To proceed, I still need a clear instruction from you to delete the workout."
- m11: "CoS checked the current journal and made no change in run loop3-h23-m11. The deletion is not recorded. CoS had previously reported a pending-approval line (event seed-3, run loop3-h23-m10), but now cannot confirm that line is still present. ... Still needed from you: Your approval is needed to proceed. If you want the workout removed, reply approve seed-3."
Pattern: both failures cite the previous run's pending line. The uncompacted channel session carries old runs and the COO answers from them instead of asking the CoS to write a new line. Small sample (6 and 6); not proof. Proposal 4 below.

## Item 5: drafts accepted
- (a) contracts/identity-access.yaml status accepted (APR-0113) with a known_differences block for the CFO (text lists only the COO; config also allows the CoS). 13 tests, one asserts the difference is still true. CFO instructions and config NOT changed. Two ways to close it: Proposal 3.
- (b) ops/success-metrics.md adopted from 2026-11-04; the health feed stays "design only, no real data".
- (c) research/hardware.md: direction recorded (home box for the high-privacy path after the gate is wired; no purchase, no setup). Shortlist searched 2026-11-04: Mac mini M4 Pro 48 GB (1,799 to 1,999 USD list, 1,869 refurbished lowest), Mac Studio M4 Max 64 GB (about 2,600 to 2,900 USD at resellers), NVIDIA DGX Spark 128 GB (3,999 to 6,950, sources disagree). Power, noise and some speeds are marked unknown. Safe link: private VPN tunnel, no open port. CEO decisions listed in the file.
- (d) ADR-0003 implementation note appended (the prefilter and plugin are now built and scratch-tested).
- (e) scripts/verify/history_scan.sh + 8 tests. Run on the repo (70 commits): clean for tokens, keys, IPs, Slack-ID shapes and emails in content. INFO for the CEO: the commit metadata holds 1 distinct author/committer email address, and the repo is public (APR-0114). Not printed here.

## Proposals (CEO decides)
### Proposal 1: where the weekly backup goes (off the VM)
Options (seven items each is in the table columns; the recommended one is written out below the table).

| Option | Cost | Who holds the keys | Risk |
|---|---|---|---|
| A. Private GitHub repository with Git LFS | Free for small sizes (the archive is about 0.2 MB now; 4 copies a year of growth is small); LFS quota is 1 GB free | The CEO holds the private decryption key. The VM holds only the public key and a GitHub deploy key with write access to that one repo | A leaked deploy key lets someone overwrite or delete backups; the content stays encrypted. GitHub account takeover is the main risk (turn on two-factor) |
| B. Object store (for example a cloud bucket with versioning) | Cents per month at this size | The CEO holds the private key; the VM holds an access key limited to one bucket | One more account and bill; a leaked access key can delete unless versioning and no-delete rules are on |
| C. The CEO's Mac pulls the archive by scp over the existing VPN | Free | The CEO holds both the private key and the pull key; the VM holds only the public key and gives read access to one folder | Works only when the Mac is on; a missed week is silent unless the Mac checks the file age |

What: send each weekly encrypted archive to a place that is not this VM.
Used for: restoring the four agent workspaces and a token-free config if the VM is lost.
Why now: the script and tests are ready and the live check passed; without a destination the archive stays on the same disk it protects.
Risk if approved: option A adds a deploy key on the VM; the data is encrypted before it leaves, so a leak exposes only that backups can be overwritten.
Risk if not: a VM loss loses everything the agents wrote since the last copy that exists elsewhere.
Recommendation: option A (private GitHub repository with Git LFS), because it needs no new account and no always-on machine, and the CEO already uses GitHub. Keep the private key off the VM and off GitHub.
Reply: approve, explain more, or keep.

Crontab line, shown and NOT installed (needs the public key file and fingerprint file in place first): `30 6 * * 0 bash $HOME/lifeos-ro/scripts/ops/backup-weekly.sh --execute >> $HOME/loop1/backups/backup.log 2>&1`

### Proposal 2: wire the gate live
What: install the gate plugin in the live gateway so every agent turn is checked before it reaches a cloud model.
Used for: enforcing the privacy rule in code instead of in instruction text.
Why now: the scratch test passed (high blocked, low passes, missing label blocked, hook error blocks, 1 to 4 ms per turn, gateway keeps running).
Risk if approved: practically only prefilter-low turns pass today. Medium turns are blocked too (the policy has no sensitivity value for them). CHO and CFO turns are always blocked. Cron, sessions_send and suite turns carry no label except the prefilter's guess, so most agent work would stop. The hook needs `hooks.allowConversationAccess` in the config, or it is silently absent (no gate).
Risk if not: the gate stays unwired; privacy rests on instruction text only.
Recommendation: keep for now. First decide what a medium turn should be allowed to do and how internal turns (cron, sessions_send) get a label; then wire on a second scratch run with those turns, then live in a window with the CEO present.
Reply: approve, explain more, or keep.

### Proposal 3: the CFO send-list difference
Known difference: the CFO instruction text lists only the COO as a recipient, but the config also lets the CFO send to the CoS. Nothing was changed.
Option 1: change the CFO instruction text to list the CoS too. Used for: the text matches what the config allows. Risk: the CFO may start messaging the CoS more.
Option 2: remove the CoS from the CFO send list in the config. Used for: the config matches the text and the CFO has fewer paths. Risk: needs a config change and a gateway restart; anything that relied on that path stops.
What: close the difference between instruction text and config for the CFO.
Why now: the identity-access contract is accepted and records the difference.
Risk if approved: see the two options.
Risk if not: the contract keeps a known difference; no known harm.
Recommendation: option 2 (the narrower permission), at the next planned restart.
Reply: approve, explain more, or keep.

### Proposal 4: compact the COO channel session before a request
What: run sessions compact on the COO Slack channel session before each CEO request, as a manual step now, later as a scheduled job (outside 03:30 to 05:10).
Used for: the COO writing the pending line on the first try.
Why now: measured 6 of 6 with compact against 4 of 6 without.
Risk if approved: compact may drop context the CEO expects the COO to remember; a scheduled job could run while a request is open.
Risk if not: about one delete request in three may need to be asked again.
Recommendation: a scheduled job before the CEO's usual start, not a manual step, plus a repeat of the measure (20 runs) before relying on it. No instruction change.
Reply: approve, explain more, or keep.

## End state (checked 2026-11-04 after the work)
Gateway one process (pid 3792080, 0 restarts). Crontab identical to crontab-final.txt, cron active. Calendar at the seed (3 workouts, 1 busy), journal 3 0. Plugin enabled, config and four plugin hashes unchanged. Health check PASS 74, WARN 0, FAIL 0. No agent instruction or config was changed. Time rules: no agent message or restart between 03:30 and 05:10 (the first live action was 05:11).
