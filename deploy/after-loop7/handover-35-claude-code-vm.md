# Handover 35 to Claude Code on the LifeOS VM (COO morning compaction ignores Slack thread sessions)

Same Claude Code as handovers 1 to 34. The CEO chose option A (APR-0134, deploy/after-loop7/coo-compaction-threads-draft.md). Background: the 05:25 compaction (scripts/ops/coo-compact.sh, APR-0121) finds the COO channel session by the key prefix agent:coo:slack:channel: and needs exactly one. A Slack thread session (key ends :thread:<ts>) has the same prefix, so the script finds two, logs "error (COO channel sessions found: 2 (need exactly 1))" and compacts nothing. The change: the channel session is the key that starts with that prefix and does NOT contain ":thread:". Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0134" near the top of decisions/APPROVALS.md tail; if not, stop and tell the CEO). Scratch copy `~/work35`. Return `~/handover/handover35.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml), `~/handover/REPORT-35.md`, `~/handover-35.tar.gz` with ONLY those and ~/handover/h35/ (move old files in ~/handover aside, do not delete).

## How to talk to the CEO
One step at a time; say which machine; exact text. Never ask for a secret; never print a token or the gateway token.

## IMPORTANT: real data
The CEO's real entries are in the CLO, CFO, CHO and CoS state files and the TEST calendar; the repo is public. Never copy or print their content. Counts and yes/no only. No reset, no re-seed, no regression suite. This handover needs no agent message at all.

## Hard limits
1. Allowed live changes, only these: (a) the pull; (b) the installed coo-compact.sh replaced with the repo copy (find the installed path from the crontab line for coo-compact; print only that one line; back up first as <name>.pre-h35; sha256 equal to the repo copy afterwards). Nothing else: no crontab edit, no config, no plugin, no agent file, no gateway stop or restart (the script is read at run time by cron).
2. No secrets, Slack IDs, session IDs or thread timestamps, tokens, VM address or account names in ~/handover or the repo. In any log line you quote, replace the thread key with agent:coo:slack:channel:<id>:thread:<ts>. Straight quotes only. Cited APR numbers must exist (APR-0134 does).
3. TIME WINDOW: no compaction run by you inside 03:30 to 05:10 AST; you never run it with --execute (the 05:25 cron does that). A dry run (no option) is allowed outside that window.
4. End state: crontab equal to its starting copy; the gateway untouched (same PID before and after); all agent files, config and plugin hashes equal to their start copies; health check PASS with WARN at most the compaction WARN until the next 05:25 run, FAIL 0.

## Part 1. Repo and scratch
In ~/work35: edit scripts/ops/coo-compact.sh so the python parse keeps rows whose key starts with "agent:coo:slack:channel:" and does not contain ":thread:". Change nothing else (window, 10-minute skip, waiting-request skip, log format). Update the header comment (one line: thread sessions are ignored, APR-0134). In tests/unit/test_coo_compact.py add: (1) channel session plus a thread session (key = the test channel key + ":thread:1.2", other numbers anything) -> the channel session is compacted, the compact call names only the channel key, exit 0; (2) a thread session alone -> exit 3 error "found: 0"; (3) keep the existing "two channel sessions is an error" test. Synthetic session lists only. Strict unit suite `python -X dev -W error -m unittest discover -p "test_*.py"` and the validator must pass.

## Part 2. Live
Install the script as in rule 1(b). Then a DRY RUN on the real sessions (outside 03:30 to 05:10): it must say would-compact or skipped, NOT "error ... found: 2". Quote the log line with the thread key masked. Dry-run log lines go to the normal log; that is expected.

## Part 3. Proof (needs the next morning)
After the next 05:25 AST cron run (read after 05:40 AST, not earlier), read the last lines of ~/loop1/state/coo-compact.log and report: result (compacted, no-compaction-needed or skipped is fine; error is a FAIL), size before and after. Run the health check: the compaction WARN should be gone. If you are asked before that time, say Part 3 is waiting for 05:25 and report Parts 1 and 2 now.

## Rollback (in the report, exact commands)
Copy ~/...coo-compact.sh.pre-h35 back over the installed script (print the path in the report); revert the repo patch.

## Report (REPORT-35.md)
Per part: done, files, raw evidence in ~/handover/h35/ (script diff, the new tests' output, strict suite tail, validator tail, sha256 equal, dry-run line with the key masked, crontab diff empty, gateway PID before and after, health check). Part 3 status stated plainly. A statement that no token, ID, session key or real item is in the package. Secrets scan before packaging. `tar czf ~/handover-35.tar.gz -C ~ handover`.
