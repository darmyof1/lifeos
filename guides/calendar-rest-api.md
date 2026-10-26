# Google Calendar REST scripts - guide

Status: working (run from the repo on the VM on 2026-10-25: unit tests, list, find and the round trip, which creates, moves, reads and deletes one event by ID. The create, move, get and delete scripts have been run on the VM only inside the round trip; each is unit-tested.)
Last verified: 2026-10-25 on Oracle VM, Ubuntu 24.04 arm64
Tool version: Python 3.12 from the gcalcli pipx environment (the Google libraries come with gcalcli 4.5.1). google-api-python-client 2.201.0 (recorded 2026-10-25 with the command in Verify).
Owner: CEO

## What this is for
gcalcli 4.5.1 cannot move or delete an event by its Google ID: `delete` and `edit` take search text, and `edit` is interactive (checked 2026-10-25). P-28 needs ID-based moves and deletes. APR-0074 sends those through the Google Calendar REST API, using the same login gcalcli already holds. Each scenario has its own script in `scripts/gcal/`. gcalcli stays installed and documented for reads and as a fallback (guides/calendar-gcalcli.md).

## Before you start (HUMAN)
1. gcalcli works: `gcalcli list` shows your calendars (guides/calendar-gcalcli.md). The OAuth app must be In production; in Testing mode Google expires the login after 7 days.
2. The login file is `~/.local/share/gcalcli/oauth`, mode 600 (APR-0041). The scripts only read it. They never copy or print it.
3. Your calendar email is never written in the repo. Set it for the shell: `export GCAL_CALENDAR="<calendar-email>"` (or pass `--calendar`).

## Where to run
On the VM as `ubuntu`, from the read-only clone. The gcalcli Python has the Google libraries; the system Python does not.
```
cd ~/lifeos-ro && git pull
PY=~/.local/share/pipx/venvs/gcalcli/bin/python
```
Every command below is `$PY scripts/gcal/<script>.py ...`. Times are local (America/Santo_Domingo) and written without an offset, for example `2026-10-26T07:00`. Every write script has `--dry-run`: run it first.

## Scenarios
| Script | Scenario | Writes? |
|---|---|---|
| gcal_list.py | List events in a date range with their IDs | no |
| gcal_find.py | Find events by exact title (the check before a retry) | no |
| gcal_get.py | Show one event by ID | no |
| gcal_create.py | Create one event and print its ID | yes |
| gcal_move.py | Move one event by ID | yes |
| gcal_delete.py | Delete one event by ID (needs the CEO's approval) | yes |
| gcal_roundtrip_test.py | Create, move, read and delete one test event | yes |

Output of the read scripts is one tab-separated line per event: ID, start, end, title. The count goes to stderr (`events: N`). The end date of a range is not included.

1. List
   `$PY scripts/gcal/gcal_list.py --from 2026-10-25 --to 2026-10-27`
2. Find by exact title
   `$PY scripts/gcal/gcal_find.py --title "CHO - Doctor Appointment - 10262026-0001"`
   No line means no match.
3. Show by ID
   `$PY scripts/gcal/gcal_get.py --id <event-id>`
4. Create (dry run first, then the same command without `--dry-run`)
   `$PY scripts/gcal/gcal_create.py --title "COS - Test - 10272026-0001" --start 2026-10-27T09:00 --minutes 30 --dry-run`
   Expected: `dry-run create`, then start, end and title. The real run prints `created` and the new ID.
5. Move (the length stays the same unless `--minutes` is given)
   `$PY scripts/gcal/gcal_move.py --id <event-id> --start 2026-10-27T09:30 --dry-run`
   Moving to another day also needs `--new-title` with the new date, because the title carries the event date (APR-0035).
6. Delete (only after the CEO approves, APR-0044)
   `$PY scripts/gcal/gcal_delete.py --id <event-id> --title "<exact current title>" --ceo-approved --approval-note "<where the CEO said yes>" --dry-run`
   Remove `--dry-run` to delete. Expected: `deleted`, the ID, the title and the approval note.
7. Round trip on a test event (it deletes its own event, so it needs the approval flag)
   `$PY scripts/gcal/gcal_roundtrip_test.py --date 2026-10-26 --ceo-approved`
   Run it with `--dry-run` first. Expected output is in Verify, step 4.

## What the scripts refuse
- A title that does not follow `<DOMAIN> - <Title> - <MMDDYYYY>-<NNNN>`, or whose date is not the start date (APR-0034, APR-0035, APR-0037).
- A second event with the same title (no duplicates).
- Any event that is not a LifeOS event: move and delete only touch events with a mandated title, so your personal events are never changed. Recurring and all-day events are refused too.
- A delete without `--ceo-approved` and `--approval-note`, or with a title that does not match the event with that ID.
- A login file that is not a regular file owned by you, or is readable by others.
- Anything beyond title, start and end: nothing else is sent to Google (APR-0032).
Test events use counters from 9001 up (for example `COS - REST API test - 10262026-9001`), so they never collide with the counters the CoS assigns.

## Verify
1. Unit tests, from the repo root, no Google needed (expected: `OK`):
   `python3 -B -m unittest discover -s tests/unit -p "test_gcal*.py"`
   With the gcalcli Python the same command also runs a request-shape check with the real Google client.
2. Record the library version (expected: a version number):
   `pipx runpip gcalcli show google-api-python-client | head -2`
3. Read test: `$PY scripts/gcal/gcal_list.py --from 2026-10-25 --to 2026-10-27`
   Expected: the same events as `gcalcli agenda`, with their IDs.
4. Round trip on one test event (it deletes its own event, so the CEO approves with the flag):
   `$PY scripts/gcal/gcal_roundtrip_test.py --date 2026-10-26 --dry-run`
   then the same command with `--ceo-approved` instead of `--dry-run`.
   Expected: four lines: `1 created: <id>`, `2 moved to: ...T07:30:00-04:00`, `3 read by id: True ...`, `4 deleted by id: <id>`.
5. Check that nothing is left: `gcalcli agenda 2026-10-26 2026-10-27`

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80` when reading the login file | The login file is a Python pickle, not JSON (seen 2026-10-25) | Use the repo scripts, which read it correctly. Never load it as JSON |
| `invalid_grant: Token has been expired or revoked` | The login expired or was revoked. Likely cause on 2026-10-25: the OAuth app was in Testing mode, where logins expire after 7 days | Publish the app (Audience, Publish app), delete `~/.local/share/gcalcli/oauth`, run `gcalcli --client-id=<client-id> init` again (guides/calendar-gcalcli.md) |
| `error: the Google libraries are missing` | The system Python was used | Run with `~/.local/share/pipx/venvs/gcalcli/bin/python` |
| `error: the login file is readable by others` | `gcalcli init` left the new login file open to others (seen 2026-10-25 after the third login) | `chmod 600 ~/.local/share/gcalcli/oauth`, then `stat -c "%a %U %n" ~/.local/share/gcalcli/oauth` must show `600 ubuntu` |

## Never paste here
Calendar email addresses, event IDs from your real calendar, personal event titles, tokens, client secrets, authorization codes.

## History
- 2026-10-25: REST read, create, move, read by ID and delete by ID verified with an ad hoc script after the gcalcli login was renewed (ops/install-log.md). APR-0074 decides: moves and deletes by ID use REST; gcalcli stays. Repo scripts added in fix-65.
- 2026-10-25: repo scripts run on the VM: 59 unit tests OK, list (2 events with IDs), find (0 matches after cleanup) and the round trip (create, move, read by ID, delete by ID) passed, with nothing left on the calendar. See ops/install-log.md.
