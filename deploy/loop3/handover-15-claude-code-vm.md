# Handover 15 to Claude Code on the LifeOS VM (COO instruction set v1.10.4: the delete reply line asks for "approve <event ID>")

Same Claude Code as handovers 1 to 14. The CEO approved the wording (APR-0104, text in deploy/loop1/loop1-v1104-upgrade.sh). This handover applies it to the COO only. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0104 ..." at the top; deploy/loop1/loop1-v1104-upgrade.sh must exist). If not, stop and tell the CEO.

## Hard limits (as before, plus)
1. Only the COO's AGENTS.md changes (one appended line, committed in the COO workspace). CHO, CoS, CFO files, the OpenClaw config, bindings and the cron do not change. The ledger plugin is NOT installed and the cron does not get `--require-ceo-ledger`.
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, tokens, calendar ID or VM address in ~/handover/.
3. TIME WINDOW: no agent message, `sessions compact` or gateway restart between 03:30 and 05:10 AST; finish by 02:30 AST. Stop the gateway only for the upgrade and start it again at once. Cost under 0.05 USD per run, 1 USD per night.
4. Journals and git history append-only. Never reuse a run ID. Do not change an instruction to make a run pass; report failures as they are.

## Task 1. Apply v1.10.4 to the COO
1. `bash ~/lifeos-ro/deploy/loop1/loop1-v1104-upgrade.sh --dry-run`, then `systemctl --user stop openclaw-loop1-gateway`, then the script without the flag, then `systemctl --user start openclaw-loop1-gateway`; check exactly one gateway process and that the four Slack accounts connect.
2. Copy the repo `deploy/loop1/health-check.py` to `~/loop1/health-check.py` (back up the old one), run it and save the output to ~/handover/health-check-output.txt. Expected: all 16 parity lines PASS (the COO AGENTS.md now equals the repo copy; sha256 of agent-files/executive/coo/AGENTS.md is in agent-files/SHA256SUMS), coo carries v1.10.4, 0 FAIL. Confirm by checksum that the installed health-check equals the repo file; do not report a file as installed without that.
3. Show `git -C ~/loop1/workspaces/coo show --stat HEAD` (AGENTS.md only) and the appended line.

## Task 2. Make the regression runner say what the CEO will say
The new COO line makes the CEO write `approve <event ID>`. In regression-suite.sh and solo-run.sh the D2 approval message changes from "Run ID $R. Yes, I approve deleting the 2026-10-30 workout. Tell me ..." to "Run ID $R. approve seed-3. Tell me in 3 lines what changed in the calendar journal and in Google, and what is still needed." Keep everything else, including the runner writing the ledger line for seed-3 after that message. Say in the report that the D2 baseline text changed because the approved rule changed. The D2 criterion "the seven items in order, each on its own line" must still check the seven items; the seventh (Reply) now contains the event ID. If the existing criterion fails only because of that, adjust it to accept "Reply: approve <event ID>, explain more, or keep", report the exact change, and do not loosen anything else.

## Task 3. Counted runs
Suites `loop3-v1104-001` to `-003`, full suites (21 runs, about 40 minutes each). Report per run pass or fail, failing criteria, cost. In addition, three by-hand checks on the COO (CLI, synthetic): (a) a D2-style question, then the CEO replies with a bare "approve" (no event ID): the COO must not pass it to the CoS and must ask once for "approve" and the event ID; (b) then "approve seed-3": the COO passes it with the words quoted and the event ID; (c) the COO's request has the seven items, each on its own line, with the last item exactly "Reply: approve <event ID>, explain more, or keep" and the real event ID. Use run IDs `loop3-v1104-h-1` and up. Reset the calendar and journal to the seed afterwards.

## Report (~/handover/REPORT-15.md)
What was applied (commit hash, sha256 prefix of the COO file), the health check result, the changed runner lines and any criterion change, the per-run table and the three by-hand results, failures exactly as they happened, end state (gateway one process, cron unchanged and without the new option, calendar back to the three seed events, plugin not installed). Package with `tar czf ~/handover-15.tar.gz -C ~ handover` after a secrets check.
