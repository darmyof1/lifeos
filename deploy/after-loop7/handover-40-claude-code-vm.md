# Handover 40 to Claude Code on the LifeOS VM (P-50 item 2, step 1: read-only look at the Slack mention and thread settings)

Same Claude Code as handovers 1 to 39. The CEO chose option A for P-50 item 2 (APR-0139): once an agent has replied in a thread, the CEO's next messages in that thread need no @mention; a new top-level channel message still needs one; all five agents the same. This approval starts step 1 ONLY: find out, read-only, what the settings are and whether option A can be reached by configuration alone. NOTHING live changes in this handover. Pull first: `cd ~/lifeos-ro && git pull -q` (expect "APR-0139" near the end of decisions/APPROVALS.md; if not, stop and tell the CEO). Scratch copy `~/work40`. Return `~/handover/handover40.patch` (empty is fine; git add -A; git diff --cached --binary; no commit, no push), `~/handover/REPORT-40.md`, `~/handover-40.tar.gz` with ONLY those and ~/handover/h40/ (move old files in ~/handover aside, do not delete).

## How to talk to the CEO
One step at a time; say which machine; exact text. Never ask for a secret; never print a token.

## IMPORTANT: secrets and real data
The OpenClaw config holds Slack tokens. NEVER print, cat, grep-with-context or copy the config file or any token, app ID, team ID, channel ID or user ID. Extract only the named keys below with a script that prints key paths and true, false or short enum values, nothing else, and check the output for strings that look like IDs before saving it. Real entries are in the CLO, CFO, CHO and CoS files; do not read them. No agent message is needed for this handover. No reset, no re-seed, no regression suite.

## Hard limits
1. NO live change: no config edit, no restart, no crontab, no plugin, no agent file. The only live actions are the pull and reading the OpenClaw docs, the installed SDK or source files, the config keys named below (values only), and gateway log counts.
2. No secrets, Slack IDs, tokens, session IDs, thread timestamps, VM address or account names in ~/handover or the repo. Straight quotes only. Cited APR numbers must exist (APR-0139 does).
3. End state: gateway PID unchanged, config, crontab, agent files and plugin hashes equal before and after (record hashes before and after).

## Part 1. Documentation
Read the OpenClaw 2026.10.5 Slack channel docs (and the config reference they link) and report, with file names and short quotes (a few lines each, no IDs):
a. Every setting that decides whether the bot needs an @mention: requireMention (per account and per channel), implicitMentions (replyToBot, threadParticipation), requireMentionInBotThreads, and any other you find (for example an ack or "always" mode, or a per-channel override).
b. For each: scope (global, per Slack account, per channel), default value, and exactly what it does for (1) a top-level message in a channel, (2) a thread started by the bot, (3) a thread started by the user in which the bot has already replied, (4) a thread started by the user in which the bot has not replied, (5) a direct message.
c. Whether a setting change needs a gateway restart or is read live.

## Part 2. Live values (values only)
For each of the five Slack accounts (report them as coo, cho, cos, cfo, clo, never by account or channel ID), print with a script ONLY: the values of the keys found in Part 1 (path and true, false or enum). Report whether the five agree. Do not print any other key.

## Part 3. What happens today (counts only)
From the gateway log of the last 7 days (the file is the current log; if it was rotated, say so): count, per agent, Slack messages in threads that the gateway ignored because there was no mention, if the log records that reason (name the log phrase you counted, no message text or IDs). If the log does not record ignored messages, say so.

## Part 4. Findings and options (no change)
One page: (1) can option A be reached by configuration alone: yes or no, with the exact keys and values per account; (2) what option B would be (for the record); (3) does the change affect DMs or top-level channel messages: say exactly what changes and what does not; (4) restart needed or not; (5) validate the proposed config in a scratch copy of the config with all tokens removed or replaced by dummies, in a scratch state folder, with `openclaw config validate` or the nearest equivalent, and show only the verdict (a scratch copy must not be started with real tokens; delete it afterwards); (6) the live check that would be needed (what the CEO types, where, and what he should see) and the rollback (restore the backed-up config); (7) risks, and what is not yet known. If option A is not reachable, say so plainly.

## Report (REPORT-40.md)
Per part: done, files, raw evidence in ~/handover/h40/ (doc quotes, key values table, counts, validate verdict, hashes before and after, process counts). A plain statement that no token, ID, session key or real item is in the package. Secrets scan before packaging. `tar czf ~/handover-40.tar.gz -C ~ handover`.
