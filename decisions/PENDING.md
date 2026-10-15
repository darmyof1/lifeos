# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.
Resolved since the last version: P-10 (APR-0030), P-11 (APR-0031).

## P-08 — Haiku 5.5 API model ID (still open)
Needs: a probe result recorded in research/spikes/.

## P-09 — Spikes not yet run
SPK-01 to SPK-05 and SPK-07 are planned. SPK-05 is recorded as passed in conversation only. It needs a file entry before the router depends on it.

## P-12 — What may be stored in Google Calendar
Calendar events can reveal health, family, and money details. The privacy gate (APR-0007) says high-privacy data stays local.
Options:
  a) Titles only in Google Calendar; details stay local. Events with high privacy show as "busy".
  b) Full details in Google Calendar, accepting that the provider holds them.
  c) A private calendar that is not synced to Google, with a Google "busy" mirror only.
Needs: a, b, or c.

## P-13 — Who holds the Google Calendar access token
Connecting Google Calendar needs a sign-in in your browser. This is a human-gated step, like Slack.
Needs: confirm that you will do this step yourself, and that the token lives only on the VM (never in the repo).
