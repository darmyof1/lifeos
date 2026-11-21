# Handover 39 to Claude Code on the LifeOS VM (health check ignores the COO's tools-policy log line; one repeat test; read-only look at ~/lifeos-ro/0)

Same Claude Code as handovers 1 to 38. The CEO chose option A (APR-0138, deploy/after-loop7/health-coo-warn-approved.md). Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0138" near the end of decisions/APPROVALS.md and ops/handover-2026-11-21-claude-code-report-38.md present; if not, stop and tell the CEO). Scratch copy `~/work39`. Return `~/handover/handover39.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml), `~/handover/REPORT-39.md`, `~/handover-39.tar.gz` with ONLY those and ~/handover/h39/ (move old files in ~/handover aside, do not delete).

## How to talk to the CEO
One step at a time; say which machine; exact text. Never ask for a secret; never print a token.

## IMPORTANT: real data
Real entries are in the CLO, CFO, CHO and CoS files and the TEST calendar; the repo is public. Never copy, print or quote their content or the live send-log lines. No reset, no re-seed, no regression suite.

## Hard limits
1. Allowed live changes, only these: (a) the pull; (b) the installed health-check.py replaced with the repo copy (backup first as health-check.py.pre-h39, sha256 equal). Nothing else: no config, no agent file, no plugin file, no crontab, no gateway stop or restart, no file deleted (the stray file is looked at, not deleted).
2. No secrets, Slack IDs, tokens, session IDs, calendar ID, WirePusher ID, VM address or account names in ~/handover or the repo. Straight quotes only. Cited APR numbers must exist (APR-0138 does).
3. TIME WINDOW: no agent message between 03:30 and 05:10 AST or across the 05:25 to 05:40 compaction. Cost under 0.05 USD per run; record the cost or token figure per run this time if the CLI reports it, else say so.
4. End state: gateway PID unchanged (no restart), crontab, config, all agent files and plugin hashes equal to their starting copies; no journal line or calendar event changed beyond what Part 3 adds (it adds none: a question only).

## Part 1. Repo and scratch
In ~work39: change deploy/loop1/health-check.py so the rule "tools policy: profile" (the one that turns the gateway log line "tools policy: profile ... Add alsoAllow ..." into WARN, 2026-10-22 incident) skips lines that name "agent coo" and still counts lines for every other agent. Change nothing else in the health check; keep the version lines and the COO "read-only, own workspace" line as they are. Tests (tests/unit/test_health_check_loop7.py or the file that tests this rule): a COO line gives no WARN; a CFO line (also CHO, CoS, CLO, solo) still gives WARN; a mixed log (COO and CFO lines) warns and names only the other agent. Strict suite `python -X dev -W error -m unittest discover -p "test_*.py"` and the validator must pass.

## Part 2. Live
Install the repo health-check.py (backup, sha256 equal). Run the health check against ~/lifeos-ro (after the pull) and report PASS, WARN and FAIL counts. Expected: PASS 89 (or the new count), WARN 0, FAIL 0, parity equal for coo/AGENTS.md. If a WARN remains, say which and why; do not hide it. Also report whether the log WARN would still fire for a non-COO agent: show it by the unit tests.

## Part 3. Repeat test and a read-only look
1. The nothing-exists case, repeated with a topic that does not exist: in a fresh explicit session (loop39-...), send the COO the bare message "What did I last tell the CFO about my boat insurance?". Expected: it says plainly nothing was found, invents nothing, no path or file name. First confirm by grep -ci only (no content shown) that the CFO state files do not contain "boat" or "insurance"; if they do, pick another invented topic ("my yacht club fees") and check again. If the answer contains anything that looks real, do not copy it: report "raw not copied: real data" and a yes/no verdict. Cost or tokens per run if shown.
2. The stray file ~/lifeos-ro/0: report ONLY its size in bytes, whether git lists it as untracked or tracked (git status --short, name only), its modification time, and whether it is a regular file (file command output without contents). Do NOT print or copy its content, and do NOT delete it. If it is empty (0 bytes) and untracked, say so; the CEO decides.

## Rollback (in the report)
cp ~/loop1/health-check.py.pre-h39 ~/loop1/health-check.py; revert the repo patch.

## Report (REPORT-39.md)
Per part: done, files, results with raw evidence in ~/handover/h39/ (test output, strict suite tail, validator tail, sha256 equal, health check output, the repeat test reply, hashes and process before and after, the stray-file facts). A plain statement that no token, Slack ID, live log line or real item is in the package. Secrets scan before packaging. `tar czf ~/handover-39.tar.gz -C ~ handover`.
