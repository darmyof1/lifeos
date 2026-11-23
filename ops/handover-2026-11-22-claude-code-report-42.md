# REPORT 42 (APR-0143): requireMentionInBotThreads false for the five Slack accounts

Pull ok (APR-0143 present). Patch `handover42.patch`: 5 files, `git apply --check` ok on a fresh clone.

## Result
Live and working for the COO: a reply in the thread under the COO answer, with no mention, was answered. A new top-level message without a mention is still ignored. A thread under the CEO's own message is still ignored (unchanged policy). Health check PASS 93, WARN 0, FAIL 0. The other four apps are not tested yet (their Slack apps need the message events first).

## Part 1: repo
- deploy/after-loop7/bot-thread-mention-patch.py (new): sets channels.slack.accounts.<id>.requireMentionInBotThreads false for default (COO), cho, cos, cfo, clo; compares the whole config key by key and refuses unless the only change is those five additions; prints key paths and false only; backup CONFIG.pre-mentionthreads (never overwritten); --dry-run; second run says "already set".
- deploy/loop7/clo-config-patch.py: a new CLO-style account entry now carries the key (this is the only place the repo builds an account entry; the other four were built before the repo had a template).
- deploy/loop1/health-check.py: one new line "slack bot-thread mention: requireMentionInBotThreads false for 5 of 5 accounts" (reads only the five key values; PASS when all false; WARN when any is unset or true or an account is missing).
- guides/slack-new-agent-app.md: step 7.2 reworded and a new section 8 (message.channels and message.groups with channels:history and groups:history in addition to app_mention, reinstall; the account carries the key; this replaces the APR-0063 mention rule only for threads whose first message the bot sent; top-level messages still need a mention; test and the order of causes if a reply is ignored); one troubleshooting row. Note: the repo manifest guides/slack-app-manifest-clo.json already holds those events and scopes.
- tests/unit/test_bot_thread_mention.py (9 tests): five keys exactly, missing account refused, backup, second run, output holds no IDs, clo patch, health line PASS and WARN cases, guide content. Strict suite 560 OK; validator 0 blocking, 1 usual warning (`h42/strict-suite-tail.txt`, `validator-tail.txt`).
- Scratch: config copy with dummy tokens, no bindings, never started: patch applied (five additions), `openclaw config validate` valid, health line PASS, second run "already" (`h42/scratch-*.txt`); deleted.

## Part 2: live
- Backup `~/loop1/state/openclaw.json.pre-mentionthreads`. Dry run and apply (`live-dryrun.txt`, `live-apply.txt`). Key-path diff against the backup: five additions (coo, cho, cos, cfo, clo), 0 removed, 0 changed (`config-key-diff.txt`). `openclaw config validate`: valid (`live-validate.txt`).
- Gateway stopped, started once: PID 464268 to 489405 (`gw-pid-*.txt`), one process; Slack probe 5 of 5 connected (`slack-probe.txt`).
- Health-check.py installed from the repo copy (backup `health-check.py.pre-h42`, sha256 equal, `sha-equal.txt`). Health check against the patched repo copy: PASS 93, WARN 0, FAIL 0, INFO 6; the new line PASS (`health-after.txt`).
- Hashes before and after (`hashes-*.txt`): only openclaw.json differs; agent files, plugin files equal; crontab equal.

## Part 3: live thread test (`h42/slack-test-2026-11-22-evening.txt`)
1. "@COO ping" top-level: answered; 1 inbound app mention; send log line.
2. "ping again" in the thread, no mention: ACCEPTED (no missing-mention rejection), the COO answered "pong" in the thread, second send-log ceo-message line, 0 history or scope errors. PASS.
3. "ping three" top-level, no mention: 1 missing-mention rejection, no answer. PASS.
4. Thread under the CEO's own message, no mention: the root message and the thread reply were both rejected (missing-mention); no answer. As expected; the limit is recorded.
5. The other four agents: the key is set and all five accounts are connected. Their Slack apps still subscribe only to app_mention, so Slack sends them no unmentioned thread replies; nothing was tested for them.

### Steps for the CEO to enable the other four apps (CHO, CoS, CFO, CLO), one app at a time, in a browser on the Mac
1. api.slack.com/apps, open the app (for example CHO).
2. Event Subscriptions, "Subscribe to bot events": add message.channels (and message.groups if its channel is private). Save changes.
3. OAuth and Permissions, Bot Token Scopes: check channels:history (and groups:history for a private channel) are present. The CLO manifest already has them; add any that are missing.
4. Install App, Reinstall to Workspace (Slack asks for approval).
5. Tell Claude Code which app is done. It checks the Slack probe (5 of 5) and then in that agent's own channel: you type "@AGENT ping", reply in its thread with no mention, and Claude Code reads the log for the same counts. A reinstall can show the account disconnected for about 40 seconds.

## End state (rule 4)
One gateway process (new PID 489405). Crontab equal. Config differs from the start only by the five keys. Agent files and plugin hashes equal. Slack 5 of 5. Health PASS 93, WARN 0, FAIL 0.

## Rollback
systemctl --user stop openclaw-loop1-gateway; cp ~/loop1/state/openclaw.json.pre-mentionthreads ~/loop1/state/openclaw.json; systemctl --user start openclaw-loop1-gateway; confirm 5 of 5 Slack accounts and a single process; cp ~/loop1/health-check.py.pre-h42 ~/loop1/health-check.py; revert the repo patch.

## Package statement
No token, Slack ID, session key or real item is in the package.
