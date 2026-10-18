# SPK-02-openclaw-state-dir - Does OpenClaw honour a state-directory override?

Status: done
Decision unblocked: runtime layout
Owner: CEO
Date run: 2026-10-18

## Environment
- Host: Oracle A1 class VM, Ubuntu. OpenClaw 2026.10.4, fresh install with one default agent. The default state directory already held the install's files from an earlier run.

## Question
Can OpenClaw keep its state somewhere other than the default state directory?

## Pass criterion (stated in the runbook step 3; recorded after the run)
With OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH set, setup, status and the gateway create and read their state under the override path, and the default state directory is unchanged by those runs.

## Method
Runbook step 3 (guides/vm-spike-runbook.md).
1. The CLI help lists OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH. Used as the names.
2. Setup under the override: openclaw setup --baseline. Exit 0.
3. Default state directory listed before and after setup: identical.
4. Gateway run under the override, in its own terminal. Started and reported ready. Stopped with Ctrl-C afterwards.
5. Status under the override.
6. Doctor under the override was started by mistake and cancelled at its apply prompt (exit 130). No repairs were applied.

## Result
- Setup: exit 0. Config, workspace, sessions and state database created under the override. PASS.
- Default state directory: unchanged after setup. PASS.
- Gateway: started under the override. Status reports its agent database at the override path, and the gateway's state folders (cache, media, tmp, state, plugin-skills) are under the override. PASS.
- Gateway log file: written to /tmp/openclaw/, not the override. NOT under the override.

## Open items (not blocking the layout decision)
1. Gateway log location is outside the override. Logs need a separate decision: an ops-logs location, or a config key that moves them (to be found with openclaw config --help).
2. At runtime, gateway auth showed "none". The gateway generated a token for the run and warned that a restart changes it. Set a persistent token (gateway.auth.mode and gateway.auth.token, or OPENCLAW_GATEWAY_TOKEN) before channels are connected.
3. The default model is openai/gpt-6-astra, which needs an OpenAI key. The local model must be set as the default before agents run without a cloud key.
4. The state folder holds config-journal-fingerprint.key. Treat it as a secret.

## Conclusion
The runtime layout can keep OpenClaw state outside the default folder, using the two environment variables. The layout decision (where state lives) is the CEO's and belongs in the runtime layout design. Logs and the gateway token must be decided before the layout is final.

## Redaction log
- Paths: test folder and VM IP address omitted. No account names recorded.
