# SPK-02-openclaw-state-dir - Does OpenClaw honour a state-directory override?

Status: partial
Decision unblocked: runtime layout
Owner: CEO
Date run: 2026-10-18

## Environment
- Host: Oracle A1 class VM, Ubuntu. OpenClaw 2026.10.4 (fresh install, no agents configured).

## Question
Can OpenClaw keep its state somewhere other than the default state directory?

## Pass criterion (written before running)
With the override set, setup creates the config, workspace and session folders under the override path, and the default state directory is unchanged.

## Method
Step 3 of guides/vm-spike-runbook.md.
1. openclaw --help listed two environment variables: OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH. The docs page read earlier did not mention them. --help is the source for the names.
2. Recorded the file list of the default state directory (31 files) before and after the run.
3. OPENCLAW_STATE_DIR=<test folder>/state OPENCLAW_CONFIG_PATH=<test folder>/state/openclaw.json openclaw setup --baseline

## Result
- setup --baseline: exit 0. Wrote the config, created the workspace and the sessions folder under the override path, and created the state database there.
- Default state directory: file list identical before and after. PASS.
- Pass against the criterion for setup: yes.

## Open (what this spike does not yet prove)
1. The gateway and status commands with the override set. Setup passing does not show that the running gateway reads the same path.
2. Whether --profile gives the same isolation (it is documented in --help as ~/.openclaw-<name>).

## Observations for the design
- The workspace folder is a git repository. Agent files are tracked by git inside the workspace.
- The state folder holds a file named config-journal-fingerprint.key. Treat it as a secret: restrict its permissions and never copy it into the repo.

## Conclusion
The override works for setup. The runtime layout can keep state outside ~/.openclaw. The gateway check is needed before the layout is relied on. The decision is the CEO's and belongs in the runtime layout design.

## Evidence
### Output (redacted)
    OpenClaw 2026.10.4 - Wrote <test-state>/openclaw.json; Workspace OK; Sessions OK; Setup complete.
    exit=0
    diff before/after of default state: no difference

## Redaction log
- Paths: placeholders used for the test folder. No account names, hostnames or IPs recorded.
