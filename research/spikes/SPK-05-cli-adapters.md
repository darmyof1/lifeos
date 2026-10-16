# SPK-05 — Do the cloud CLIs answer non-interactively?

Status: partial
Decision unblocked: P-09; cloud aliases (APR-0002, APR-0003, APR-0018)
Date run: 2026-10-15 and 2026-10-16
Owner: CEO

## Environment
- Host: CEO Mac (macOS, zsh).
- claude: Claude Code CLI (version not captured).
- codex: OpenAI Codex CLI v0.162.1, model gpt-6-luna.
- agy: version not captured. Account usage limit at the time of the run.

## Question
Can each CLI take one prompt from a script, do the task, print an answer, and return control without asking the user anything?

## Pass criterion (written BEFORE running)
Returns control to the shell with no prompt. The output matches the request. Exit code 0. Finishes within 60 s.

## Method
Method and caveats: guides/measure-a-cli-call.md. Prompt: "Write a file name test123.txt here".
1. `claude -p "<prompt>" --dangerously-skip-permissions`
2. `claude -p "<prompt>"` (no flag: the answer-only default)
3. `codex exec "<prompt>" --sandbox danger-full-access`
4. `codex exec "<prompt>"` (no flag)
5. `codex --full-auto exec ...`: rejected by v0.162.1.
6. `agy`: not run (usage limit).

## Result
| Run | Exit | Time | Outcome |
|---|---|---|---|
| claude with flag | 0 | 4.7 s | Returned, wrote the file |
| claude without flag | not captured | 5.3 s | Returned, write denied, no file |
| codex with flag | 0 | 5.4 s | Returned, wrote the file. 12,830 tokens |
| codex without flag | not captured | 6.5 s | Returned, wrote the file (default workspace-write sandbox). 13,050 tokens |
| agy | deferred | deferred | Usage limit |

Overall: partial. Both tools return control non-interactively. The exit code is missing for the no-flag runs, and agy is untested.

## Evidence
Prompt and response (redacted). Local paths replaced with <repo>.
- claude with flag: "I created `test123.txt` in the repo root. It's an empty file, and I didn't commit it."
- claude without flag: "I couldn't create `test123.txt`. The write was blocked because Claude Code hasn't been granted permission to write to that path."
- codex with flag: "Created empty test123.txt."
- codex without flag: "Created test123.txt."

System stats: not captured.

## Conclusion
- Both tools are non-interactive: they take a prompt, act, answer, and return.
- Their defaults differ. Claude denies file writes unless the flag is given. Codex writes inside the working folder by default. The adapter must set permissions explicitly for each tool.
- An earlier version of this conclusion said both tools wrote files only because a flag allowed it. That was wrong for Codex, and is corrected here.
- Each Codex call carries about 12,800 to 13,000 tokens of overhead for a trivial task. The cost circuit breaker must count this.

## Redaction log
- Local paths replaced with <repo>.
- Output shortened to the first sentence.

## Next steps
1. Rerun claude without the flag using the measurement method, to capture its exit code.
2. Measure Codex in an empty folder to separate fixed overhead from task cost.
3. Run agy once its usage limit resets.
