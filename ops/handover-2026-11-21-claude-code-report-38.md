# REPORT 38 (APR-0137): COO v1.10.12 and the COO read tool, live

## H35 Part 3: compaction check (first)
- 2026-11-21 05:25 AST run: result=compacted, size_before=11278, kept_lines=1 (size_after not reported by the script). Not an error.
- Health check re-run: the compaction WARN is gone (`h38/compact-log-tail.txt`, `h38/health-before.txt`).

## Part 1: repo (patch `handover38.patch`, 8 files, `git apply --check` ok on a fresh clone)
- COO AGENTS.md: the v1.10.11 Status rule replaced in place by the approved v1.10.12 wording. One Status rule.
- New `deploy/loop1/loop1-v11012-upgrade.sh`; v11010 and v11011 scripts skip on later versions.
- health-check.py: COO v1.10.12; new line "coo read-only, own workspace".
- Tests updated; strict suite 539 OK.

## Part 2: live
- Gateway stopped; dry run (`h38/live-dryrun.txt`); apply (`live-apply.txt`, commit "Loop 1 instructions v1.10.12 (APR-0137)" in the COO workspace git); second run "already v1.10.12" (`live-second-run.txt`); live file equals the repo-copy file; diff `coo-agents-diff.txt`.
- Config diff only these keys (`config-diff.txt`): agents.entries.coo.tools.alsoAllow ["read"], agents.entries.coo.tools.fs.workspaceOnly true. Backup `openclaw.json.pre-h38`.
- Gateway started once; one process (`gw-process.txt`); Slack 5 of 5 (`slack-probe.txt`).
- Health check installed from the repo copy (sha256 equal; backup `health-check.py.pre-h38`).
- Health result: PASS 88, WARN 1, FAIL 0 (`health-after-work38.txt`, parity run against the patched copy). Parity against `~/lifeos-ro` FAILS until the patch is pushed (`health-after.txt`).
- The 1 WARN: gateway log line "tools policy: profile messaging (agent coo) ... Add alsoAllow write, edit". It is logged on every COO run now. It is expected for a read-only COO. The WARN does not mean a fault; it needs a decision (change the health rule or accept it). Not changed.
- Tools: the COO has one file tool, read. No write, no edit. It also keeps the exec wrapper; in scratch and in proof 7 it could not reach files outside its workspace or write.
- Hashes before/after: only openclaw.json and the COO AGENTS.md changed. send-log, ceo-ledger, gate-plugin files, other agents' instructions and the crontab are equal.
- Counts: CFO budget +2 lines (Test Item Seven, Eight), CLO lifestyle +2 (Show Seven-D, Test Place Seven-E), COO send log 5 to 21 lines (`counts-*.txt`, `log-shape-after.txt`: 17 send, 3 ceo-message, 5 error-with-"changed while starting work"). No existing line changed.

## Part 3: proofs (CLI explicit sessions loop38-..., replies in `h38/scenarios/replies.md`)
1. Route purchase to CFO: ok, 2 log lines added.
2. "What did I last tell the CFO?" fresh session: read, asked CFO, named Test Item Seven, CFO, run ID; no path. PASS.
3. CLO item logged; fresh "What did I last tell the CLO...": right item, run ID, no path. PASS.
4. Pension question: not "nothing found": the CFO holds a real record and the COO relayed it, no path. Content withheld from this package (real data). Result: no path, but the expected "nothing found" did not apply.
5. Test Item Eight typed directly to the CFO: COO found it via the CFO, named the CFO. No run ID for that entry (this route is not logged); it gave its own lookup run ID.
6. Routing unchanged: lifestyle to CLO only, budget question to CFO.
7. Outside-workspace read refused; file creation refused; nothing created, workspace listing unchanged.
8. CEO in the COO channel: read the log (named newest send time and run ID), asked the CFO, named the CFO, gave a run ID, no path or file name, right item: all yes per the CEO's pasted answer. Note: the COO added a "late reply" line.
- Cost per run: not recorded (raw run output was reduced to replies to keep real data out). Say so plainly; no run was near limits.

## Rollback
1. systemctl --user stop openclaw-loop1-gateway
2. cp ~/loop1/state/openclaw.json.pre-h38 ~/loop1/state/openclaw.json (removes the two keys)
3. cd ~/loop1/workspaces/coo && git revert --no-edit <v1.10.12 commit> (previous file also saved in ~/start38)
4. systemctl --user start openclaw-loop1-gateway
5. cp ~/loop1/health-check.py.pre-h38 ~/loop1/health-check.py
6. Revert the repo patch.

## Package notes
No token, Slack ID, WirePusher ID, live log line or real item is in the package. Session ids are not included. Open: stray ~/lifeos-ro/0; the WARN decision above.
