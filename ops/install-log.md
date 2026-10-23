# Install and change log (sanitized)

Append-only. One dated entry for each change on any host. Secrets, tokens, authorization codes, and personal values never go in this file. Raw transcripts stay in your private seed folder.

## 2026-10-15 — Oracle VM — gcalcli (calendar)
Host: Oracle VM, Ubuntu 24.04 arm64 (hostname not recorded here).
- Removed the apt package gcalcli 4.3.0 (it has no `init` command).
- Installed pipx and python3-venv. Ran `pipx ensurepath`. Added `~/.local/bin` to PATH in `~/.bashrc`.
- `pipx install gcalcli` gave version 4.5.1.
- Created the Google Cloud OAuth client (Desktop app). Values kept in the password manager.
- Authenticated with `gcalcli --client-id=... init` through an SSH tunnel to the redirect port.
- Read test: `gcalcli list` and `gcalcli agenda` passed.
- Write test: added "LifeOS write test" to the primary calendar at 17:00. Visible in agenda. Deletion from the web app still to confirm.
- ACTION (owner: CEO): the client secret appeared in a chat transcript. Reset it in Google Cloud Console and update the password manager. Status: open until reset is confirmed.
Guide: guides/calendar-gcalcli.md

## 2026-10-15 — CEO Mac — AI command-line tools
Host: CEO Mac (macOS, zsh).
- `claude -p "<prompt>" --dangerously-skip-permissions`: returned and created a file. Permission flag was required for the write.
- `codex exec "<prompt>" --sandbox danger-full-access`: returned and created a file. The `--full-auto` flag is not accepted by Codex v0.162.1.
- `agy`: not run. Account usage limit. Deferred.
- Both file writes left `test123.txt` in the repo folder. It is untracked. Delete it before the next commit.
Evidence: research/spikes/SPK-05-cli-adapters.md

## 2026-10-16 — CEO Mac — test corrections
- test123.txt had been committed by fix-9 (the stray file was in the repo folder during `git add -A`). Removed in this fix. Blocked by the validator from now on.
- Two timing methods were tested. The `PIPESTATUS` method gives an empty exit code in zsh. The `$?` method works. See guides/measure-a-cli-call.md.
- SPK-05 corrected: Codex writes files by default, so the earlier conclusion was wrong for Codex.
- Delete-by-ID steps added to guides/calendar-gcalcli.md.

## 2026-10-16 — repo — fix-11
- The fix-10 that ran on the Mac was an older version. It did not include validator check 12 or guide rule 6. fix-11 adds them.
- The registry generators (fix-4 to fix-10) listed files from the disk, so local git-ignored files such as execution.log appeared in the registry. The validator then failed on any clean clone. fix-11 generates the registry from git's tracked-file list. Use this method in all future scripts.
- Local test output stays outside the repo or in ignored paths.

## 2026-10-16 - decisions and tests
- APR-0032: calendar content in Google is titles only for now (changeable by a new APR entry). contracts/policy/calendar.yaml added as a draft.
- APR-0033: ADR-0003 accepted.
- Test logs moved from the AI workbench to ~/lifeos-ops/logs (outside the repo). Create it once with mkdir -p.
- Calendar guide: search and delete commands added, with <calendar-email> placeholder.
- SPK-06 done: 3.68 tokens per second. Triage latency opened as P-14.

## 2026-10-16 - naming mandate
- APR-0034: calendar event names follow "<DOMAIN> - <Title> - <MMDDYYYY>-<NNNN>". Interpretation open in P-15.
- P-14 rewritten in plain language.

## 2026-10-16 - calendar command tests (fix-14)
- Tested on the Oracle VM with gcalcli 4.5.1: create two events, search by full title, search with a date range, agenda, delete by title with --iamaexpert. Delete printed "Deleted!". Calendar email kept out of the repo.
- End dates are excluded in search and agenda. 2026-10-18 is needed to include 2026-10-17.
- Delete by event ID: rejected. The delete command takes search text, and --noprompt is not valid for delete ("unrecognized arguments: --noprompt"). The event IDs are Google's own IDs (gcalcli reads them from the Google API), but delete does not accept them. The guide now uses the full title.
- Not yet confirmed on the VM: the --details id --tsv column layout. The add command prints nothing on success; success was confirmed by search (the Google Calendar web app check is still to be done).
- APR-0035: P-15 approved (date order, counter per date, domain codes). APR-0037: meanings of the codes (CFA Family, CFO Finance, CSO Social). APR-0036: P-14 accepted for now (about 20 seconds triage). P-14 and P-15 closed.

## 2026-10-16 - model probe and token path (fix-17)
- SPK-09: claude-haiku-5-5 accepted by the API (HTTP 200) and by the CLI. Account identifiers removed. Exit codes of the CLI runs were not captured (zsh PIPESTATUS issue).
- Calendar token path corrected: gcalcli 4.5.1 stores the OAuth token at ~/.local/share/gcalcli/oauth. The guide used ~/.gcalcli_oauth. A test host showed no file at the old path. Confirmation on the VM is pending (P-13).

## 2026-10-16 - token check on the VM (fix-18)
- Token file found at ~/.local/share/gcalcli/oauth, owner ubuntu. Mode was 664, changed to 600 and confirmed with stat. P-13 awaits CEO yes.
- P-08 approved (APR-0040).

## 2026-10-16 - P-13 approved (fix-19)
- APR-0041: calendar token location confirmed on the VM. P-13 closed.

## 2026-10-16 - P-18 approved (fix-21)
- APR-0042: ADR-0002 accepted, including the tie-break. P-19 (scenario catalogue) still open.

## 2026-10-16 - P-19 approved (fix-22)
- APR-0043: scenario catalogue approved. S-06 (5-minute retry, COO escalation at attempt 5) and S-07 (CIO Slack alert) changed by the CEO. P-19 closed.

## 2026-10-16 - Slack exemption (fix-24)
- APR-0045: private data may be posted in private Slack channels until the in-house app exists. Model calls still pass the gate. privacy.yaml header corrected (not yet enforced in code).

## 2026-10-16 - P-20, P-21, P-22 approved (fix-25)
- APR-0046: instruction drafts from approved rules (CSTO). APR-0047: LLM call log approved, CISO leak check added. APR-0048: Slack model, one app and one channel per agent.
- New pending: P-23 (agent-to-agent visibility), P-24 (leak check detail).

## 2026-10-16 - P-24 approved (fix-26)
- APR-0049: CISO leak check scans all sources weekly and reports directly to the CEO. P-24 closed.

## 2026-10-16 - P-23 approved (fix-27)
- APR-0050: cross-agent visibility approved. Real-world changes and failures are posted to Slack; routine traffic stays in the call log. P-23 closed.

## 2026-10-16 - CHO scenarios drafted (fix-28)
- design/cho-scenarios.md: C-01 to C-06 (draft). P-25 pending with six questions.

## 2026-10-16 - P-25 approved (fix-29)
- APR-0051: CHO owns therapies (CSP proposes); therapy titles show the name; CIO owns alarms and needs an alarm skill; supplement timing free; meal plans local for now. P-25 closed.

## 2026-10-17 - VM spike runbook added (fix-30)
- guides/vm-spike-runbook.md: steps for SPK-07, SPK-01, SPK-02, SPK-03, SPK-04. No spike run yet.

## 2026-10-18 - SPK-07 Part A run (fix-31)
- Part A: passphrase cache found and cleared before decrypt. Wrong passphrase fails (Bad session key, exit 2). MATCH line pending rerun. Part B (asymmetric) added to the runbook, not run.

## 2026-10-18 - SPK-07 done (fix-32)
- Part A (passphrase) and Part B (public key on the VM, CEO restores) passed. Runbook Part B corrected (encryption subkey). Decision on archive encryption left to the CEO (APR-0010 / ADR-0012).

## 2026-10-18 - SPK-01 done (fix-33)
- Per-user outbound block works: test user blocked from the internet, loopback open, ordinary user unaffected. Limits: not tested on an OpenClaw process; rule not persistent.

## 2026-10-18 - SPK-02 partial (fix-34)
- OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH move setup's state; the default state is unchanged. Gateway check open.

## 2026-10-18 - SPK-02 done (fix-35)
- OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH move state for setup, status and the gateway. Logs go to /tmp. Gateway auth none at runtime; default model is cloud.

## 2026-10-18 - SPK-03 partial (fix-36)
- Two test agents with separate workspaces; sandbox mode off by default; Docker not installed (deferred to deploy).
- Isolation-off canary not obtained: local model turns did not complete on this VM. Plain Ollama answers in seconds; OpenClaw turns with the tool catalog did not.
- Added guides/local-model-setup.md.

## 2026-10-19 - SPK-04 Part A done (fix-37)
- Two Slack apps (From a manifest), two accounts in one Gateway on port 19001, two agents bound to their accounts.
- Each agent posted as its own identity (spk04-b APP, spk04-a APP). Runs: 14.7 s and 22.1 s with a hosted model.
- Leakage check limited: the account argument of a send is not in the stored transcript. Part B not run.
- Added guides/slack-multi-identity.md and research/spikes/SPK-04-slack-multi-identity.md.

## 2026-10-19 - SPK-04 cleanup verified (fix-38)
- Top-level Slack tokens removed; gateway auth token saved; both accounts connect; spk04-b direct send posted as spk04-b APP.
- Incident: a gateway stop run without the state variables stopped the default openclaw-gateway.service. Restarted with systemctl --user start. Variables now set per terminal (env.sh).
- Incident: a second gateway run on the same state folder caused a stall and a Slack socket error. Stopped; the first gateway reconnected.

## 2026-10-19 - SPK-04 model verified (fix-39)
- Utility model set explicitly to openai/gpt-6-luna (it had been the provider default gpt-5.6-luna).
- Old OpenAI keys revoked; one project key (life-os) remains in the spk04 env file.
- Billing re-check pending for the next day.

## 2026-10-20 - SPK-04 binding, channel and owner checks (fix-40)
- spk04-b binding verified by a mention. Event subscription and app_mentions:read added in the Slack app settings. Channel allowlist entry added.
- /new still refused (control-command-unauthorized). commands.ownerAllowFrom tried, not effective.
- A thread turn was served by openai/gpt-6-luna. Part B paused.

## 2026-10-20 - SPK-04 billing re-check (fix-41)
- gpt-6-luna is the only billed model in the test. gpt-5_6-luna shows $0. Billing confirmed.

## 2026-10-21 - SPK-04 close-out on AWS (fix-42)
- New guide: guides/openclaw-and-ollama-install.md.
- guides/local-model-setup.md updated: tool calling settings and proof, troubleshooting rows, open items.
- Instance terminated. Transfer copies on the Mac must be deleted by hand.

## 2026-10-22 - Loop 1 decisions recorded (fix-43)
- APR-0052 to APR-0056 and ADR-0018: time-boxed cloud-only exception, Slack test, local calendar journal, instruction approval, cost limits.
- PENDING P-26 to P-29 added. SPK-10 planned.

## 2026-10-22 - Loop 1 baseline on the Oracle VM (fix-44)
- State folder ~/loop1/state created; config written by patch (model gpt-6-luna, utility model, messaging profile). Validated; no secrets in the file.
- Old key copy removed; a new key stored in ~/loop1/openai.env (names checked only).
- Agent commands read from help text; not run. See guides/loop1-baseline.md.

## 2026-10-22 - Agent tests on the Oracle VM (fix-45)
- Four agents added (COO, CHO, CoS, CFO) with the gateway stopped; first-run files removed.
- Agent-to-agent allow lists, sessions visibility (agent) and sub-agent limits set by patch.
- File tools enabled for CoS, CHO and CFO with workspaceOnly. A handoff from CHO to CoS and a diet change from CHO to CFO both passed.
- Details and results: guides/loop1-baseline.md, section 7.
