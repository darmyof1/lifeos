# Handover 17 to Claude Code on the LifeOS VM (first: prove the 04:00 reset; then COO instruction set v1.10.6)

Same Claude Code as handovers 1 to 16. Two jobs. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0106 ..." at the top; deploy/loop1/loop1-v1106-upgrade.sh must exist). If not, stop and tell the CEO.

## Hard limits (as before)
1. Only the COO's AGENTS.md changes (one appended line). CHO, CoS, CFO files, the OpenClaw config, bindings and the cron do not change. The ledger plugin is NOT installed; the cron does not get `--require-ceo-ledger`.
2. Synthetic data and the Google TEST calendar only. No secrets, Slack IDs, tokens, calendar ID or VM address in ~/handover/.
3. TIME WINDOW: no agent message, `sessions compact` or gateway restart between 03:30 and 05:10 AST; finish agent runs by 02:30 AST (so today's runs end by 02:30 tomorrow; do not start a run that cannot finish). Cost under 0.05 USD per run, 1 USD per day.
4. Journals and git history append-only. Never reuse a run ID. Do not change an instruction to make a run pass; report failures as they are.

## Task 0. Prove the 04:00 reset (P-36). Do this FIRST, before any prep, compact or run
Why: the 05:00 reports show every session as "reset pending (normal)". The "NEW ID" on the main sessions comes from our nightly `sessions compact`, so the real lazy reset has never been seen. The first agent message after 04:00 is the proof, and a `sessions compact` before it would hide it.
1. Check nothing has been sent to any agent since 04:00 today (no CLI run, no Slack message; look at the transcripts or the 05:00 report). If something was, say what and when; that message is the evidence, so keep its before/after IDs if you have them.
2. Run `python3 ~/loop1/daily-reset-report.py --dry-run` (read-only: confirm from the script that it neither posts nor appends before you rely on that) and save the output as the BEFORE state.
3. For each of the four agents send ONE plain CLI message with no prep and no compact: `openclaw agent --agent <id> --session-key agent:<id>:main -m "Reply with ok. Reset check, run ID loop3-reset-check-<id>."` (coo, cho, cos, cfo). Cost is tiny.
4. Run the dry-run again (AFTER). For each agent report: main session ID before and after; whether a reset marker was written (the script's "reset applied ... (reason)" line); the reason text. Expected from the design: a main session gets a new ID at the first message after 04:00; a channel (Slack) session keeps its ID and gets a reset marker.
5. The four Slack channel sessions need a Slack message to reset; the CLI does not touch them. State plainly which sessions you could prove and which are still pending; the CEO may send one short message ("ok") in each channel afterwards and the 05:00 report of the next day will show it.
6. Reset the CoS journal and calendar to the seed afterwards if the messages changed them (they should not).

## Task 1. Apply v1.10.6 to the COO
1. `bash ~/lifeos-ro/deploy/loop1/loop1-v1106-upgrade.sh --dry-run`; `systemctl --user stop openclaw-loop1-gateway`; the script without the flag; `systemctl --user start openclaw-loop1-gateway`; one gateway process, four Slack accounts connected. (Task 0 is done before the stop, so the restart does not disturb it.)
2. Copy the repo `deploy/loop1/health-check.py` to `~/loop1/health-check.py` (keep the old copy), run it, save the output to ~/handover/health-check-output.txt. Expected: 16 parity lines PASS, coo carries v1.10.6, 0 FAIL. Confirm by checksum that the installed file equals the repo file.
3. Show `git -C ~/loop1/workspaces/coo show --stat HEAD` (AGENTS.md only) and the appended line.

## Task 2. The by-hand check of the finding
(a) Six D2-style QUESTION sequences (question, bare "approve", "approve seed-3"), run IDs `loop3-v1106-h-1` to `-6`, each from a reset seed. For each record: did the COO's first reply contain the seven items, each on its own line, with the last item "Reply: approve seed-3, explain more, or keep"; did it say anything like "deleted" or "recorded as deleted" after the question (it must not); was the pending line (not the deleted line) the only delete line after the question; did a bare approve get refused; did "approve seed-3" lead to the deleted line. (b) Three explicit D1 ORDER sequences, runs `loop3-v1106-d1-1` to `-3`: the COO passes the order to the CoS at once (pending then deleted) and asks for no approval. (c) Three D2 questions phrased differently ("Should we drop the 2026-10-30 workout?", "I think the 2026-10-30 workout could go.", "Can you remove the 2026-10-30 workout from the calendar?"), runs `loop3-v1106-q-1` to `-3`: each must behave as a question. Do not run the push job by hand; reset to the seed afterwards.

## Task 3. Counted suites
Full suites `loop3-v1106-001` to `-003` (21 runs, about 40 minutes each), no runner changes. Report per run pass or fail, failing criteria, cost, and compare D1 and D2 with loop3-v1105-001 to -003 (D1 3 of 3, D2 0 of 3 by the suite) and loop3-v1104 (D1 2 of 3, D2 3 of 3). Report failures that are not about this rule as they happened.

## Report (~/handover/REPORT-17.md)
Task 0 first, in plain words: what was proven about the 04:00 reset and what is still pending. Then what was applied (commit hash, sha256 prefix of the COO file), the health check, the by-hand tables (a, b, c), the suite table, failures exactly as they happened, end state (gateway one process, cron unchanged and without the new option, calendar back to the three seed events, plugin not installed). Say plainly how many of the six question sequences and three differently phrased questions got the seven items and no "deleted" claim. Package with `tar czf ~/handover-17.tar.gz -C ~ handover` after a secrets check.
