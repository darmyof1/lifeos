# SPK-05 — Do the cloud CLIs answer non-interactively?

Status: partial
Decision unblocked: P-09; cloud aliases (APR-0002, APR-0003, APR-0018)
Date run: 2026-10-15
Owner: CEO

## Environment
- Host: CEO Mac (macOS, zsh).
- claude: Claude Code CLI (version not captured).
- codex: OpenAI Codex CLI v0.162.1, model gpt-6-luna.
- agy: version not captured.

## Question
Can each CLI take one prompt from a script, do the task, print an answer, and return control without asking the user anything?

## Pass criterion (written BEFORE running)
Returns control to the shell with no prompt. The output matches the request. Exit code 0. Finishes within 60 s.

## Method
Run from the repo folder:
1. `claude -p "Write a file name test123.txt here" --dangerously-skip-permissions`
2. `codex --full-auto exec "Write a file name test123.txt here"`: rejected by this version.
3. `codex exec "Write a file name test123.txt here" --sandbox danger-full-access`
4. `agy`: not run (account usage limit).

## Result
- claude: returned and answered. Created the file. Exit code: not captured. Timing: not captured.
- codex: returned and answered. Created the file. Exit code: not captured. Timing: not captured. `--full-auto` is not accepted by v0.162.1.
- agy: deferred.
- Overall: partial. Both tools return control, but exit codes and timing are missing, and agy is untested.

## Evidence
### Prompt and response (redacted)
claude: "I created an empty file named test123.txt in the working directory ... I didn't commit it, so it shows up as an untracked file in git."
codex: "Created test123.txt."
Local paths replaced with <repo>.

### System stats
Not captured.

## Conclusion
Both tools accept a prompt non-interactively and return. Both wrote a file only because a permission or sandbox flag allowed it. Those flags turn off safety prompts. The router must not use them for answer-only tasks. Rerun with the flags removed to see what the safe default does.

## Redaction log
- Local paths replaced with <repo>.
- Output shortened to the first sentence.

## Next steps
1. Rerun each command followed by `; echo "exit=$?"` and record the exit code and `time` output.
2. Test answer-only mode without the permission or sandbox flags.
3. Run agy once its usage limit resets.
