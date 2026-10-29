# COO reply line with the event ID (APR-0103 follow-up). DRAFT. Not applied. The CEO approves the wording first (a new APR).

Nothing in this file has been installed. No agent file, config, cron or gateway was touched. No upgrade script was written.

## What it changes
The seven-item approval request ends with a Reply item. Today it says "approve, explain more, or keep". The push job now needs the CEO's message to carry the event ID and an approve word (design.md section 4), so the COO must put the event ID into that line.

New last item, exact text for a delete request:

`Reply: approve <event ID>, explain more, or keep`

with the real event ID in place of `<event ID>` (for example `Reply: approve loop2-scn-021-cho-01, explain more, or keep`).

## The existing COO rules it changes (quoted from agent-files/executive/coo/AGENTS.md, current set v1.10.3)
- v1.10 (APR-0092), line 41: "...post one message with these lines: What. Used for. Why now. Risk if approved. Risk if not. Recommendation. Reply: approve, explain more, or keep. When the CEO approves a delete, pass it to the CoS with his words quoted and the event ID..." The words "Reply: approve, explain more, or keep" are the ones replaced, for deletes.
- v1.10.1 (APR-0093), line 42: "...quote the CEO's exact words and give the event ID from the journal entry... Never write approving or approved in your message unless the CEO's own words say so. When you post an approval request, put each item on its own line, in this order: What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply." Unchanged. The new Reply item contains "approve" only as the instruction to the CEO, not "approving" or "approved", so this rule still holds.
- v1.10.3 (APR-0095), line 43: "...always post the seven items, each on its own line: What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply. A plain sentence is not enough." Unchanged. The Reply item stays the seventh and last.

Approval requests that are not deletes (a time two chiefs both need) keep the old Reply wording; the rule below is limited to deletes.

## Next instruction-set version
v1.10.4 (COO only). The other three agents stay as they are (cos v1.10.2, cho v1.9, cfo v1.10).

## Text to append (one line to the end of the COO's AGENTS.md, same style as loop1-v1103-upgrade.sh)
In that script's style, the variable and the single-quoted line would be:

```
COO_REPLY='- Delete reply line (APR-0103, instruction set v1.10.4): in every delete approval request, make the last item exactly "Reply: approve <event ID>, explain more, or keep", with the real event ID from the journal entry in place of <event ID>. This replaces the Reply wording of v1.10 for deletes. Add one short sentence after the seven items telling the CEO to type approve and the event ID, for example approve <event ID>, and that a bare approve will not delete. When the CEO writes approve and the event ID, pass it to the CoS with his words quoted and the event ID, as before. If the CEO writes approve without an event ID, do not pass it as an approval: ask once for approve and the event ID. Never write the event ID of a different request.'
```

An upgrade script written later would follow loop1-v1103-upgrade.sh: refuse unless the COO file has "instruction set v1.10.3", skip if it already has "instruction set v1.10.4", require the gateway stopped (not in --dry-run), append the line, commit AGENTS.md only with the message "Loop 1 instructions v1.10.4 (APR-0103)", and leave state/ and the OpenClaw config alone. It is not written here.

## What the CEO should type
Exactly: `approve <event ID>`, with the ID copied from the COO's Reply line (for example `approve loop2-scn-021-cho-01`), in any channel the bot reads. One message, no other words needed.
- A bare `approve` will not delete. The plugin records it as an approval word with no event ID and the job finds no match, so the delete waits and the COO asks again.
- Words that make the plugin record "not approving": not, no, never, cannot, without, cancel, stop, keep, explain, dont/don't, cant/can't, wont/won't, wait, hold off. Do not paste the COO's whole Reply line back: it contains "explain" and "keep" and counts as not approving.
- "Yes, I approve" without the ID, "approval", "disapprove": do not delete.
- If a message is judged not approving, nothing is lost: write it again as `approve <event ID>`.

## Open points for the CEO
1. Whether the COO asks again after a bare approve (as drafted), or only waits.
2. Whether the added short sentence for the CEO is wanted, or the Reply line alone.
3. The exact wording above; any change needs a new APR before a script is written.
