# SPK-06 — Can the local model run on the VM?

Status: partial
Decision unblocked: P-05 (resolved as APR-0019); backup in APR-0025
Date run: 2026-10-12
Owner: CEO

## Environment
- Host: Oracle A1 Flex VM (24 GB RAM). Hostname redacted.
- OS: Ubuntu 24.04 LTS. Ollama: version not recorded yet (TODO).

## Question
Can llama3.1:8b answer a prompt on the VM with memory and speed we can live with?

## Pass criterion (written BEFORE running)
Responds to a plain prompt; resident memory under 8 GB; time to first token under 5 s. Tokens/s not yet measured (TODO).

## Method
1. `ollama run llama3.1:8b`
2. Send a plain prompt, then exit.
3. While the model answers, capture `htop` (process lines only).

## Result
- Responds: pass.
- Resident memory: about 5.3 GB for the runner process: pass.
- Time to first token: not measured. TODO.
- Tokens/s: not measured. TODO.
- Overall: partial. Enough to pick the model, not enough to size the VM.

## Evidence
### Propose test
```
ollama run llama3.1:8b --verbose    # prints load time, prompt eval rate, and eval rate (tokens/s)
ollama ps                           # shows what's loaded and its memory
free -h                             # total memory used
```
### Prompt and response (redacted)
```text
>>> Testing, how are you
I'm functioning properly! I'm here to help with any questions or topics you'd like to discuss. How
can I assist you today?
```
### System stats (redacted)
```text
  PID USER      PRI  NI  VIRT   RES   SHR S CPU%  MEM%   TIME+ Command
 3027541 ollama  20   0 7202M 5302M 27296 R 45.8 22.1 0:26.46 /usr/local/bin/ollama runner --model ...
```

## Conclusion
llama3.1:8b runs on the VM at about 5.3 GB resident. Recorded as APR-0019. The timing numbers are still needed before we size the VM for Genesis.

## Redaction log
- Shell prompt with the VM hostname removed.
- The VPN server process line removed (not needed for this test, and it exposes network setup).
- Other system processes removed.
- Ollama runner path shortened to "...".

## Next step to finish this spike
Rerun with `ollama run llama3.1:8b --verbose` and record the printed eval rate and load time. Then mark Status: done.
