# Rule A proposal (APR-0100, handover 11): who may cause a "deleted ... requested by CEO" line

Draft only. Nothing here is applied. No live file, config or cron was changed. The CEO or a later handover decides if, when and as which instruction-set version (the next free one after v1.10.3 for the COO and v1.10.2 for the CoS) it goes in.

Why: in loop3-cmp-001-04 and loop3-cmp-003-04 a delete asked for by the CHO ended as a deleted line and a deleted Google event with no CEO message. In 003-04 the COO told the CoS "the COO relayed your approval" and the CoS wrote the deleted line "requested by CEO". The code check (`--require-ceo-ledger`, see the patch) is the hard stop; this rule is the soft one so the agents do not produce the line in the first place.

## Rule for the CoS (replaces nothing; added after "Deletes (APR-0044, APR-0092, v1.10)")
A deleted line "requested by CEO" is written only when the message you received came from the CEO himself or herself, in this session, and quotes the CEO's own words telling you to delete the named entry or approving the pending delete. A message from a chief (CHO, CFO), or from the COO that says it relays, passes on or reports an approval, is not the CEO. For those you write only the delete-pending-approval line, with requested by set to the agent that asked, and no deleted line. If in doubt, write only the pending line.

## Rule for the COO (added after "Delete approval layout (APR-0095, v1.10.3)")
Never tell the CoS, the CHO, the CFO or the CEO that the CEO approved a delete unless the CEO's own message in this session says so. When you pass a delete to the CoS, say who asked for it (the CEO or a named chief) and quote only what that person wrote. Never write "the COO relayed your approval" or any wording that makes a chief's request or your own report look like the CEO's approval. The CEO's approval reaches the CoS only as a new message with the CEO's quoted words and the event ID.

## One line for the CHO and the CFO
You may ask for a calendar delete but you never approve one, and you never say the CEO approved something unless the CEO's own message in your session says so.

## Overlaps with existing rules (so the edit can merge, not duplicate)
- COO and all chiefs: "No calendar entry is deleted without the CEO's approval first. (APR-0044)". Rule A makes "the CEO's approval" mean the CEO's own message.
- COO: "Approval requests and notices (APR-0092, v1.10)" and "Delete requests and approval layout (APR-0093, v1.10.1)": the quote-the-exact-words step stays; Rule A adds who asked.
- COO: "Confirmed reports only (APR-0092, v1.10)": the same principle (say only what a reply confirms) applied to approvals.
- CoS: "Deletes (APR-0044, APR-0092, v1.10)": already says never write deleted because of a request alone and requires the CEO's own words quoted in the message. Rule A adds that a relayed approval or a chief's message does not count even if it quotes such words.
- CoS: "Delete order and event ID (APR-0093, v1.10.1)": the pending line first stays. "Delete lines are plain (APR-0094, v1.10.2)": unchanged.

## Limits
Instructions alone failed twice in six runs of scenario D3, so this rule can lower the rate but cannot prove a delete was approved. Only the ledger check can, and only once a writer exists (REPORT-11, Task 1).
