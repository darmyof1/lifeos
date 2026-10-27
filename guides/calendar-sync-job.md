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
- `deleted`: executed only with `--allow-deletes` and only after a `delete-pending-approval` line for the same event ID (APR-0044). Off by default. The cron passes `--allow-deletes` only when `GCAL_ALLOW_DELETES=1` is in `~/loop1/gcal-sync/env` (APR-0092, after the delete gate passes).
- `requested`, `pushed`, `conflict`, `moved`, `delete-pending-approval`: nothing to do.
- Before it creates anything it searches Google for the exact title (APR-0034). If the title is already there at the same time, it just records `pushed`. If it is there at another time, or twice, it appends `conflict` and touches nothing.
- If Google says the login was revoked (invalid_grant or HTTP 401), it writes the pause file, sends one alert, and does nothing more until you log in again and remove the file (S-07, APR-0043).
- A journal line marked `privacy=high` in its detail column becomes an event titled `busy` in Google, with a hidden key, never the mandated title (APR-0032, APR-0079). See "High-privacy events" below.
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

## Alerts need the gateway
`openclaw message send` goes through the gateway, which runs in terminal T1 (`source ~/loop1/env.sh; set -a; source ~/loop1/slack.env; source ~/loop1/openai.env; set +a; openclaw gateway run`). Every other shell, and the cron wrapper, loads `~/loop1/env.sh` first. If the gateway is not running, the alert fails with `Channel is unavailable: slack` and is written to `alerts.log` only (seen 2026-10-26 14:12, when T1 was down). The job itself does not depend on the gateway.

## High-privacy events (busy)
APR-0032: a high-privacy event shows in Google as busy. A journal line with `privacy=high` in its detail column (8th column) is pushed as an event titled `busy` with the time shown as busy and one hidden field that holds the journal's event ID. The mandated title never goes to Google for it. The job finds the event again by the hidden key, never by title. The mark is remembered from the job's `pushed` line and follows a move, so a forgotten mark on the new line cannot put a mandated title into Google. The CoS writes the mark from instruction set v1.9 (APR-0086): when the chief marks the entry, for every CHO and CFO entry (health and finance are high by default), or when the CEO asks. Raising privacy is supported: if the earlier Google event of the entry (through a move, or the same name marked later) is a normal one, the job turns it into a busy event (`made busy`: title busy, description and place cleared, hidden key set). The other direction, busy to normal, is not supported (APR-0086). A busy event is deleted with `gcal_delete.py --id <Google ID> --busy-key <journal event ID> --ceo-approved --approval-note ...` (no --title).

Test with fake data on the test calendar (T2, gateway not needed). Make a test journal with one high-privacy and one normal fake entry:

```
mkdir -p ~/loop1/gcal-sync-hp
printf 'name | start | end | status | run ID | event ID | requested by\nCHO - Secret test - 10282026-9201 | 2026-10-28 11:00 | 2026-10-28 12:00 | written | hp1 | hp1-01 | test | privacy=high\nCHO - Normal test - 10282026-9202 | 2026-10-28 13:00 | 2026-10-28 14:00 | written | hp1 | hp1-02 | test\n' > ~/loop1/gcal-sync-hp/journal.md
```

Then: dry run, real run, a second run, a look at Google, a move, and the delete gate. Expected: the high-privacy entry is created as `busy` (`created (busy)`), the normal one with its full title; `gcal_find.py --title "CHO - Secret test - 10282026-9201"` finds nothing; `gcal_list.py` shows `busy` at 11:00 to 12:00; Google Calendar shows a busy block; a second run does nothing; a `moved` line plus a `written` line without the mark moves the busy event and keeps it busy.

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

Clean up leftover events in the test calendar only with the delete script and your approval (APR-0044). A leftover busy event is deleted with `--busy-key` (see "High-privacy events").

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
- VM test 2026-10-26 14:12 to 15:11 AST (T2 and T1): five failed attempts (calendar ID that does not exist): attempts 1 to 5 appended, the fifth marked final, no sixth try; the alert did not reach Slack because the gateway (T1) was not running ("Channel is unavailable: slack"). After T1 was started: alert sent to the COO channel. Revoked login (a copy of the login file with a broken refresh token, the real login untouched): Google answered invalid_grant, exit 3, pause file written, one alert in the COO channel, the second run did nothing and sent no alert, nothing was written to the journal. A first attempt at this test failed because the copy was not broken and the job created one event in the test calendar; it was deleted with the CEO's approval.
- 2026-10-26: high-privacy busy events and the env.sh load in the cron wrapper added (fix-73, APR-0079). Unit-tested; to be tested on the VM.
- high-privacy test 2026-10-26 15:44 AST (fake data, test calendar, T2): dry run wrote nothing; real run created the high-privacy entry as `busy` (11:00 to 12:00) and the normal entry with its full title; a second run did nothing; the secret entry's mandated title found 0 events in Google; the journal's pushed line ended `google=<id>; privacy=high`; a `moved` line plus a `written` line without the mark moved the same busy event to the next day and kept it busy; with the delete-pending-approval lines and no flag both deletes were skipped; with `--allow-deletes` both were deleted; 116 unit tests passed on the VM. Not yet checked: how the busy block looks in the Google Calendar app.
- Scenario run loop2-scn-005 with the cron live, 2026-10-26 15:56 to 16:02 AST: before the run the cron was paused, a leftover test event was deleted (CEO approval), the state was reset and the seed lines were pushed by hand (10-28 created, 10-26 and 10-30 already in Google). After the run, the job found the old event from the journal's pushed line and moved the same Google event to 10-29 07:00 with the new title (`moved 7t343...`). Google then held 10-26, 10-29 and 10-30. The cron was resumed. See tests/scenario/bad-sleep-reschedule.md for the run and P-39 for the CHO finding.
- 2026-10-26: P-28 closed by the CEO (APR-0080). What remains before real data is in decisions/PENDING.md, P-40.
- 2026-10-26: raising privacy added (make_busy; `made busy`) and `gcal_delete.py --busy-key` (fix-82, APR-0086). Unit-tested; to be tested on the VM.
