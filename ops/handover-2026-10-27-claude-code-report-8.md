# Report 8 - Loop 3 step 1: rebuildable repo, parity check, regression suite (APR-0097), 2026-10-27

## 1. 05:00 report fix (fix-94)
- Installed deploy/loop2/vm/daily-reset-report.py and .sh to ~/loop1/ (old copies kept as .pre-fix94). The cron line is unchanged. The wrapper's dry run printed "Gateway: 1 process (OK), up 19h46m" (hours and minutes, not "unknown"). The dry run wrote no snapshot or log.

## 2. Mirrored agent files (~/handover/agent-files/, SHA256SUMS with repo paths)
- Copied 13 of 16 files, byte for byte, workspace git HEADs: coo 89d43c9, cos 918b843, cho 0b18245, cfo c5dd57e (no uncommitted changes in any of the 16 files).
- Sizes in bytes: coo AGENTS.md 5614, SOUL.md 76, IDENTITY.md 85, USER.md 345; cos SOUL.md 71, IDENTITY.md 74, USER.md 345; cho SOUL.md 82, IDENTITY.md 78, USER.md 345; cfo SOUL.md 73, IDENTITY.md 82, USER.md 345.
- NOT copied (limit 5): cos/AGENTS.md (8305 bytes), cho/AGENTS.md (4525), cfo/AGENTS.md (3659). Each holds a Slack channel ID in its "Own-channel post" rule: cos/AGENTS.md line 34, cho/AGENTS.md line 28, cfo/AGENTS.md line 25. The ID is written into the live files by loop1-v13-upgrade.sh from the VM-only file ~/loop1/slack-channels.env.
- No other file in the four workspace tops (there are only these four .md files per agent). No token, calendar ID or VM address in any copied file.

## 3. Rebuild from the repo scripts (throwaway HOME)
- Order: loop1-agent-files.sh (v1.2 baseline), then v13, v14, v15, v16, v17, v18, v19, v191, v110, v1101, v1102, v1103; with a stub pgrep and a copy of slack-channels.env in the throwaway HOME.
- Result: all 16 files (4 per agent) match the live files byte for byte (cmp). The repo scripts can rebuild every agent file, but only with ~/loop1/slack-channels.env (VM-only, holds the three channel IDs). The repo parity check cannot hold the three AGENTS.md copies that contain an ID unless the CEO decides to keep the IDs in the repo or to move them behind a placeholder.

## 4. Parity check
- health-check.py (live ~/loop1/health-check.py and ~/handover/): 16 new checks, "parity <agent>/<file> (live = repo agent-files/<path>)": PASS when sha256 equal, FAIL when different, WARN when the repo copy is missing or empty. Logic tested on a PASS and a FAIL case (I briefly replaced two tracked empty placeholder files in ~/lifeos-ro/agent-files and restored them with git checkout; the repo is clean).
- Output (health-check-output.txt, 2026-10-27 21:5x): PASS 54, WARN 16, FAIL 0, INFO 4. The 16 WARNs are the empty repo copies.

## 5. Regression suite
- ~/handover/regression-suite.sh (installed in ~/loop1/ with reg-criteria.py and run-cost.py). Options --only N, --dry-run; refuses to start if it would run into 02:30 to 05:10 AST (tested); trap resumes the cron; Slack start and end lines per run; closing reset; one result file per run and regression/<SUITE>.md. The job step is the cron wrapper by hand.
- Baseline loop3-reg-001 (21:30 to 21:49 AST): 5 pass, 2 fail, total cost 0.0455 USD (measured), each run under 0.011 USD.
  1. -01 bad-sleep: FAIL (6 pass, 4 fail). The sessions_send checker failed on SESSION_WORK_START_CHANGED (the known P-35, 2 results). The CHO's move was written twice (the journal holds moved and written twice: numstat 5 0 before the job). The runner correctly did not run the job, so the busy event, numstat 6 0 and the later checks failed too. Real failure; not a script error.
  2. -02 D1: PASS (7 of 7). 3. -03 D2: PASS (9 of 9, seven items in order). 4. -04 D3: PASS (7 of 7, pending only). 5. -05 CFO entry: PASS (7 of 7, CFO called the CoS itself). 7. -07 privacy: PASS (7 of 7).
  6. -06 overlap: FAIL (8 pass, 1 fail). The conflict line and the later written line were right and the job created the event, but the COO's first reply did not offer the 08:00 to 09:00 slot (it said only that the CoS logged a conflict). In loop2-scn-023 the COO did offer it. Real failure, flaky.
- No instruction was changed to make a run pass. The failed runs' evidence is in regression/loop3-reg-001/.

## For the CEO to decide
1. Slack channel IDs in three AGENTS.md files: keep them out of the repo (the repo parity check stays WARN for those three) or approve a placeholder scheme so the repo can hold those files.
2. Two baseline failures to look at in Loop 3: the bad-sleep duplicate write after a P-35 acknowledgement failure (-01), and the COO not offering the free slot (-06). Proposed text only on request.
3. Record an APR for the 05:00 report fix, the parity check and the regression suite.

## End state (21:55 AST)
Gateway active, one process. Cron */5 on the test calendar (stress-ng and 05:00 lines kept), GCAL_ALLOW_DELETES=1. Google holds only the three seed events. State reset to the seed, seeds pushed (3 0). Last agent message and compaction at about 21:50 AST (loop3-reg-001-99-final).

## Files in ~/handover/
agent-files/ (13 files and SHA256SUMS), health-check.py, health-check-output.txt, regression-suite.sh, reg-criteria.py, run-cost.py, regression/loop3-reg-001.md and regression/loop3-reg-001/ (7 result files), daily-reset-report.py and .sh (from the repo, installed), REPORT-8.md.
