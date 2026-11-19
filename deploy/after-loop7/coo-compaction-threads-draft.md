# COO morning compaction and Slack thread sessions (DRAFT, waiting for the CEO's approval; nothing is approved here)

Why: the 05:25 compaction (scripts/ops/coo-compact.sh, APR-0121) picks the COO's Slack channel session by key prefix "agent:coo:slack:channel:" and refuses unless it finds exactly one. Since the CEO's Slack thread of 2026-11-17, the thread has its own session whose key starts with the same prefix (it ends with ":thread:<timestamp>"). The script now finds two, logs "error (COO channel sessions found: 2 (need exactly 1))" and compacts nothing. It has done so twice (read-only check, handover 34), and the health check shows WARN 1. The channel session keeps growing, which is what the compaction was built to stop (APR-0116 and APR-0121).

## Option A (recommended): leave thread sessions alone
Change one thing in scripts/ops/coo-compact.sh: the channel session is the one key that starts with "agent:coo:slack:channel:" and does NOT contain ":thread:". Everything else stays: the 03:30 to 05:10 refusal window, the 10-minute skip, the waiting-request skip, one log line per run, no message text in the log. "Exactly one" still applies to channel sessions, so two real channels would still be an error.
- Thread sessions are not compacted. They are small and short-lived, so this is acceptable. If a thread session grows large, a later change can add it.
- Live change: replace the installed script with the repo copy (backup first, sha256 equal). No cron, config, plugin or agent-file change. The 05:25 cron line stays.
- Tests: add to tests/unit/test_coo_compact.py one channel session plus one thread session (the channel one is compacted and the thread one is not touched), and keep the "two channel sessions is an error" test. Synthetic session lists only.
- The next real compaction at 05:25 AST is then the proof. Handover reads the log line after it, and nothing is run inside 03:30 to 05:10.

## Option B: compact the thread sessions too
The script would compact the channel session and then each thread session of the COO. More code, more ways to fail, and the "waiting request" and "recent message" rules would have to be applied to each session. Not recommended now.

## Option C: leave it
The error stays, the WARN stays, and the COO's channel session is never compacted.

## What stays the same
No agent instruction change, no config change, no crontab change. The session key and tokens are never written to the log.

## Question
Reply "A", "B" or "C", or tell me the changes. Approval would be recorded as the next APR in your words, with a numbered handover to follow.
