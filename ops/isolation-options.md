# Agent isolation: what is contained, what is not, options (Loop 7, handover 27, APR-0124)

Evidence: research/spikes/SPK-03-agent-isolation.md, section "Results 2026-11-09" (raw files in the handover package). Synthetic data only. The CEO decides; nothing here is installed or changed.

## Contained today
- File tools: CHO, CoS and CFO have read, write and edit with `fs.workspaceOnly: true`. Reading or writing a path outside their own workspace is refused by the tool ("Path escapes sandbox root"), also with a relative path (5 of 5 tries in a scratch copy with the same settings).
- The COO has no file tool at all (tool profile "messaging"); its code-mode tool lists no shell, file, edit or patch tool.
- Agents reach each other only through sessions_send, limited by the send lists (APR-0044, APR-0092), and `tools.sessions.visibility` is "agent".

## Not contained
- The protection is one setting per agent. The schema default for `fs.workspaceOnly` is false: without the key, an agent reads other workspaces (the baseline run did). A new agent (the CLO in Loop 7 part 3) is exposed until its entry carries the key.
- No container: sandbox mode is off for all four agents and Docker is not installed. All four agents, the gateway and the Slack plugin run as the same operating-system user. Anything that user can read (all workspaces, the stored sessions, the config, the model key) is out of reach of the agents only because of the tool rules above.
- The model provider (cloud) sees everything an agent sees (threat model residual risk 5). Isolation between agents does not change that.
- A model's refusal is not a control: when asked to try other ways, the model sometimes declines, sometimes not. Only the tool refusal counts.
- Not measured: a shell tool (none in these profiles, so it could not be tried), and the effect of a future plugin or tool added to a profile.

## Options to close the gap (the CEO chooses; I recommend installing nothing now)

### Option A: guard the setting (smallest)
What: add a health-check line (FAIL if any agent entry that has file tools lacks `fs.workspaceOnly: true`), and a rule in the new-agent checklist for the CLO.
Cost: small repo change (health check plus test); about half a handover.
Risk: low. It detects drift; it does not stop it.
Live change needed: installing the health-check file only (the same step as before). No config change.
What I would test: a scratch config without the key makes the line FAIL; the live config makes it PASS; the canary read on the scratch agent without the key succeeds (already shown) and with the key is refused.

### Option B: least privilege for the file tools
What: take write and edit away from agents that do not need them (check each agent's instructions first: the CoS writes the journal; the CHO and CFO may only need read). A tool an agent does not have cannot be misused.
Cost: one config edit per agent plus a regression suite (about 7 runs, about 0.1 USD); one handover.
Risk: medium. If an instruction relies on write or edit, that scenario fails; the suite shows it before closing.
Live change needed: yes, config keys for the agents (hot reload; restart only if it does not apply).
What I would test: scratch copy first (canary and the seven regression scenarios), then live only after your approval.

### Option C: Docker sandbox per agent (hard isolation)
What: install Docker and set `sandbox.mode` to "all" (or "non-main") with `workspaceAccess` "rw" for the agent's own workspace only, so each agent runs in a container that sees only its own folder.
Cost: highest: Docker install on the VM, config changes, possible gateway restart, and a full re-test of every scenario (the agents read and write the journal, run the calendar tools and talk to each other from inside a container).
Risk: highest: tool behaviour in a container is untested here (SPK-03 could not test it), the CPU of this VM is small, and a mistake can stop all four agents. Rollback is a config change back to "off".
Live change needed: yes (Docker, config, maybe a restart).
What I would test: first a scratch gateway with Docker and two canary agents with the same profile (does b still fail to read a, with the sandbox on and workspaceOnly off?), then one agent live, then the others.
