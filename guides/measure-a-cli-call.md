# Measuring a CLI call: exit code, time, tokens

Status: working (verified on the CEO Mac, 2026-10-16)
Last verified: 2026-10-16, macOS, zsh
Tool versions: Claude Code (version not captured); Codex CLI v0.162.1
Owner: CEO

## What this is for
A test result without an exit code and a time is not evidence. This guide shows how to capture both, and what went wrong in our first attempts.

## Method (use this one)
```
start=$(date +%s.%N)
<command> "<prompt>"
exit_code=$?
end=$(date +%s.%N)
echo "exit=$exit_code time=$(echo "$end - $start" | bc)s"
```
This is correct because `$?` is read immediately after the command.

To also keep the output, write it to a file outside the repo (the repo is public and tracked):
```
<command> "<prompt>" > "$HOME/lifeos-workbench/state/run.log" 2>&1
echo "exit=$?"
```

## Do NOT use
- `echo "Exit code: ${PIPESTATUS[0]}"` after a pipeline. On macOS the shell is zsh, which has no `PIPESTATUS`. The line prints an empty value. We recorded empty exit codes this way on 2026-10-16.
- If you need the pipeline form, zsh uses `$pipestatus`. Check it once: `false | true; echo $pipestatus` should print `1 0`.

## Tokens
- Codex prints `tokens used` in its output. Record that number.
- Claude Code did not show a token count in these runs. Record "not shown".

## Observed runs (2026-10-16, same prompt: "Write a file name test123.txt here")
| Tool | Flags | Exit | Time | Tokens | Result |
|---|---|---|---|---|---|
| codex | `--sandbox danger-full-access` | 0 | 5.4 s | 12,830 | Wrote the file |
| codex | none (sandbox defaulted to workspace-write) | not captured | 6.5 s | 13,050 | Wrote the file |
| claude | `--dangerously-skip-permissions` | 0 | 4.7 s | not shown | Wrote the file |
| claude | none | not captured | 5.3 s | not shown | Write denied; no file |

Notes:
- Codex wrote the file without any permission flag, because its default sandbox allows writes in the working folder. Claude denied the write without its flag. The two tools have different defaults. The router must set the flags explicitly and never rely on defaults.
- A trivial file write cost about 12,800 to 13,000 tokens in Codex. That looks like a fixed overhead per call. Measure it with an empty folder before budgeting.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `Exit code:` is empty | `PIPESTATUS` in zsh | Use the method above |
| Claude says it cannot write | Permission denied in non-interactive mode | Expected for answer-only tasks. Add the flag only when a write is intended |
| A stray `test123.txt` or `execution.log` appears in git status | Test output written into the repo | Write test output outside the repo, or delete it. The validator blocks it from being committed |
