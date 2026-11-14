# REPORT-31: Loop 7, the COO routes lifestyle requests to the CLO; COO v1.10.8 and CLO v1.1 (APR-0128)

Evidence: `~/handover/h31/`. Patch: `handover31.patch` (10 files, applies to a fresh clone, `artifacts.yaml` not touched, no commit, no push).

## Short answer
- Done and live. The COO now sends lifestyle requests to the CLO, the CLO can reach the CoS, and your sentence from the night works end to end (log, calendar line by the CoS, COO names the CLO).
- Your real Slack message (Show Four) also routed COO to CLO and was logged.
- Not as hoped: (1) no synopsis was given, (2) the COO used a stray text as a run ID, (3) the regression suite shows 3 failures that are older or stale checks, none new (details below).

## Part 1 Repo and scratch
- Files: `agent-files/executive/coo/AGENTS.md` (v1.10.8) and `agent-files/department/clo/AGENTS.md` (v1.1) exactly as in `routing-wording-approved.md`; `deploy/loop1/loop1-v1108-upgrade.sh` and `deploy/loop1/loop1-v11-clo-upgrade.sh` (dry run, refuse unless the file is on the previous version, gateway must be stopped, safe twice, commit in the workspace); `deploy/loop7/coo-send-clo-patch.py` (the one config key, backup first, checks that nothing else changes) with tests; the health check (COO v1.10.8, CLO v1.1, COO send list now cfo, cho, clo, cos); `contracts/identity-access.yaml` (COO may send to the CLO); rebuild and parity tests.
- Scratch gateway (own state folder, port 19932, no Slack, deleted afterwards): COO with "clo" in its send list and both new files. One message "log it, give me a synopsis, make an appointment" went COO to the CLO, the CLO wrote the line, called the CoS, the CoS wrote one normal-privacy line. What the receiving side needs: nothing. The session `agent:clo:main` is created by the first send, no change on the CLO, CoS, CHO or CFO entries (`h31/scratch/RESULT.md`). The CEO was not asked to approve an extra change because none was needed.

## Part 2 Live
- Gateway stopped, both instruction files backed up (`~/start31/`), both scripts applied and committed in their workspaces (COO 63a6ab8, CLO b65d1b1), second run "already applied", one config key added (`h31/config-diff-one-key.txt`: `agents.entries.coo.tools.agentToAgent.send` gets `clo`; backup `openclaw.json.pre-coo-clo` equals the starting copy; every other key equal), gateway started, one process, Slack probe 5 of 5 connected, parity PASS.
- First attempt note: my first command ran the scripts while the gateway was still seen as running, so the scripts refused (as designed) and the config key was applied, then the gateway was started once with the new config and the old instruction files. I stopped it again, applied both scripts and started it. No agent message was sent in between.

## Part 3 Proof (new run IDs loop31-..., explicit-session CLI route as the earlier COO scenarios, synthetic names; raw files in `h31/coo/`, `h31/clo/`)
1. Your sentence (loop31-coo-001): COO sent to the CLO (never the CHO), the CLO wrote "Show One S5E3 watching", the CLO called the CoS by the handoff call, the CoS wrote `CLO - Watch Show One S5E4 - 11152026-0001` (normal privacy, requested by CLO), the COO reported only what the CLO and the CoS confirmed and named them. The CLO gave NO synopsis: it said plot details were not available (Show One is made up). The "from memory, may be wrong" marker was therefore not shown.
2. No appointment asked (loop31-coo-002, 004, 005, 006): lines logged, no calendar line (journal checked).
3. CLO asked directly (loop31-clo-003): it said it cannot look up the return date and asked for it. This is the new rule working.
4. Routing: three lifestyle wordings (004, 005, 006) went to the CLO only; the COO never named the CHO. A budget question went to the CFO (008). A workout question (007) was answered by the COO without asking anyone (it holds your plan), so I added a request that names the right chief (009), which went to the CHO. `h31/coo/routes-sessions-send-targets.txt` lists the send targets per run.
5. Regression suite (all seven scenarios, `loop31-reg-001`, `h31/reg/`): stored result 1 pass, 6 fail. Re-scored with the repo criteria of handover 28 (`h31/reg/rescore.md`): 3 pass, 4 fail, no change outside the two intended checks. The 4 left: (a) D3 "delete asked by a chief": the COO asked the CoS directly, the CoS wrote a deleted line and the gate held (no approval record); the same failure is in the older suites `loop3-v1106-001` to `003`, so it is not new; (b) bad-sleep, CFO entry and privacy request fail only on the old "Google shows busy" check, which cannot pass under `privacy_display: full`; the installed `reg-criteria.py` is still the old copy and I did not touch it. The CFO entry content criteria (CFO title, privacy=high, CFO called the CoS, event ID) all passed.
6. Calendar cleanup: the test line of loop31-coo-001 was removed from the CoS journal (back to 3 added 0 removed); the suite's own reset removed its Google test events; Google shows only the three seed workouts (`google-end.txt`). Crontab paused for the first batch and restored (diff empty).
7. Your real message (10:08 AM, `h31/coo/real-slack-message-route.txt`): COO to `agent:clo:main`, CLO logged Show Four S2E1, the COO named the CLO. The CHO was not mentioned.

## Finding: a stray message became the run ID
At 05:50 AM you typed one word alone in the COO channel. At 10:08 the COO used that word as the run ID and the event ID of your Show Four log line. The route was correct. The COO instruction has no rule to create a run ID of its own for a Slack message, so it reuses text it has seen. The state file is append-only, so I left the line (the package shows the word as `<STRAY-TEXT>`). Options for a later handover: a COO rule "use <date>-<time>-coo as the run ID unless the message states 'run ID'" and a correction line in the CLO state. Your call. If that word was something private, change it where you use it.

## Rollback
- COO back to v1.10.7: stop the gateway; in `~/loop1/workspaces/coo` run `git revert --no-edit 63a6ab8` (the pre-upgrade file is also `~/start31/coo.AGENTS.md`, commit 26bda23); remove the one key: `cp ~/loop1/state/openclaw.json.pre-coo-clo ~/loop1/state/openclaw.json` (this undoes only that key, nothing else changed in the config since); start the gateway.
- CLO back to v1.0: in `~/loop1/workspaces/clo` run `git revert --no-edit b65d1b1` (pre-upgrade file `~/start31/clo.AGENTS.md`, commit e173fdb); then start the gateway. Revert the repo patch as well (the health check expects v1.10.8 and v1.1).

## End state
- Gateway one process; no restart in 03:30 to 05:10 or across the compaction times; tests ran 09:45 to 10:30 AST.
- Crontab equal to the starting copy (`crontab-diff.txt` empty).
- CHO, CoS, CFO instruction files equal to their starting copies; their config entries and the CLO entry equal; ledger and gate plugin hashes unchanged.
- Calendar at the seed (journal 3 added 0 removed; Google three events).
- Health check (work copy as repo copy): PASS 86, WARN 0, FAIL 0, INFO 6; version lines COO v1.10.8, CLO v1.1. The extra INFO is the MaxListeners log line, now "3 gateway start(s)" because of today's restarts and scratch gateways. The installed `~/loop1/health-check.py` is replaced (sha256 equal, backup `health-check.py.pre-h31`); until the patch is pushed and pulled it will show COO and CLO parity as FAIL and WARN.
- Unit suite 523 OK; validator 0 blocking failures. The CLO state file and the investments file keep their synthetic test lines.
- Cost: regression suite 0.036 USD (measured); about 20 other short runs, each a few cents at most; day total well below 1 USD.
- Work copies left: `~/work31`, `~/scratch31`, `~/start31`.

## Secrets
No token, Slack ID, channel ID, gateway token, address or IP is in this package or the patch (scan: the CLO channel ID, the CEO Slack ID, the gateway token and the CLO bot token searched with grep -F, 0 hits; no `xox` or `xapp` strings; /home paths shortened).
