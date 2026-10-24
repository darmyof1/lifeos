# SPK-10 - One Slack app, one display name per agent

Status: done (one app failed; one app per agent passed)
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
Run 2026-10-23 and 2026-10-24 on the Loop 1 VM (OpenClaw 2026.10.5, gateway running).

First shape, one Slack app, identity from the agents' config (name and emoji):
- The identity keys are agents.entries.<id>.identity (name, emoji, theme, avatar); openclaw agents set-identity writes them.
- A reply to a routed message showed the agent's name. The icon showed only after the emoji was written in the :name: form (":compass:"); a raw emoji did not show.
- A post made by an agent with its message tool after a handoff showed the app name. The Slack plugin resolves the agent's identity for replies only.
- Result: FAIL against the pass criterion, which required correct names and icons for both kinds of post.

Second shape, one app per agent (the SPK-04 shape; APR-0062, CEO answer "ok, (a) is approved, proceed"):
- Four apps and four accounts. channels status --probe: four Slack lines ending in works.
- Test 6: mention of the COO in its channel. COO replied under its name and compass icon.
- Test 7: a mention in each of the other three channels. After each account got its own channel in its allowlist, CHO, CoS and CFO each replied in its own channel under its own name and emoji.
- Before the allowlist entries, the CFO answered: "This OpenClaw bot can't reply here because this channel isn't in its OpenClaw channel allowlist." CHO and CoS did not reply. The gateway log showed the inbound event and no reply.
- Test 8 (handoff): the CEO asked the COO to have the CHO post one word in the health channel with its message tool. The CHO posted it from the CHO app, with the CHO name. The icon was the app's own Slack image, not the emoji.
- Not clean: a mention of the CFO in the health channel was stopped by Slack because the CFO app is not a member there. The OpenClaw allowlist refusal was seen only in the CFO's own channel, before its entry was added.

## Findings
1. One app cannot give a handoff post the agent's identity. One app per agent can.
2. A channel needs an allowlist entry under each account that should answer in it.
3. The Slack image of an app shows on message-tool posts. The emoji shows on replies. Set both to match.
4. Open: the CHO, CoS and CFO answer the CEO directly in their channels (P-33).

## Conclusion
APR-0053's fallback is used: one app per agent (APR-0062). The setup steps are in guides/loop1-baseline.md section 7.8.
