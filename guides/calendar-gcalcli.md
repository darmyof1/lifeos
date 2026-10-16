# Google Calendar from the command line (gcalcli)

Status: working (read and write verified on 2026-10-15)
Last verified: 2026-10-16 on Oracle VM, Ubuntu 24.04 arm64 (commands below)
Tool version: gcalcli 4.5.1, installed with pipx. Do NOT use the Ubuntu apt package (4.3.0): it has no `init` command.
Owner: CEO

## What this is for
Lets the CoS read and write your Google Calendar from the VM (APR-0030, APR-0031). Read works now. Writing works on your primary calendar.

## Before you start (HUMAN)
1. A Google account whose calendar you use.
2. A Google Cloud project (name it `gcalcli`).
3. Enable the Google Calendar API for that project.
4. Configure the OAuth consent screen: user type External, your own email as developer contact, and your own email added as a test user.
5. Create an OAuth client of type **Desktop app**. Google shows a Client ID and a Client Secret.
6. Store the Client ID and Client Secret in your password manager. Never in the repo, never in a chat.
7. If a secret was ever pasted in a chat or committed, reset it in Google Cloud (Clients → your client → reset secret) before using it.

## Install
1. `sudo apt update && sudo apt install -y pipx python3-venv`
2. `pipx ensurepath`
3. `export PATH="$HOME/.local/bin:$PATH"`
   Make it permanent: `grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`
4. `pipx install gcalcli`
5. `hash -r && command -v gcalcli`
   Expected: `/home/ubuntu/.local/bin/gcalcli`
6. `gcalcli --version`
   Expected: `gcalcli 4.5.1` (or later).

If step 5 shows `/usr/bin/gcalcli`, the old apt package is still installed: `sudo apt remove -y gcalcli`, then `hash -r` and repeat step 5.

## Authenticate
1. (HUMAN) `gcalcli --client-id="<your-client-id>" init`
   Paste the client secret when asked.
2. The command prints a Google URL that ends in a `redirect_uri` of `http://localhost:<PORT>/`. Note the PORT. It changes every run.
3. The VM has no browser, and your browser is on the Mac. Open a second terminal on the Mac and forward the port:
   `ssh -L <PORT>:127.0.0.1:<PORT> ubuntu@<vm-host>`
   Keep it open.
4. (HUMAN) Open the printed URL in your Mac browser. Approve the calendar permission. If Google warns that the app is unverified, use Advanced and continue, since this is your own app.
5. Expected in the VM terminal: `Successfully loaded credentials`.

## Verify
1. `gcalcli list`
   Expected: your calendars, with access levels. Copy the exact title of the calendar you want to use.
2. `gcalcli agenda today tomorrow`
   Expected: your events, or `No Events Found...`.
3. Write test (use the exact title from step 1):
   `gcalcli --calendar "<calendar-title>" add --title "LifeOS write test" --when "tomorrow 17:00" --duration 15 --noprompt`
   Expected: no output on success.
4. `gcalcli --calendar "<calendar-title>" agenda today tomorrow`
   Expected: the test event listed at 17:00.
5. Delete the test event in the Google Calendar web app.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `invalid choice: 'init'` | The apt package 4.3.0 is the one being run | Remove it (`sudo apt remove -y gcalcli`), `hash -r`, use the pipx version |
| `No available calendar to use` | `--calendar` text does not match a calendar title | Run `gcalcli list` and copy the title exactly |
| `invalid get_time_from_str value: '+7'` | That relative end date is not accepted | Use `today tomorrow` or explicit dates |
| Browser cannot open the redirect | The listener runs on the VM, the browser on the Mac | SSH tunnel with the PORT from the URL (step 3 above) |
| Init stops with Ctrl+C | Authorization not completed | Run init again; a new URL and port are issued |
| `Cannot access ~/.gcalcli_oauth` | Not initialized yet | Run init |
| `--noauth_local_webserver` rejected | Not accepted by 4.5.1 init | Do not use it; use the SSH tunnel |

## Naming every event (mandate APR-0034, details APR-0035)
Format: <DOMAIN> - <Title> - <MMDDYYYY>-<NNNN>
Example: CHO - Doctor Appointment - 10202026-0001 (October 20, 2026, event 0001 of that date)
- DOMAIN: CHO (Health), CSP (Spirituality), CDO (Development), CFO (Finance), CFA (Family), CLO (Lifestyle), CSO (Social), CCO (Career). COO (Operations) or COS (Staff) for events that belong to no domain. APR-0037.
- MMDDYYYY: the event date, month first.
- NNNN: a four-digit counter that restarts at 0001 for each date. The CoS assigns it.
- Only the CoS creates calendar events (APR-0030).

## Create an event
Replace the placeholders. <calendar-email> is the email of the calendar you use (shown by "gcalcli list").
   gcalcli --calendar "<calendar-email>" add --title "CHO - Doctor Appointment - 10172026-0001" --when "tomorrow 07:00" --duration "30" --noprompt
Expected: no output on success (the add command only shows a prompt when --noprompt is missing). Confirm with the search below, then check the event in the Google Calendar web app.

## Find an event
Search by full title. Only events with that title match:
   gcalcli --calendar "<calendar-email>" search "CHO - Doctor Appointment - 10172026-0001"

Search by title and date range. The end date is excluded, so to include October 17 end on October 18:
   gcalcli --calendar "<calendar-email>" search "CHO - Doctor Appointment - 10172026-0001" 2026-10-16 2026-10-18

Agenda for a date range (same end-date rule):
   gcalcli --calendar "<calendar-email>" agenda 2026-10-16 2026-10-18

Show the Google event ID. For reading only: delete cannot use it (see below).
   gcalcli --calendar "<calendar-email>" search "CHO - Doctor Appointment - 10172026-0001" --details id --tsv
The column layout of this output has not been checked on your machine.

## Delete an event
Delete by ID is not possible with gcalcli 4.5.1. The delete command takes search text, not an ID, and --noprompt is not an option for delete (checked in the gcalcli 4.5.1 source and by running it: "unrecognized arguments: --noprompt"). Delete by the full title instead. Names follow the mandate, so the title is unique.

1. Search by the full title. Expected: one line.
   gcalcli --calendar "<calendar-email>" search "CHO - Doctor Appointment - 10172026-0001"
2. Delete:
   gcalcli --calendar "<calendar-email>" delete --iamaexpert "CHO - Doctor Appointment - 10172026-0001"
   Expected: the event line, then "Deleted!" (seen on 2026-10-16).
3. Search again. Expected: no matching events.

Warnings:
- --iamaexpert deletes every event the text matches, with no prompt. Always search first. Use the full title. A short text such as "Doctor" matches many events.
- Without --iamaexpert, delete asks "Delete? [N]o [y]es [q]uit" for each match.
- Calendar emails and event IDs are not pasted in the repo. Use <calendar-email>.

## Never paste here
The client secret, authorization codes in any URL, token files, your event titles, your calendar email address. Use `<calendar-title>` and `<client-id>` placeholders.

## History
- 2026-10-15: first working setup. Entry in ops/install-log.md.
- 2026-10-16: naming standard (APR-0034, APR-0035). Create, search, date-range search, agenda and delete by title tested (ops/install-log.md). Delete by ID was tested and rejected; an earlier note saying a test event was removed by ID was wrong and is removed.
