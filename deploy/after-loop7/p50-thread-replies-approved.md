# P-50 item 2: replies inside a Slack thread without an @mention (intent APPROVED by the CEO, APR-0139, option A; the config change itself still needs its own APR)

What you saw (2026-11-17): in a thread you started in an agent's channel, the COO answered only when you typed @COO again. You asked for thread replies without a mention.

What we know so far (from handover 33, read-only; not yet verified for all five agents):
- Every agent answers in Slack only when it is mentioned (the mention rule of APR-0063, in guides/slack-new-agent-app.md).
- OpenClaw has settings for implicit mentions (a reply to the bot and thread participation) and a setting requireMentionInBotThreads. Claude Code reported that requireMentionInBotThreads false only helps threads the bot started, not threads you started.
- We do not yet know the exact keys, their defaults and their live values for the five Slack accounts, nor whether a thread you start can be made mention-free after the bot has replied in it. Slack cannot be tested in the scratch gateway (no Slack there), so any test is live, with you present, and every change has a rollback.

## What you decide now (intent)
- Option A (recommended): thread follow-ups only. Once an agent has replied in a thread, your next messages in that thread need no @mention. A new top-level message in a channel still needs the @mention, so an offhand message cannot start a run (and cost) by accident. Applies to all five agents so they behave the same.
- Option B: no mention needed anywhere in an agent's own channel. Every message you type there starts a run. Simplest to use, but a message meant for yourself, or one typed in the wrong channel, also starts a run, and the privacy gate is still only watching.
- Option C: leave it as is.

## How it would be done (the same path as P-51)
1. Handover 40, read-only, no change: Claude Code reads the Slack channel docs and the live config values (key names and true or false only, no tokens or IDs) for the five accounts and reports: which keys control thread follow-ups, their current values and defaults, what each option would change, and whether option A can be reached by config alone. It also reports what an unmentioned thread message does today (from the gateway log, counts only).
2. I draft the exact config change and the tests from that report, with the rollback, for your approval as its own APR (the change replaces the mention rule of APR-0063 for threads).
3. A numbered handover applies it with you present: config change, one gateway restart outside 03:30 to 05:10 AST, then a live check in a synthetic thread (you type a harmless message in a thread without a mention and see whether the agent answers), then the same in another agent's channel, and a check that a top-level message without a mention is still ignored (option A).

## Risks
- A mention-free thread can start a run from a stray message: cost about 0.003 USD per run, so small.
- The change touches Slack config for all five agents and needs a gateway restart: the rollback is restoring the backed-up config.
- The setting may not exist for threads you start; then option A is not reachable by config alone, and we would report that and stop, with no change.

## Answer (APR-0139)
The CEO chose option A: "P-50: A".
