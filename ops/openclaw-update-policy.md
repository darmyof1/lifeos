# OpenClaw update policy

Status: draft, written 2026-11-01 under APR-0112. Decider: the CEO. Changeable: yes; a change is a new approval.

## Rule
The OpenClaw version is pinned to 2026.10.5 (APR-0060; the health check fails on any other version). Nobody updates it on the live VM without the CEO's approval. An update is a change of the platform under every agent, so it is tested first and can be undone.

## When to update
- A security fix that applies to how we use OpenClaw (Slack socket mode, plugins, gateway), or
- A fix for a bug that costs us runs (for example the Slack plugin cleanup warning, or the sessions_send acknowledgement error P-35), or
- A feature the roadmap needs (for example a hook for the privacy gate).
Not for "a newer number exists". Check the release notes at most once a month and write one line in ops/install-log.md.

## How (in this order)
1. Read the release notes for every version between 2026.10.5 and the target. List anything about plugins, hooks, Slack, sessions, the gateway, config keys and defaults. Write the list in the proposal to the CEO (seven items).
2. Back up (no step below may start without this): the config (`openclaw.json` and its `.bak` files), the four workspaces (git repos), the crontab (`crontab -l`), the plugin folder `~/loop1/state/extensions/ceo-ledger`, and an encrypted archive as in ops/recovery/restore-drill.md. Record sha256 of each.
3. Build a scratch copy: a separate state folder (set `OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` to a new folder) and the new version installed beside the pinned one, not over it. Never run two gateways on the same Slack tokens: stop the live gateway before the scratch gateway talks to Slack, or run the scratch one without Slack (CLI only).
4. Run the checks on the scratch copy: unit tests, the health check with the new pin, the plugin load check (`openclaw plugins inspect ceo-ledger`: enabled, hook-only), and the regression suite (single-scenario suites, at least 3 runs each of D1, D2, D3, overlap, privacy) with the cron paused. Compare pass counts with the last results on the pinned version (Handover 21: D1, D2, D3 pass). Check cost per run and turns.
5. Compare: any scenario that passes less often, any new warning, any change in the ledger plugin's hook, any change in config keys is a stop. Write the comparison table in the report.
6. The CEO decides (approve, explain more, or keep). If approved: use the kill switch (scripts/ops/kill-switch.sh), switch the install, update the pin in the health check, restart the gateway once, run the health check and one scenario of each type, then restore the cron.
7. One update per handover. No other change in the same handover.

## Rollback
Stop the gateway; reinstall the pinned version; restore the config from the backup of step 2 (compare sha256); restore the plugin folder; start the gateway once; run the health check (73 PASS or better) and one run of D1; restore the cron. The workspaces are git repos: if an agent file changed, `git checkout` the previous commit of that file and commit it (history stays append-only). If the state folder was damaged, restore from the encrypted archive.

## Never
Update during the 03:30 to 05:10 AST window; update while a scenario run is in progress; update two things at once; update on the CEO's real data.
