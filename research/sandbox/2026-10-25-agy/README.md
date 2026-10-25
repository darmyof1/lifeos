# Sandbox session 2026-10-25 (agy)

What this is: drafts written overnight by a Gemini agent (agy) in a fenced sandbox on the VM. It had no access to secrets, did not run the gateway or any agent, and could not push. Its instructions are TASK.md and TASK2.md in this folder.

Status: research input. Nothing here is a decision. SD-001 to SD-010 are the agent's proposals, not APR entries. Decisions live in decisions/APPROVALS.md.

## CEO answers (2026-10-25)
| Item | Answer |
|---|---|
| SD-001, P-37 | Keep open until checked on a real Loop 2 run |
| SD-002, cost kill switch | Ignore for now |
| SD-003, calendar driver | Question to Claude; not decided (gcalcli is the working tool) |
| SD-004, journal archive | Yes (APR-0072) |
| SD-005, embeddings | Later, after the local model work |
| SD-006, state grounding | Needs a token estimate |
| SD-007, short COO handoffs | Needs explaining |
| SD-008, Slack files:read | Defer |
| SD-009, Loop 2 order | Under review |
| SD-010, Loop 2 start | Cloud-only on synthetic data; APR entry pending |

## Corrections from Claude's review
- P-31-cost-hard-stop.md treats 1 USD per day as a kill switch. APR-0056 sets a provider alert at 1 USD per day; only the 0.05 USD run ceiling stops a run. APR-0056 is also titled "Loop 1 cost limits".
- SUMMARY.md says cloud embeddings and dreaming stay off "permanently". APR-0061 applies to Loop 1 and is changeable.
- P-37: the retry claim comes from reading the OpenClaw 2026.10.5 code. The gateway logs for 2026-10-24 and 2026-10-25 contain no "maintenance paused" line, which supports it. It is not yet checked on a Loop 2 run.
- The sandbox health check run (5 PASS, 3 WARN, 27 FAIL) is expected there: the sandbox has no OpenClaw and no Loop 1 files. The same file reported 41 PASS on the VM (VM agent's report, 2026-10-25).

## Not included
- branch-changes.patch: a full diff that repeats these files.
