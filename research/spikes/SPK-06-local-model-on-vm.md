# SPK-06 - Can the local model run on the VM?

Status: done
Decision unblocked: P-05 (resolved as APR-0019); P-14 (triage latency, opened by this spike)
Date run: 2026-10-16
Owner: CEO

## Environment
- Host: Oracle A1 Flex VM, Ubuntu 24.04 arm64, 24 GB RAM. Hostname redacted.
- Model: llama3.1:8b (digest 46e0c10c039e).
- Ollama version: not recorded (TODO).

## Question
Can llama3.1:8b answer on the VM within the memory and latency we can live with?

## Pass criterion (written BEFORE running)
- Responds to a plain prompt.
- Resident memory under 8 GB.
- Time to first token under 5 s.
- Tokens per second: recorded. No pass criterion was set for it.

## Method
1. ollama run llama3.1:8b --verbose
2. Prompt: "what is the command in linux to list directories"
3. Record the stats printed after the answer.

## Result
- Responds: pass.
- Resident memory: about 5.3 GB (htop run, earlier): pass.
- Time to first token: load 0.19 s plus prompt evaluation 3.90 s, about 4.1 s: pass.
- Generation: 380 tokens in 1 min 43 s, 3.68 tokens per second.
- Total: 1 min 47.6 s.
- Overall: done. The model works. Generation speed is the finding (see Conclusion).

## Evidence
### Verbose stats (copied)
total duration: 1m47.55062883s
load duration: 192.700714ms
prompt eval count: 288 token(s)
prompt eval duration: 3.902007423s
prompt eval rate: 73.81 tokens/s
eval count: 380 token(s)
eval duration: 1m43.144405845s
eval rate: 3.68 tokens/s

### Prompt and response (summarized)
Prompt: "what is the command in linux to list directories". The answer was a structured list covering ls, cd, pwd, tree, and find, with options. The answer was correct.

### System stats
Earlier htop run: resident memory about 5.3 GB for the runner process.

## Conclusion
The model runs on the VM and answers correctly. Generation at 3.68 tokens per second is slow. A routing JSON of about 60 tokens would take roughly 20 seconds including prompt processing. The design assumed triage under one second, which this VM does not meet. The model choice (APR-0019) stands. The triage latency is a separate decision, recorded as P-14.

## Redaction log
- Hostname removed.
- Full answer text summarized.

## Next steps
1. Decide P-14.
2. If option b: write SPK-08 comparing smaller local models on token rate and on routing-JSON quality.
