# SPK-04-slack-multi-identity - Can one OpenClaw Gateway give two agents two Slack identities?

Status: partial (Part A done; Part B not run; leakage check limited)
Decision unblocked: per-agent Slack identity design (follow-up to ADR-0002 and P-09)
Owner: CEO
Date run: 2026-10-18 to 2026-10-19

## Question
Can one Gateway with two Slack accounts let agent spk04-b post as spk04-b and agent main post as spk04-a, with each message showing its own bot identity?

## Pass criterion (Part A)
- Two Slack apps, each created From a manifest, each showing the APP badge.
- Two Slack accounts in one Gateway, both connected in socket mode.
- Each agent posts with an agent turn, and the Slack message shows the identity of the account bound to that agent.

## Environment
- OpenClaw 2026.10.5 (1b58cb9). Test state folder ~/spk04 (OPENCLAW_STATE_DIR). Gateway on port 19001.
- Default system service openclaw-gateway.service stays on port 18789 and was not touched.
- Hosted model: openai/gpt-6-luna configured. The log shows the request was served as gpt-5.6-luna. Usage on the OpenAI dashboard showed $0 for Oct 19 (rounded; cost not confirmed).
- Local model: not used for Part A (see guides/local-model-setup.md).

## Results
- Step 1 PASS: two apps created From a manifest. Posts show the APP badge (not AGENT).
- Step 2 PASS: channels status --probe: Slack default and Slack spk04-b both enabled, configured, running, connected, works.
- Step 3 PASS: agents add spk04-b, bind main to slack:default, bind spk04-b to slack:spk04-b. agents list --bindings shows the bindings.
- Step 4 PASS (run 1): agent spk04-b sent "spk04-b identity test 1" to the test channel. Slack showed spk04-b APP. Turn returned DONE in 14.7 s.
- Step 5 PASS (run 2): agent main sent "spk04-a identity test 1". Slack showed spk04-a APP. Turn returned DONE in 22.1 s.
- Aborted attempt: one spk04-b run was sent with the placeholder channel text and cancelled before any model call. Nothing was posted from it.

## Leakage check (limited)
- The stored session transcript records the send's accountId as [Truncated], so the account argument cannot be read back from it.
- The Gateway log does not record the outbound account for a successful send.
- What is shown: each agent's message carried the Slack identity of its bound account, and neither run named an account in a visible argument.
- Not shown: a test in which an unbound or mis-bound send would be caught.

## Findings
1. Use "From a manifest". The AI agent template gives an AGENT identity, not an APP.
2. Config set, config patch and config unset require the Gateway to be stopped (docs). agents add --bind also requires it.
3. A second account's secret reference failed until a full Gateway restart; an in-process reload keeps the old environment.
4. A top-level channels.slack botToken or appToken is ignored when accounts exist (SECRETS_REF_IGNORED_INACTIVE_SURFACE).
5. gateway.mode must be local, or the Gateway refuses to start.
6. The default system gateway holds port 18789. The test Gateway needs its own port (19001).
7. The Gateway generates a runtime auth token on every start when none is saved.
8. tools.profile messaging was enough for both agents to send. The docs do not list the message tool under that profile; the runs confirm it.

## Conclusion
- Part A: two identities work through one Gateway, and each agent posts as its bound account in both runs.
- Leakage: supported by the binding and the Slack display names, not by a recorded account argument.
- Part B (local model posting): not run. Local model turns did not complete on this VM (SPK-03).

## Next
- Remove the top-level botToken and appToken from channels.slack, then confirm there are no SECRETS_REF warnings. Not yet tested: the accounts-only shape.
- Persist a gateway auth token.
- Find a way to read the account argument of a send, or design a test that would fail if an agent used the wrong account.
- Confirm the served model and the cost on the OpenAI dashboard.
- Plan the kernel reboot (6.17 running, 7.0 expected): a reboot restarts the default service and stops the test Gateway.

## Redaction log
- Tokens, API keys, workspace channel ID, VM address and paths outside the test folder omitted. No secret values recorded.

## Update 2026-10-19: cleanup verified
- Top-level Slack tokens removed. Accounts-only config connects both Slack accounts.
- Gateway auth token saved. No auth-token warning at the spk04 start.
- Direct send from spk04-b posted as spk04-b APP.
- Restart lessons: state variables per terminal; a gateway stop without them stopped the default service; a second gateway run on the same state caused a 40-second stall and a Slack socket error.
- Still open: Part B (local model posting), the leakage check (account argument not in the stored transcript), the served model vs config (gpt-5.6-luna vs gpt-6-luna), and the cost.

## Update 2026-10-19: model verified
- Utility model was unset; OpenClaw used the provider default gpt-5.6-luna for side calls. Set explicitly to openai/gpt-6-luna.
- After the change, the test turn was served as gpt-6-luna (gateway log) and no gpt-5.6-luna request appeared.
- Billing on the life-os project (7-day range): gpt-6-luna only. Re-check tomorrow.
- Prices confirmed on OpenAI model pages: gpt-6-luna is the cheaper model.

## Update 2026-10-20: binding, channel allowlist, owner test; Part B paused
- spk04-b binding verified by a mention: session key agent:spk04-b, reply from the spk04-b app.
- Required in Slack: event subscription app_mention and scope app_mentions:read (the manifest did not include them).
- Required in config: channels.slack.accounts.spk04-b.channels.<CHANNEL_ID>.enabled true.
- /new refused as control-command-unauthorized. commands.ownerAllowFrom with the plain and the slack-prefixed user ID did not authorize it.
- A thread turn was served by openai/gpt-6-luna, not by the per-agent ollama model. Not explained.
- Part B paused. See the guide, section Open items after 2026-10-20.

## Update 2026-10-20: billing re-check
- Life-os chip set, 1-day view: gpt-6-luna about $0.04 (cache writes, cached input, input, output); gpt-5_6-luna $0 on every line.
- Personal October total $1.17 to $1.21, matching the gpt-6-luna increase.
