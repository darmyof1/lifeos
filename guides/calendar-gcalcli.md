# Google Calendar from the command line (gcalcli)

Status: working (read and write verified on 2026-10-15)
Last verified: 2026-10-15 on Oracle VM, Ubuntu 24.04 arm64
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

## Never paste here
The client secret, authorization codes in any URL, token files, your event titles, your calendar email address. Use `<calendar-title>` and `<client-id>` placeholders.

## History
- 2026-10-15: first working setup. Entry in ops/install-log.md.
