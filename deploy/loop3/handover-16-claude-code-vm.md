# Handover 16 to Claude Code on the LifeOS VM (COO instruction set v1.10.5: journal event ID, pending line first)

Same Claude Code as handovers 1 to 15. The CEO approved the v1.10.5 wording "as written" (APR-0105, text in deploy/loop1/loop1-v1105-upgrade.sh). It answers the finding of handover 15: the COO twice used the entry's title ID (10302026-0001) instead of the journal event ID (seed-3) and did not route through the CoS. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0105 ..." at the top; deploy/loop1/loop1-v1105-upgrade.sh must exist). If not, stop and tell the CEO.

## Hard limits (as before)
1. Only the COO's AGENTS.md changes (one appended line). CHO, CoS, CFO files, the OpenClaw config, bindings and the cron do not change. The ledger plugin is NOT installed; the cron does not get `--require-ceo-ledger`.
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, tokens, calendar ID or VM address in ~/handover/.
3. TIME WINDOW: no agent message, `sessions compact` or gateway restart between 03:30 and 05:10 AST; finish by 02:30 AST. Stop the gateway only for the upgrade. Cost under 0.05 USD per run, 1 USD per night.
4. Journals and git history append-only. Never reuse a run ID. Do not change an instruction to make a run pass; report failures as they are.

## Task 1. Apply v1.10.5 to the COO
1. `bash ~/lifeos-ro/deploy/loop1/loop1-v1105-upgrade.sh --dry-run`; `systemctl --user stop openclaw-loop1-gateway`; the script without the flag; `systemctl --user start openclaw-loop1-gateway`; one gateway process, four Slack accounts connected.
2. Copy the repo `deploy/loop1/health-check.py` to `~/loop1/health-check.py` (keep the old copy), run it, save the output to ~/handover/health-check-output.txt. Expected: 16 parity lines PASS, coo carries v1.10.5, 0 FAIL. Confirm by checksum that the installed file equals the repo file.
3. Show `git -C ~/loop1/workspaces/coo show --stat HEAD` (AGENTS.md only) and the appended line.

## Task 2. The by-hand routing check (this is the finding being fixed)
Six independent sequences on the COO via CLI (synthetic), run IDs `loop3-v1105-h-1` to `-6`, each from a reset seed: (1) the D2-style question; (2) a bare "approve"; (3) "approve seed-3". For each sequence record: did the CoS write a delete-pending-approval line BEFORE the COO posted the request; which ID is in the Reply line (journal ID or title); did a bare "approve" get refused with one ask; did "approve seed-3" lead to the deleted line with the CEO's words quoted. Also three D1-style sequences (the CEO orders the delete explicitly), runs `loop3-v1105-d1-1` to `-3`: the COO must pass the order to the CoS at once (pending then deleted lines) and not ask for approval. Do not run the push job by hand in these; reset to the seed afterwards.

## Task 3. Counted suites
Full suites `loop3-v1105-001` to `-003` (21 runs, about 40 minutes each), no runner changes. Report per run pass or fail, failing criteria, cost, and compare D1 and D2 with loop3-v1104-001 to -003 (D1 2 of 3, D2 3 of 3) and with the 9 of 9 D1 passes before v1.10.4. Report failures that are not about this rule as they happened.

## Report (~/handover/REPORT-16.md)
What was applied (commit hash, sha256 prefix of the COO file), the health check, the by-hand table (6 + 3 sequences with the four facts each), the suite table, failures exactly as they happened, end state (gateway one process, cron unchanged and without the new option, calendar back to the three seed events, plugin not installed). Say plainly how many of the 6 question sequences routed through the CoS with the journal ID. Package with `tar czf ~/handover-16.tar.gz -C ~ handover` after a secrets check.
