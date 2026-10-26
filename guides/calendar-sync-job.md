# Calendar push job - guide

Status: working (VM test 2026-10-26 passed; cron installed 2026-10-26, every 5 minutes, test calendar)
Last verified: 2026-10-26 on Oracle VM, Ubuntu 24.04 arm64, against a separate test calendar
Tool version: Python 3.12 from the gcalcli pipx environment (gcalcli 4.5.1, google-api-python-client 2.201.0); OpenClaw 2026.10.5 for the alert
Owner: CEO

## What this is for
The CoS writes every calendar entry it means to make into its journal (`~/loop1/workspaces/cos/state/calendar-journal.md`). The push job reads that journal, creates or moves the events in Google Calendar, and appends the result as new lines. It is code, not the model (ADR-0008, ADR-0011). Decided in APR-0077 (design) and APR-0078 (the four defaults). Google stays the calendar of record (APR-0031).

## What it does
- Reads the journal. The latest line of each name decides what to do.
- `written`: create the event, or move the old event when a `moved` line with the same run ID and event ID came first (APR-0057). Then append a `pushed` line with `google=<event id>`.
- `failed`: tried again on the next run, up to 5 attempts. The 5th failure is final, and the alert goes to the COO channel (S-06).
- `deleted`: executed only with `--allow-deletes` and only after a `delete-pending-approval` line for the same event ID (APR-0044). Off by default.
- `requested`, `pushed`, `conflict`, `moved`, `delete-pending-approval`: nothing to do.
- Before it creates anything it searches Google for the exact title (APR-0034). If the title is already there at the same time, it just records `pushed`. If it is there at another time, or twice, it appends `conflict` and touches nothing.
- If Google says the login was revoked (invalid_grant or HTTP 401), it writes the pause file, sends one alert, and does nothing more until you log in again and remove the file (S-07, APR-0043).
- It never edits or removes a journal line (APR-0054, APR-0058). The health check still fails on any removed line.
- It never touches personal events. Only title, start and end go to Google (APR-0032).

Lines the job writes use the same 7 columns plus a detail column, and `sync` as requested by:
`name | start | end | pushed | run ID | event ID | sync | google=<id>`
`name | start | end | failed | run ID | event ID | sync | attempt=2; error=...`
`name | start | end | conflict | run ID | event ID | sync | reason=...`

## Before you start (HUMAN)
1. The REST scripts work on the VM (guides/calendar-rest-api.md, Verify step 4).
2. Use a separate Google test calendar for the first tests, not your main calendar. Create it in Google Calendar and copy its calendar ID. Never write the ID in the repo.
3. Find the name of the COO channel variable without printing values: `cut -d= -f1 ~/loop1/slack-channels.env`. The alert target is `channel:<ID>`, for example `channel:C0123456789`.

## Run it by hand first
On the VM as `ubuntu`:

```
cd ~/lifeos-ro && git pull
PY=~/.local/share/pipx/venvs/gcalcli/bin/python
export GCAL_CALENDAR="<test calendar id>"
```

1. Unit tests (expected: `OK`): `python3 -B -m unittest discover -s tests/unit -p "test_gcal*.py"`
2. Make a test journal outside the CoS workspace: `mkdir -p ~/loop1/gcal-sync-test` and put two lines in `~/loop1/gcal-sync-test/journal.md`: a header line and `CHO - Sync test - 10282026-9001 | 2026-10-28 07:00 | 2026-10-28 08:00 | written | test | test-01 | test`
3. Dry run (reads Google, writes nothing, appends nothing): `$PY scripts/gcal/gcal_sync.py --journal ~/loop1/gcal-sync-test/journal.md --state-dir ~/loop1/gcal-sync-test --dry-run`. Expected: `would CHO - Sync test ... created` and `dry run: pushed 1, ...`
4. Real run: the same command without `--dry-run`. Expected: `done  ... created <id>`, `summary: pushed 1, ...`, and one new `pushed` line in the test journal.
5. Run it again. Expected: `pushed 0`, nothing new in the journal.
6. Clean up the test event with the delete script and your approval (APR-0044): `$PY scripts/gcal/gcal_delete.py --id <id> --title "CHO - Sync test - 10282026-9001" --ceo-approved --approval-note "<where you said yes>"`

## Test the alert
Set the target for this shell, then send one test message:

```
export LIFEOS_ALERT_TARGET="channel:<COO channel ID>"
$PY scripts/gcal/gcal_sync.py --test-alert --state-dir ~/loop1/gcal-sync-test
```

Expected: `alert: sent` and the message in the COO channel. Every alert is also written to `alerts.log` in the state folder. If the line says `send failed`, the reason is printed. If it says `no System Agent owner`, OpenClaw needs a System Agent setting (`agents.defaults.systemAgent.agentId`); that is a config change and needs your yes first. Until then alerts only reach `alerts.log`.

## Turn it on (after your go)
1. Create the settings file (mode 600, never committed): `~/loop1/gcal-sync/env` with the lines `GCAL_CALENDAR=<calendar id>`, `LIFEOS_ALERT_TARGET=channel:<COO channel ID>` and, if needed, `LIFEOS_ALERT_ACCOUNT=<slack account>`.
2. Run the wrapper once by hand: `bash ~/lifeos-ro/scripts/gcal/gcal_sync_cron.sh; tail -n 5 ~/loop1/gcal-sync/sync.log`. Expected: a block that starts `=== <time> exit 0`.
3. Add the cron line with `crontab -e` (every 5 minutes, plain cron under ubuntu, APR-0078): `*/5 * * * * bash $HOME/lifeos-ro/scripts/gcal/gcal_sync_cron.sh`
4. The wrapper appends to `~/loop1/gcal-sync/sync.log` and keeps it to about 1500 lines. The job pushes at most 20 entries per run.

## Scenario resets
Resetting the journal (`git checkout -- state/`) while the job runs would leave events in Google that the journal no longer knows about, and the pushed lines would break the numstat check (2 0). Every scenario run therefore pauses the cron before the reset and resumes it after the checks and the export. The commands are in tests/scenario/bad-sleep-reschedule.md ("Loop 2 calendar cron (APR-0078)") and in deploy/loop1/STATE.md. Pause (the line must start with #):

```
crontab -l | sed 's|^\*/5 .*gcal_sync_cron.sh|#&|' | crontab -
crontab -l | grep gcal_sync
```

Resume (the line must start with */5):

```
crontab -l | sed 's|^#\(\*/5 .*gcal_sync_cron.sh\)|\1|' | crontab -
crontab -l | grep gcal_sync
```

Clean up leftover events in the test calendar only with the delete script and your approval (APR-0044).

## If the login is revoked
The job writes `~/loop1/gcal-sync/PAUSED-login-revoked`, alerts once, and exits with 3 on every run after that. To resume: renew the login (guides/calendar-gcalcli.md, Troubleshooting), run `$PY scripts/gcal/gcal_list.py --from 2026-10-26 --to 2026-10-27` to confirm it works, then `rm ~/loop1/gcal-sync/PAUSED-login-revoked`.

## Verify
1. Unit tests: `python3 -B -m unittest discover -s tests/unit -p "test_gcal*.py"` (expected: `OK`).
2. The test journal run above (steps 3 to 5).
3. `tail -n 20 ~/loop1/gcal-sync/sync.log` after the cron has run (expected: blocks every 5 minutes, `exit 0`).

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `paused: the Google login was revoked` | The pause file exists | Renew the login, remove the pause file (section above) |
| `error: cannot read the journal` (exit 4) | Wrong `--journal` path, or the CoS workspace is not there | Check the path; the default is `~/loop1/workspaces/cos/state/calendar-journal.md` |
| `error: no login file` (exit 4) | gcalcli login missing | guides/calendar-gcalcli.md |
| `another run is active; nothing to do` | A run was still working | Nothing; it was only a second run at the same time |
| A `conflict` line | The title exists in Google at another time or twice, or the entry is not valid | Look with `gcal_find.py --title "<name>"`; fix by hand with the move or delete script; the job does not retry a conflict |
| A `failed` line with `final` | 5 attempts used | Read the error in the line, fix the cause, then add a new `written` line only through the CoS |
| `alerts.log` says `logged only` | `LIFEOS_ALERT_TARGET` is not set | Put it in `~/loop1/gcal-sync/env` |

## Never paste here
Calendar IDs, channel IDs, tokens, personal event titles, personal email addresses.

## History
- 2026-10-26: job written and unit-tested (fix-70, APR-0078).
- VM test 2026-10-26 (test calendar, test journal outside the CoS workspace): unit tests OK on the system Python and on the gcalcli Python (99 tests each); dry run wrote nothing; real run created one event and appended a pushed line; a second run did nothing; a moved line plus a written line with a new title moved the same Google event (old title returned 0 events); a second written line for the same title at another time gave a conflict and Google was unchanged; a deleted line without a delete-pending-approval line was skipped; with the pending line it was skipped without --allow-deletes and executed with it; the alert test posted in the COO channel; the cron wrapper ran by hand (dry run, exit 0) and wrote sync.log. Not yet tested on the VM: five failed attempts, a revoked login. Both are covered by unit tests. See ops/install-log.md.
- Cron installed 2026-10-26 13:31 AST (every 5 minutes, test calendar, real CoS journal). First run 13:35: three events created, three pushed lines, three events in the test calendar. Run at 13:40: pushed 0, exit 0. Your other cron line (stress-ng) was kept. See ops/install-log.md.
