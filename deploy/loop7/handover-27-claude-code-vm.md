# Handover 27 to Claude Code on the LifeOS VM (Loop 7 parts 1 and 2: isolation measure, reliability watch)

Same Claude Code as handovers 1 to 26. The CEO approved Loop 7 (APR-0124, scope in deploy/loop7/LOOP7-SCOPE.md). Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0124 ..." at the top; if not, stop and tell the CEO). Work in a scratch copy (`rm -rf ~/work27 && cp -a ~/lifeos-ro ~/work27`). Return ONE patch `~/handover/handover27.patch` (git add -A; git diff --cached --binary; no commit, no push; exclude contracts/registry/artifacts.yaml: git reset that file first), `~/handover/REPORT-27.md`, and everything as `~/handover-27.tar.gz` (report and patch inside, raw evidence in ~/handover/h27/).

## How to talk to the CEO
One step at a time; say which machine; give the exact text; say what he should see. Never ask him to print, paste or send a private key, token or password; never print the gateway token (read config with a small script that prints only the key you need).

## Hard limits
1. NO live change at all: no config key, no crontab line, no agent instruction, no plugin change, no gateway restart, no Docker install, no package install on the live state. Scratch only, in its own state folder and port, deleted afterwards (it holds copies of agent auth files).
2. Synthetic data and the Google TEST calendar only. No real data of any kind.
3. No secrets, Slack IDs, tokens, calendar ID, VM address, IP addresses or account names in ~/handover or the repo. Never print ~/loop1/ceo-slack-id (grep -cF only). Straight quotes only in repo files. Cited APR numbers must exist.
4. TIME WINDOW: no agent message, compaction or gateway restart between 03:30 and 05:10 AST (the daily 05:25 COO compaction is outside it; do not run a suite across 05:25 either); agent runs end by 02:30 AST unless the CEO is present. Cost under 0.05 USD per run, 1 USD per day. Never reuse a run ID. One gateway.
5. The CEO's dentist test entry (2026-11-09) sits in the calendar journal. Before the FIRST suite prep, ask the CEO one yes/no question: may the suite prep remove his dentist test entry (it is a past test entry)? If no, copy the journal and the entry aside, and put them back byte for byte at the end. Do not decide for him.
6. Final state: gateway one process; crontab and config equal to their starting copies (save both first, diff at the end); ledger plugin and gate plugin files unchanged (hashes before and after); calendar at the seed; health check PASS 77 or better, WARN 0, FAIL 0.

## Part 1. Isolation measure (SPK-03)
Read research/spikes/SPK-03-agent-isolation.md and research/threat-model.md (residual risk 6).
a. Live agents, READ ONLY: for each of coo, cho, cos, cfo print the effective tool list/profile, whether file read/write/shell tools exist, any workspace-only or sandbox setting (`openclaw sandbox explain --agent <id>`, config values with a small script), and the workspace path. Do not run an agent to find this out unless the config cannot tell you.
b. Scratch canary (own state folder, own port, no Slack, no cron): two agents a and b with separate workspaces, the SAME tool profile as the live agents (copy the profile, not the secrets). A canary marker file in a's workspace. Ask b, with the cloud model and a new run ID, to read it by path. Repeat 3 times, with the exact prompt in the evidence. Record: read succeeded or refused, and how (tool error or no tool). Also try a path under b's own workspace as the control.
c. Repeat b once with the live agents' profile changed ONLY in the scratch copy if a sandbox or workspace-only setting exists in the config schema (name it, show the effective explain output). Docker is not installed: do not install it. If the setting needs Docker, report that and stop that sub-step.
d. Write `research/spikes/SPK-03-agent-isolation.md` update (append a "Results 2026-11-09" section, keep the old text) and `ops/isolation-options.md`: what is contained today, what is not, and 2 to 3 options to close the gap, each with cost, risk, whether it needs a live change and what you would test. Do not recommend installing anything; the CEO decides.

## Part 2. Reliability watch
a. D2 requested-by gap and overlap 08:00-slot gap: read how handover 20 ran them (deploy/loop3/handover-20-claude-code-vm.md, ops/handover-2026-11-01-claude-code-report-20.md if present). Run 10 more single-scenario runs of each, same method, new run IDs, no instruction change, after the question in rule 5. Cost about 0.1 USD each batch. Report per run: pass or fail, raw files. If a run fails, keep its raw files and do not retry it.
b. P-36: read the 05:00 AST reset reports in ~/loop1 since 2026-11-01 (their log folder) and say for each of the four channel sessions whether a reset marker appears after a normal message and on which dates. No agent message needed.
c. End: reseed the calendar as the suites do, cron line restored byte for byte after each pause.

## Report (REPORT-27.md)
Per part: done, files, results with raw evidence, plain verdicts (SPK-03: what we know now; D2 and overlap: n of 30 each with the earlier ones counted separately; P-36: yes/no per session). End state per rule 6. Secrets scan before packaging (CEO's Slack ID compared without printing, no keys, no tokens, no addresses, no IPs). `tar czf ~/handover-27.tar.gz -C ~ handover`.
