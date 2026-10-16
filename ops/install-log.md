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
