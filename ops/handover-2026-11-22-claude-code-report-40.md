# REPORT 40 (APR-0139): Slack mention and thread settings, read-only (P-50 item 2, step 1)

Pull ok (APR-0139 present). Nothing live changed: gateway PID, config, agent files, plugin files and crontab hashes are equal before and after (`h40/gw-pid-*.txt`, `hashes-*.txt`). Patch is empty.

## Short answer
1. Option A is reachable by configuration alone, and is very likely ALREADY the live behavior: all five agents run on defaults, and the defaults let a thread reply skip the @mention once the bot has replied in that thread. Nothing to change unless the live check below fails.
2. The one unknown is whether the Slack apps are subscribed to the channel message events (`message.channels` or `message.groups`). If they are only subscribed to `app_mention`, an unmentioned thread reply never reaches the gateway at all. This cannot be read without a token, so it is not known.

## Part 1: documentation (OpenClaw 2026.10.5 docs, `h40/doc-*.txt`)
Settings (docs/channels/slack/access-control.md, threads-and-sessions.md, gateway/config-channels/shared-policies.md, channels/groups.md):
- `requireMention`: per channel (`channels.slack.channels.<id>`), also account level default. Default true: "Channel messages are mention-gated by default." Top-level channel messages need a mention. Not applied to DMs.
- `implicitMentions.replyToBot`: scope `channels.defaults`, `channels.slack`, or `channels.slack.accounts.<id>`; each flag resolves account, then channel, then defaults. Default true. "controls whether a reply to the bot's own message bypasses mention gating".
- `implicitMentions.threadParticipation`: same scopes, default true. "controls whether follow-ups in a thread where the bot has replied bypass mention gating ... Set it to false to require a new explicit mention."
- `requireMentionInBotThreads`: per channel, "*" entry, account, or root. No default (omitted keeps the implicit behavior). It acts only in threads whose root message the bot sent. "Threads started by other people keep their normal policy."
- Others: `ignoreOtherMentions` (default false; drops channel messages that mention someone else but not the bot; DMs unaffected), `allowBots`, `messages.groupChat.unmentionedInbound` (room_event: unmentioned chatter becomes silent context), mention regex patterns (`groupChat.mentionPatterns`), Slack user-group mentions.

Per case (defaults):
1. Top-level channel message: needs a mention (requireMention true).
2. Thread started by the bot: no mention needed, because the reply is to the bot's message (replyToBot) and the bot has participated; `requireMentionInBotThreads` false would force it, true would require a mention.
3. Thread started by the user in which the bot has already replied: no mention needed (threadParticipation true), as long as the bot's reply was delivered inside that thread (the plugin records participation when a reply is delivered in the thread).
4. Thread started by the user, bot has not replied: needs a mention.
5. DM: no mention gating (DM policy and pairing apply instead).
- Restart: `channels.*` is "Depends on setting and loaded plugin" (docs/gateway/configuration/hot-reload.md). The docs do not say whether `implicitMentions` hot-applies; in hybrid mode (default) the gateway restarts what is needed. Not proven here; treat a restart of the Slack runtime as possible.

## Part 2: live values (`h40/live-values.txt`)
None of requireMention, requireMentionInBotThreads, ignoreOtherMentions, implicitMentions, replyToMode, allowBots, groupPolicy, thread or messages.groupChat is set anywhere in the config (root, five accounts, channel entries, channels.defaults). Each account has only enabled, mode and one channel entry with enabled and users. The five agree: all defaults.

## Part 3: what happens today
The Slack plugin source rejects an unmentioned channel message with the log phrase "Slack inbound event rejected during preparation" (reason missing-mention). Count in the current and previous log files: 0 and 0. Only about 2 days of log exist (/tmp, rotated). A plain unmentioned top-level message was sent on 2026-11-21 and should have produced one, so the gateway log does not record ignored messages at its level. Result: no per-agent counts are possible; absence of lines does not prove nothing was ignored.

## Part 4: findings and options
1. Config alone: yes. Exact explicit keys (a no-op, same as the defaults), per account coo, cho, cos, cfo, clo: `channels.slack.accounts.<id>.implicitMentions = {replyToBot: true, threadParticipation: true}`. Not needed unless a default turns out to differ.
2. Option B (for the record): drop the mention everywhere in the channel with `requireMention: false` per channel. Not chosen; it would make every message in the channel trigger the agent, including top-level ones.
3. Effect: only thread follow-ups after the bot has replied. Top-level channel messages still need a mention; DMs are unchanged; threads where the bot has not replied still need a mention.
4. Restart: unknown (see Part 1c). Plan for one gateway restart only if the change is needed.
5. Validation: scratch config copy with every token replaced by a dummy and no channel bindings, scratch state folder, never started. `openclaw config validate`: proposed config valid (only a warning that the Slack plugin is not installed in the scratch). Control: a made-up key under implicitMentions is rejected, so the key is really checked (`h40/validate-*.txt`). Scratch deleted.
6. Live check (no change needed first): CEO, in Slack in the browser, COO channel: type `@COO ping`, wait for "Here." Then use "Reply in thread" under the COO answer and type `ping again` without @COO. Expected: the COO answers in that thread. If it does, option A already works and the answer is "no change needed". If it does not, either the Slack app lacks the message.channels event (fix in the Slack app settings, not in the VM) or the reply was not in a thread. Repeat for the other four agents if wanted. Rollback of any later change: restore the backed-up config, restart the gateway.
7. Risks and unknowns: Slack event subscriptions (not readable without a token); whether a bot reply made at top level (replyToMode off) counts as thread participation; restart need; a thread reply to a message the bot posted at top level counts as reply-to-bot, so it should work even then. Unmentioned replies will also reach the agent when the CEO means them for someone else, which is the intended trade.

## Package statement
No token, Slack ID, team, channel or user ID, session key or real item is in the package. The config file was read only by a script that printed key names and true/false values.

## Addendum: Slack thread tests after the report (2026-11-22)
Raw: `h40/slack-test-2026-11-22.txt`. Summary: with the Slack app subscribed to message.channels and message.groups, all three test messages (02:09 "hey" top-level, 02:10 @COO, 02:10 thread reply "ping") reached the gateway. The two unmentioned ones were rejected with reason missing-mention, parentUserId absent. The send log has a ceo-message line only for the @COO message. The thread-participation table has 1 entry (2026-11-17) and no new one, so the COO's top-level answer was not counted as a reply inside a thread. The earlier statement that the log does not record ignored messages was only true before the Slack change (the messages never arrived); rejections are now logged.

Answers given to the CEO (config unchanged, nothing restarted for them):
- requireMentionInBotThreads: "overrides mention gating only in threads whose root message was sent by this bot." A bot thread = first message sent by the bot; "Threads started by other people keep their normal policy." It covers a thread under a bot top-level answer (the test case) and does not cover a thread the CEO starts with a message of their own. The plugin decides who started the thread from the parent-author field, or, if absent, by reading the thread first message from Slack history.
- threadParticipation: live value for the COO account is unset, so the default true. It does not use parentUserId; it tracks threads the bot posted in (memory plus stored table). replyToBot does use parentUserId.
- Proposed key: channels.slack.accounts.<id>.requireMentionInBotThreads = false for coo, cho, cos, cfo, clo. Top-level messages still need a mention; DMs unaffected; threads the CEO starts under their own message unchanged. Not read live: the key is outside the plugin list of live-applied settings but under the Slack reload prefix, so the Slack runtime restarts by itself (inferred from the source, not tested). Risk: the history lookup needs Slack history permission (channels:history or groups:history); scopes cannot be checked without a token.
- Scratch validation: `openclaw config validate` passed with the five accounts set to false; a bad value was rejected; scratch deleted.
- Rollback: copy the config to openclaw.json.pre-mentionthreads first; to undo, stop the gateway, restore the copy, start the gateway, confirm 5 of 5 Slack accounts.
- The other four apps still subscribe only to app_mention (the CEO changed only the COO app), so they receive no thread replies until the same Slack change is made.

Side event (outside this handover's read-only scope): on 2026-11-22 the OpenAI key was found expired; the CEO supplied a new one and it was installed with one gateway restart; details in the raw file above. The report statement below still holds: no token, ID, session key or real item is in the package.
