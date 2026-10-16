# SPK-09 - Does the API accept the model ID claude-haiku-5-5?

Status: done
Decision unblocked: P-08 (aliases.yaml option ID, APR-0021)
Owner: CEO
Date run: 2026-10-16

## Environment
- Host: Apple Mac (client). The API is Anthropic's hosted service.
- OS and versions: macOS. Claude Code CLI (claude). curl.

## Question
Does the Anthropic API accept the model ID claude-haiku-5-5 and return it as the model used?

## Pass criterion (written after the run, stated plainly)
HTTP 200 from the messages endpoint, and the returned model field equals claude-haiku-5-5. The CLI run must return a text answer with the --model flag set to claude-haiku-5-5.

## Method
1. Export the key from your own environment. Do not paste it anywhere: export ANTHROPIC_API_KEY set to your key.
2. Send one small request, with max_tokens 10 and the prompt "Hi":
   curl -i -s -X POST "https://api.anthropic.com/v1/messages" -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d '{"model": "claude-haiku-5-5", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'
3. Run the CLI once: claude --model claude-haiku-5-5 -p "Hi"
4. Confirm the model ID against the official overview page: platform.claude.com/docs/en/models/haiku-5-5/overview

## Result
- API: HTTP/2 200. Returned model: claude-haiku-5-5. stop_reason: max_tokens (expected, because max_tokens was 10). Input tokens 11, output tokens 10. Client time 1.01 s.
- CLI: returned a text answer with --model claude-haiku-5-5. Two runs: 19.8 s (with --dangerously-skip-permissions) and 3.2 s (with --permission-mode auto).
- Pass against the criterion: yes.
- Not recorded: exit codes of the CLI runs. The shell printed them empty (zsh PIPESTATUS issue, see guides/measure-a-cli-call.md). The HTTP 200 is the evidence for the API.

## Evidence
### Prompt and response (redacted)
Prompt: "Hi". Response: "Hi! How can I help you today" (cut at 10 tokens by max_tokens).

### System stats (redacted)
Not applicable. This spike is a remote API call.

## Conclusion
The model ID claude-haiku-5-5 is accepted by the API and works through the CLI. The option in contracts/models/aliases.yaml (APR-0021) is probed. Switching to it is still the CEO's decision under APR-0021. P-08 is closed once the CEO approves it.

## Redaction log
- API key: never written to a file or to chat. The request in the method uses an environment variable.
- Organization ID and workspace ID from the response headers: removed (account identifiers).
- Request ID and trace headers: removed.
- Local repository name and branch in the CLI answer: removed.
