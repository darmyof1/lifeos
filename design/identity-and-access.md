# Identity and access

Status: accepted by the CEO (APR-0113); written 2026-11-01 under APR-0112. Machine-checked copy: contracts/identity-access.yaml (tests/unit/test_identity_access.py checks it against the send lists in the health check, the agent instruction text, the plugin and the push job). The blocker named in the old stub (P-04) was answered by APR-0023, so it is gone. Changeable: yes; a change is a new approval.

## Who is who
| Identity | What it is | How it proves who it is (mechanism only) |
|---|---|---|
| CEO | The person | Own Slack user account; password manager |
| COO, CHO, CoS, CFO | The four agents | One Slack bot token per agent (the COO uses the default account), the gateway token, the OpenClaw agent entry |
| Sync job | Cron job that pushes the journal to the Google TEST calendar | The Google OAuth client file on the VM; runs as user ubuntu |
| CEO ledger plugin | Hook-only plugin inside the gateway | Runs in the gateway process; reads the CEO's Slack user ID from a file |
| Claude Code on the VM | The operator who builds and tests under a handover | SSH session as user ubuntu |
| Repo owner | The CEO pushing the repo | GitHub account and git credentials on the CEO's machine |

## What each may do
| Identity | Read | Write | Send to | Approve |
|---|---|---|---|---|
| CEO | Slack channels, reports, repo | Slack messages (with an @mention of the bot), approvals | all four agents | deletes, privacy override, instruction changes, installs |
| COO | its workspace | its own state files | CHO, CoS, CFO | nothing |
| CHO | its workspace | its own state files | COO, CoS | nothing |
| CoS | its workspace | the calendar journal (only the CoS), its state files | COO, CHO | nothing |
| CFO | its workspace | its own state files | COO, CoS | nothing |
| Sync job | journal, ledgers, its state folder | the Google TEST calendar (only the job), its state folder, sync.log | nobody | nothing |
| CEO ledger plugin | the inbound Slack message event, the CEO ID file | the Slack ledger (append only) | nobody | nothing |
| Claude Code on the VM | repo clone (read-only), VM state as the handover allows | the handover folder, scratch copies, files the handover names | nobody | nothing |
| Repo owner | repo | repo | nobody | merge and push |
Note on the CFO (a known difference, recorded in the contract; nothing is changed until the CEO decides): the CFO instruction text lists only the COO under "You may send to"; the OpenClaw config also allows the CoS (set on 2026-10-26, ops/cfo-send-list-diff-2026-10-26.txt). The test requires that the text never lists more than the contract.

## The rules that matter most
1. **Delete.** Only the CEO approves. A delete needs a pending line in the journal, then a CEO approval in the ledger, and the push job runs with `--require-ceo-ledger` for both ledgers (the cron line carries it; the health check fails if it does not). A plain "approve" counts only when exactly one delete is waiting (APR-0110); otherwise the CEO writes "approve" and the event ID. An approval is valid for 48 hours and counts once (its message ID is used up).
2. **Calendar writes.** Google: only the sync job. The journal: only the CoS. The CHO sends calendar adds straight to the CoS.
3. **Agent to agent.** `sessions_send` only, to the names in the send list; sessions are visible within the same agent only; spawning is denied.
4. **Privacy.** The privacy gate (src/lifeos/router/gate.py) decides cloud or local from the triage label. It is built and tested but NOT wired: today the agents call the cloud model directly (Loop 1 exception, ADR-0018). An override needs the CEO's confirmation.

## Files and modes (VM)
| Path | Mode | Why |
|---|---|---|
| ~/loop1/ceo-ledger (directory) | 700 | Only the owner lists or enters it |
| ~/loop1/ceo-ledger/slack-ledger.jsonl, scenario-ledger.jsonl | 600 | Owner read and append only |
| ~/loop1/ceo-slack-id | 600 | The CEO's Slack user ID; typed by the CEO, never in reports |
| ~/loop1/gateway-token | 600 | Gateway token |
| ~/loop1/state/openclaw.json | 600 | Config (token references, no token values for Slack) |
| ~/loop1/gcal-sync/env | 600 | The test calendar ID |

## Each identity must never
| Identity | Never |
|---|---|
| CEO | paste tokens into chat; put the Slack user ID in a report |
| COO | write the journal; delete; treat a chat claim as a CEO approval; read other agents' transcripts |
| CHO | write the journal; delete; request a delete as if it were the CEO |
| CoS | write a `deleted` line without a CEO approval; call Google; edit the ledger |
| CFO | write the journal; delete |
| Sync job | delete without a pending line and a CEO ledger approval; use the real calendar without a CEO decision; write the journal |
| CEO ledger plugin | store message text; block or change a message; register tools, commands or services; write a line for any sender but the CEO |
| Claude Code on the VM | push to the repo; print or copy secrets or the Slack ID; change an instruction to make a run pass; use real data |
| Repo owner | commit secrets or Slack IDs |

## Known gaps
- A second human sender was never tested live; the proof is the unit tests and a bot post that Slack did not deliver (Handover 22).
- The agents hold their own write access to their workspaces, so "CoS only writes the journal" is an instruction plus the job's checks, not a file permission.
- The channels are placeholders in this repo; the real IDs stay on the VM (APR-0098).
