Check its own claims. Re-read the cited OpenClaw code lines in /srv/sandbox-input/openclaw-dist. Confirm the 3-retry claim in its P-37 findings, and mark each claim as verified or assumed.
Compare the health check. Diff deploy/loop1/health-check.py against /srv/sandbox-input/health-check.py and against the VM patch, and report any differences. Check the file for Slack IDs, IP addresses, and tokens.
Draft P-26 (Slack files:read scope). Write options with tradeoffs, and a recommended choice, marked "Needs CEO: yes". Don't change the scope or any config.
Find stale text. List every repo file that still says Loop 1 is open or refers to P-35 as open, since Loop 1 is now closed. Propose the fixes, but don't make them.
Draft a Loop 2 order. Propose the sequence of the open items and what each needs before it can start. Record decisions as new SD entries (SD-008 onward), and don't edit SD-001 to SD-007.
