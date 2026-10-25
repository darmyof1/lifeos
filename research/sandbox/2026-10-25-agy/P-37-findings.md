# P-37 Findings: OpenClaw SQLite Maintenance and Reservation Warnings

This report investigates the two log messages observed during Loop 1 runs 018 and 019:
1. `"slow agent database reservation"`
2. `"SQLite automatic maintenance activity changed before age consumption"` (logged under `"SQLite session write failed"` for operation `session.maintenance.plan`).

Based on code inspection of the OpenClaw 2026.10.5 distribution in `/srv/sandbox-input/openclaw-dist`. Every claim below is explicitly tagged as either `[VERIFIED]` (with exact file and line citation) or `[ASSUMED]`.

---

## 1. Summary of Claims and Verification Status

| Item | Origin File & Line | Event Type | Does it retry? | Verification Status |
|---|---|---|---|---|
| **Slow agent database reservation** | `openclaw-agent-write-admission-CBidmy8j.mjs:29` (also worker bundles) | Latency warning (execution $\ge$ 1000 ms) | **No** (operation completed, outcome `ok`) | `[VERIFIED]` (`openclaw-agent-write-admission-CBidmy8j.mjs:15-38`) |
| **SQLite automatic maintenance activity changed** | `session-accessor.sqlite-entry-DLM4ONjh.mjs:337` (thrown), `session-accessor.sqlite-scope-X0myq54q.mjs:145` (logged) | Concurrency conflict during background maintenance planning | **Yes**: 2 immediate retries (3 total attempts), then paused until 1000ms write-quiet backoff | `[VERIFIED]` (`session-accessor.sqlite-entry-DLM4ONjh.mjs:66-67, 419-440`) |
| **No impact on message delivery or user** | Runtime observation in runs 018 & 019 | Non-fatal background maintenance exception | Foreground writes succeed regardless of maintenance abort | `[VERIFIED]` (`deploy/loop1/STATE.md:95`, `tests/scenario/bad-sleep-reschedule.md:67`) |
| **No code changes required for Loop 2** | Architectural recommendation | Proposal to close P-37 | Closed as normal OpenClaw background retry behavior | `[ASSUMED]` (Requires CEO ratification in SD-001) |

---

## 2. "slow agent database reservation"

### 2.1 Origin and Code Citation `[VERIFIED]`
- **File**: `/srv/sandbox-input/openclaw-dist/openclaw-agent-write-admission-CBidmy8j.mjs`
- **Lines**: 10–39 (warning emitted at line 29)
- **Also bundled in**:
  - `/srv/sandbox-input/openclaw-dist/state/openclaw-state-read.worker.js:77825` `[VERIFIED]`
  - `/srv/sandbox-input/openclaw-dist/infra/sqlite-readonly-location.worker.js:72570` `[VERIFIED]`

```javascript
// openclaw-agent-write-admission-CBidmy8j.mjs:10-38
function observeWriteAdmission(operation, timing, run) {
    if (timing) return run(timing);
    const observed = {};
    const enqueuedAt = performance.now();
    const report = (outcome) => {
        if (observed.reentrant !== false || observed.startedAt === void 0 || observed.finishedAt === void 0 || observed.finishedAt - observed.startedAt < 1e3) return;
        const completedAt = performance.now();
        try {
            getChildLogger({ subsystem: "session-sqlite" }).warn({
                operation,
                outcome,
                pid: process.pid,
                threadId,
                isMainThread,
                reentrant: false,
                elapsedMs: Math.round(completedAt - enqueuedAt),
                queueWaitMs: Math.round(observed.startedAt - enqueuedAt),
                writerExecutionMs: Math.round(observed.finishedAt - observed.startedAt),
                completionDelayMs: Math.round(completedAt - observed.finishedAt)
            }, "slow agent database reservation");
        } catch {}
    };
    return run(observed).then((value) => {
        report("ok");
        return value;
    }, (error) => {
        report("error");
        throw error;
    });
}
```

### 2.2 When It Happens `[VERIFIED]`
- Line 15 checks: `observed.finishedAt - observed.startedAt < 1e3`.
- If the database write lock / execution duration is $\ge 1000\text{ ms}$ (1 second), the warning is emitted.
- In runs 018 and 019, COO database write operations around scenario start took ~1.1 to 1.2 seconds (`decisions/PENDING.md:47`).

### 2.3 Does It Retry? `[VERIFIED]`
- **No.** The `report("ok")` callback runs inside the `.then(...)` handler after `run(observed)` has successfully completed.
- The write reservation already succeeded. There is no failure and no retry.

---

## 3. "SQLite automatic maintenance activity changed before age consumption"

### 3.1 Origin and Code Citation `[VERIFIED]`
- **Error Definition**:
  - File: `/srv/sandbox-input/openclaw-dist/session-accessor.sqlite-reclamation-worker-diagnostics-1pS0sNfL.mjs:22-26` `[VERIFIED]`
- **Thrown at**:
  - File: `/srv/sandbox-input/openclaw-dist/session-accessor.sqlite-entry-DLM4ONjh.mjs:337` `[VERIFIED]`
- **Logged at**:
  - File: `/srv/sandbox-input/openclaw-dist/session-accessor.sqlite-scope-X0myq54q.mjs:142-146` `[VERIFIED]`
- **Retry logic at**:
  - File: `/srv/sandbox-input/openclaw-dist/session-accessor.sqlite-entry-DLM4ONjh.mjs:417-440` `[VERIFIED]`

```javascript
// session-accessor.sqlite-entry-DLM4ONjh.mjs:332-341
consumeReadOnlyMaintenancePlan(read, assertCurrent) {
    assertInputsCurrent();
    pending.acknowledge();
    if (owner.ageChanges.size > 0) {
        planningChanged = true;
        throw new SqliteReclamationInputsChangedError("SQLite automatic maintenance activity changed before age consumption");
    }
    assertCurrent();
    readOnlyPhase.deadline = { nextAt: read.nextAt };
}
```

```javascript
// session-accessor.sqlite-scope-X0myq54q.mjs:139-146
} catch (error) {
    outcome = "error";
    completedAt = performance.now();
    getChildLogger({ subsystem: "session-sqlite" }).warn({
        ...logFields(completedAt),
        error: truncateUtf16Safe(formatErrorMessageWithCode(error), SQLITE_SESSION_WRITE_ERROR_MAX_CHARS)
    }, "SQLite session write failed");
    throw error;
}
```

```javascript
// session-accessor.sqlite-entry-DLM4ONjh.mjs:417-440
} catch (error) {
    preservation?.dispose();
    if (planningChanged && isCurrent()) {
        if (finalized && owner.generation !== generation) {
            owner.rejections = 0;
            scheduleMaintenanceAfterWriteQuiet(databasePath, owner);
            return;
        }
        activeSessionKeys.forEach((key) => owner.activeSessionKeys.add(key));
        owner.rejections += 1;
        owner.running = false;
        owner.retryDelayMs = MAINTENANCE_WRITE_QUIET_MS;
        if (owner.rejections >= MAX_MAINTENANCE_REJECTIONS) getChildLogger({ subsystem: "session-sqlite" }).warn("SQLite automatic session maintenance paused after repeated input changes", {
            error,
            path: databasePath,
            rejections: owner.rejections
        });
        else {
            owner.running = true;
            owner.retryDelayMs = void 0;
            await runPendingMaintenance(databasePath, owner);
        }
        return;
    }
```

### 3.2 When It Happens `[VERIFIED]`
1. OpenClaw background maintenance (`session.maintenance.plan`) runs to reclaim space, prune expired entries, and compute session age snapshots.
2. Concurrent foreground session writes (such as incoming scenario messages from the CEO) trigger `observeSessionEntryMaintenanceAgeChanges` (`session-accessor.sqlite-entry-DLM4ONjh.mjs:137-143`), populating `owner.ageChanges`.
3. In `consumeReadOnlyMaintenancePlan` (line 335), OpenClaw verifies whether `owner.ageChanges.size > 0`.
4. If writes occurred while planning was computing, the planned maintenance actions are stale. OpenClaw sets `planningChanged = true` and throws `SqliteReclamationInputsChangedError`.
5. `runExclusiveSqliteSessionWrite` catches the error, logs `"SQLite session write failed"`, and re-throws to `runPendingMaintenance`.

### 3.3 Confirmation of the Retry Count Mechanism `[VERIFIED]`
Re-reading lines 66–67 and 419–440 confirms the exact retry mechanics:
- Constant definition: `const MAX_MAINTENANCE_REJECTIONS = 3;` (line 67).
- Constant definition: `const MAINTENANCE_WRITE_QUIET_MS = 1e3;` (1000 ms, line 66).
- When `planningChanged` occurs:
  1. `owner.rejections += 1` (line 426).
  2. If `owner.rejections < 3` (rejections 1 and 2):
     - Takes `else` branch (lines 434–438).
     - Sets `owner.running = true` and `owner.retryDelayMs = void 0`.
     - Executes `await runPendingMaintenance(databasePath, owner);`.
     - **Result**: Exactly **2 immediate retries** (for a total of 3 attempts: initial attempt + 2 immediate retries).
  3. If `owner.rejections >= 3` (rejection 3):
     - Takes `if` branch (lines 429–433).
     - Logs: `"SQLite automatic session maintenance paused after repeated input changes"`.
     - Leaves `owner.running = false` and `owner.retryDelayMs = 1000` ms. Does NOT immediately retry.
  4. Subsequent write quiet timer:
     - When subsequent writes finish via `kickSessionEntryMaintenanceAfterWrite` (lines 88–91):
       `if (owner.rejections >= MAX_MAINTENANCE_REJECTIONS) owner.rejections = 0; scheduleMaintenanceAfterWriteQuiet(databasePath, owner);`
     - Once writes stop for $\ge 1000$ ms, maintenance executes quietly and succeeds.

---

## 4. Assessment and Conclusion `[VERIFIED]`

- **Contention vs. Retrying Normally**:
  `[VERIFIED]` from code: This is OpenClaw's intentional optimistic concurrency control protecting database consistency.
- **Safety**:
  `[VERIFIED]` from logs (`deploy/loop1/STATE.md:95`, `tests/scenario/bad-sleep-reschedule.md:67`): No user or agent messages were dropped or delayed.
- **Action for Loop 2**:
  `[ASSUMED]` (Proposed in SD-001): No code changes or configuration tweaks required. Close P-37.
