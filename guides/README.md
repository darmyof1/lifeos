# Guides

How to set up and repeat a tool on the VM or the Mac. Written so that a fresh install can be done from the guide alone.

| Guide | Status | Last verified |
|---|---|---|
| calendar-gcalcli.md | working (read and write; login renewed 2026-10-25) | 2026-10-25 |
| calendar-rest-api.md | working (round trip passed from the repo on the VM) | 2026-10-25 |
| calendar-sync-job.md | partial (built and unit-tested; not yet run on the VM) | not yet run |
| slack-multi-identity.md | working (two identities; leakage check open) | 2026-10-19 |

## Rules for every guide
1. Commands are copied from a real run, and each one shows its expected output.
2. Steps a human must do are marked (HUMAN). Secrets are never written here; use the placeholder names.
3. Every guide ends with a troubleshooting table built from problems that actually happened.
4. Every guide records the exact tool version it was verified with. Versions change.
5. A guide is updated when a step changes, and the change is dated in ops/install-log.md.
6. Code blocks use straight quotes only (" and '). A curly quote breaks a command. Check 12 in the validator blocks them.

## Where things are logged
| What | Where | In the repo? |
|---|---|---|
| How to do a thing again | guides/<tool>.md | yes |
| What was done, on which host, when | ops/install-log.md | yes (sanitized) |
| Test evidence for a design question | research/spikes/ | yes (redacted) |
| Raw transcripts with personal data | your seed folder (private) | never |
