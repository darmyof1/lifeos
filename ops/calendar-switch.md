# Calendar switch: test calendar now, real calendar later (APR-0119)

Status: the SETTING is built and tested. The real calendar is NOT authorized and NOT touched. Every authorization step below is marked
"NOT DONE, needs the CEO's go (a separate APR)".

## What the switch is
One line in the repo policy file `contracts/policy/calendar.yaml`:

    calendar_target: test        # test (default) or real

The job `scripts/gcal/gcal_sync.py` (run by the 5-minute cron line through `gcal_sync_cron.sh`) reads that line from the repo copy on the VM
every run. There is no restart. The job then picks the calendar ID by the alias:

| calendar_target | the job writes to | where the ID lives |
|---|---|---|
| `test` | the Google TEST calendar | `GCAL_CALENDAR` in `~/loop1/gcal-sync/env` (VM only, mode 600) |
| `real` | the real calendar | `GCAL_CALENDAR_REAL` in the same file (VM only, mode 600) |

- The repo holds only the alias word (test or real). A calendar ID or an address never goes into the repo, a report or a chat.
- With `real` and no `GCAL_CALENDAR_REAL` (unset or empty) the job refuses before any Google call: it prints one clear message, writes
  no journal line, makes no change. An unknown word also refuses. A missing key or a missing policy file means `test` (safe side).
- `--calendar ID` on the command line still wins over the policy (tests only).
- The second policy line, `privacy_display: busy|full`, is independent: it decides how privacy=high entries look in Google (see the comments in the file).

## Today
`calendar_target: test`. `GCAL_CALENDAR_REAL` does not exist anywhere. Proven on the VM in Loop 5: a scratch policy with `real` and no real ID
refuses (dry run and real run), and the calendar and the journal stay unchanged; the normal policy with `test` works.

## The later authorization step (NOT DONE, needs the CEO's go, a separate APR)
1. NOT DONE, needs the CEO's go: a separate APR approves using the real calendar and says which calendar.
2. NOT DONE, needs the CEO's go: the CEO opens the Google page, signs in and allows access for the VM's login (the old authorization was closed
   at the end of the real-calendar test, APR-0116). He does this himself in his browser. Nobody else signs in for him.
3. NOT DONE, needs the CEO's go: the new token is stored only on the VM (`~/.local/share/gcalcli/oauth`, mode 600, APR-0041). It is never
   sent through chat, never put in the repo, never in a report.
4. NOT DONE, needs the CEO's go: the real calendar ID is written by the CEO or by Claude Code on the VM into `~/loop1/gcal-sync/env` as
   `GCAL_CALENDAR_REAL=...` (mode 600), without printing it.
5. NOT DONE, needs the CEO's go: a first test with a synthetic entry on the real calendar, the CEO watching, then the cleanup.
6. NOT DONE, needs the CEO's go: edit the line `calendar_target: real` in the repo policy file, push, and the VM pulls (`cd ~/lifeos-ro && git pull -q`).
   The next 5-minute run writes to the real calendar.

## One-line rollback
Set `calendar_target: test` in `contracts/policy/calendar.yaml`, push, and pull on the VM. The next run writes to the test calendar again.
Events already written to the real calendar stay there; the job never deletes without the approval path (APR-0044, APR-0100).
For an immediate stop, also pause the cron line the way the suites do (`#` in front of the `gcal_sync_cron.sh` line) and restore it afterwards.

## What changes for the CEO once real is on
- Entries the CoS pushes appear on his own Google Calendar, so on his phone and everywhere he reads it.
- The agents see the real calendar's titles when they read events. With `privacy_display: busy`, privacy=high entries still show only as "busy".
- The test calendar stops receiving new entries.
- A wrong entry now sits in his real day. The checks, the approval for every delete and the privacy rules stay as they are.
