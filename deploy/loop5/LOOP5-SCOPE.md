# Loop 5 scope: calendar privacy toggle, privacy gate in shadow mode, real-calendar setting (not authorized)

Approved by APR-0119 (CEO, 2026-11-08). Synthetic data and the Google TEST calendar only. The real calendar is NOT authorized and NOT touched in this loop.

## Plain-language summary
1. A switch in one YAML line chooses how private entries look in Google: "busy" (as today) or "full" (real titles). Flipping it retitles the events already in Google, in either direction.
2. The privacy gate is turned on in SHADOW mode on the live system: it labels every model turn and logs what it WOULD block, but blocks nothing and never stops a turn, even when it errors. After some days of normal use the CEO sees real numbers and decides separately whether to enforce.
3. A second YAML line, calendar_target, names which calendar the job writes to: "test" (today) or "real". The "real" side is only a setting that refuses to run until a real calendar ID and Google permission exist. Nothing is authorized, no real ID is entered, nothing is tested on the real calendar.

## What is built
1. `contracts/policy/calendar.yaml`: new keys `privacy_display: busy` and `calendar_target: test` (the repo copy is what the job reads; flipping a key means editing the line, pushing, and the VM pulling). `scripts/gcal/gcal_sync.py` and `gcal_busy.py` apply the mode to entries marked privacy=high: in full mode they go to Google as normal events with their real title and the hidden key; a mode change reconciles the events already in Google (busy to full: the title is restored from the journal; full to busy: the event becomes a busy event, as for a raised privacy). Default and any unreadable or unknown value mean busy (safe side). A command-line option `--privacy-display` overrides the file for tests.
2. `deploy/loop3/gate-plugin/`: a `mode` setting (shadow or enforce; shadow is the default and the only mode installed live). In shadow the plugin never blocks, fails open on any error (and logs the error), and writes labels, decision, would_block, agent, channel and trigger kind to its own log (never the text, hashes only). `scripts/ops/gate-shadow-report.py` summarizes the log (counts by label, would-block by agent, channel and trigger kind, per day).
3. `calendar_target`: the job picks the calendar ID from its settings file on the VM by this alias (GCAL_CALENDAR for test, GCAL_CALENDAR_REAL for real); with target real and no real ID it refuses and writes nothing. `ops/calendar-switch.md` lists the steps for the later authorization (not done now).
4. Health-check lines: the gate plugin loaded in shadow mode; calendar_target and privacy_display values shown (INFO).

## Pass criteria
- Toggle: on the test calendar, a high-privacy entry shows as busy; flipping to full retitles it to its real title; flipping back makes it busy again; no event is recreated, no duplicate, no test event left; the journal is unchanged; move, delete (with approval) and the delete gate still work in both modes.
- Shadow gate: live in shadow mode; a normal COO, CHO, CoS and CFO exchange still works; the log has labels and would-block lines and no text; a forced error inside the plugin does not stop a turn; the report script runs.
- Real-calendar setting: target real without a real ID refuses and changes nothing; no real calendar ID, token or authorization exists anywhere; the cron still writes to the test calendar.
- The crontab, agent instructions and the delete-gate plugin are unchanged; tests and validator pass; health check PASS count does not drop.

## Not in this loop
Authorizing or testing the real calendar; enforcing the gate; a local model or GPU; other chiefs; isolation; the second-human test; the CFO difference; COO session compaction.
