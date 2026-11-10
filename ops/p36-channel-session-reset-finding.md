# P-36: why the CHO, CoS and CFO channel sessions never show the daily reset - finding (Loop 7, handover 29, APR-0126)

Follows ops/session-reset-options.md (option C). Scratch only; nothing live was changed.

## Test
One scratch gateway (own state folder and port, no Slack, no cron), the live `session` and `tools` blocks with atHour 15 (boundary 15:00 AST, outside 03:30 to 05:10). One message to each session at 14:29 to 14:31, one more after the boundary at 15:01, by the route named:
| route | key | before | after | reset marker |
|---|---|---|---|---|
| `openclaw agent --session-key` | main-style (p1) | 1bd38e7b | 008b68b6 NEW ID | no |
| `openclaw agent --session-key` | channel-style (q1) | a262d543 | 69e14e9d NEW ID | no |
| `sessions_send` from agent r | main-style (p2) | 7b8857bb | 24c5670f NEW ID | no |
| `sessions_send` from agent r | channel-style (q2, created first by a direct message because sessions_send needs an existing session) | 5122d0be | 8b66caaa NEW ID | no |
| gateway `chat.send` (stand-in for a real inbound message, channel-style key, q3) | channel-style | edab78dc | edab78dc SAME ID, start time moved to 15:01 | yes, one "reset" event, reason daily |

## What it shows
1. The daily reset works on every route, for main-style and channel-style keys. The hypothesis in handover 29 (the agent-to-agent path skips the stale check) is NOT confirmed: `sessions_send` reset the session too.
2. The route matters for HOW it resets. An inbound-style message resets in place: same session ID, new start time, a "reset" marker. This is exactly what the live CHO, CoS and CFO channel sessions show for 10-29. The other routes open a new session window with a new ID and no marker.
3. Live data (read-only database copies, counts only, no text; `h29/reset-test/live-channel-event-kinds.txt`): the CHO, CoS and CFO channel sessions hold only 2 user-role messages each, both on 10-29 (the real Slack messages at 20:12 to 20:19, which caused the one reset). Before 10-29 they held 152 / 235 / 20 assistant messages and no user message; after 10-29 the CHO and CoS added 31 and 66 assistant messages and no user message; the CFO added nothing. So since 10-23 these sessions were never reached by a message that goes through the inbound check, except on 10-29 evening, and that one reset them.
4. Therefore the missing daily reset is explained by the traffic, not by the setting: nothing real has arrived by the inbound route since 10-29, and whatever route produced the later assistant messages (not any of the three tested: they would have produced new session IDs) does not run the check.
5. Not known: which route wrote those assistant-only events. Not tested: a real Slack message, and the exact value 4.

## Consequence for option B
The compaction job (a morning job like the COO's for the CHO, CoS and CFO) is still the only way to keep those sessions small without a CEO message. The cause was not confirmed as handover 29 required, so nothing was built or installed live. The prepared script (agent-compact.sh, wrapper, tests, health lines) exists, tested in scratch (23 compaction tests pass), but is not in this patch. A new handover can install it on the CEO's word.
