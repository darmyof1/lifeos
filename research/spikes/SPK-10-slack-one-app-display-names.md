# SPK-10 - One Slack app, one display name per agent

Status: planned
Question: can one Slack app post under each agent's own display name and icon, so that APR-0048 holds?
Approval basis: APR-0053. Pending item: P-27.

## Background
OpenClaw's Slack docs (channels/slack, manifest and scopes) say the chat:write.customize scope lets outgoing messages use the active agent's custom username and icon. Slack expects emoji icons in :emoji_name: form. The config keys for an agent's name and icon are not given on that page.

## Steps
1. Find the identity keys: run openclaw config schema and search for identity, name, emoji and avatar under agents.entries.
2. One Slack app with chat:write.customize added. Two test agents with different names and emoji icons, each bound to its own channel.
3. Mention the front-door agent. It hands off to the second agent with sessions_send. The second agent posts in its own channel.
4. Check Slack: each post shows its own agent's name and icon. Check the gateway log for the account used.

## Pass and fail
- Pass: both names and icons are correct, from one app, on two runs in a row.
- Fail: one app per agent (the SPK-04 shape), and a new APR entry changes APR-0048.

## Results
Not run yet.
