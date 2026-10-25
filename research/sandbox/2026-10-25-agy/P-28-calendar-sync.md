# P-28 Design: Calendar Journal to Google Calendar Synchronization

**Document**: `sandbox/P-28-calendar-sync.md`  
**Status**: Proposal (Draft)  
**Governing Approvals**:  
- APR-0030 (CoS sole writer of calendar entries)  
- APR-0031 (Google Calendar is calendar of record)  
- APR-0032 (Titles only in Google; details kept local)  
- APR-0034 / APR-0035 / APR-0037 (Event naming standard `<DOMAIN> - <Title> - <MMDDYYYY>-<NNNN>`)  
- APR-0054 (Local append-only calendar journal kept by CoS)  
- APR-0057 (Calendar move is not a delete; two-line append rule)  
- APR-0058 (Instruction set v1.2: journal lines never edited or deleted in place)  
- ADR-0008 / ADR-0011 (Sync and retries execute in deterministic code, not in the LLM model)  
**Verification Standard**: Every factual claim cites file and line or command output, or is labeled "not verified".

---

## 1. Overview and Core Invariants

In Loop 1, the Chief of Staff (CoS) managed all calendar operations in a local journal file (`~/loop1/workspaces/cos/state/calendar-journal.md`) without pushing to Google Calendar (APR-0054, `decisions/APPROVALS.md#L431-L441`).

For Loop 2 (P-28, `decisions/PENDING.md#L21-L27`), LifeOS establishes synchronization between the CoS journal and Google Calendar under the following core invariants:
1. **Google Calendar is the Store of Record** (APR-0031, `decisions/APPROVALS.md#L201-L207`): Google Calendar holds the actual schedule viewed by the CEO.
2. **CoS Journal is the Hold and Audit Trail** (APR-0054): Every calendar intent originated by agents or the CEO is recorded in the CoS workspace before contacting external APIs.
3. **Strict Append-Only Invariant** (APR-0054, APR-0058, `deploy/loop1/health-check.py#L177-L179`): No line in `calendar-journal.md` is ever modified or deleted in place. All state progressions (including moves, pushes, and retries) append new lines.
4. **Deterministic Code, Not LLM Model** (ADR-0008, ADR-0011, `decisions/PENDING.md#L25`): Syncing, searching for duplicates, and retrying API calls execute in a Python background service (`calendar-sync`), never inside an LLM turn.
5. **Privacy Gate (Titles Only)** (APR-0032, `contracts/policy/calendar.yaml#L8-L11`): Only event title, start time, and end time are pushed to Google Calendar. Details, locations, attendees, and health/family notes remain local in agent state. High-privacy entries appear in Google as "busy".

---

## 2. Journal Schema and Status Lifecycle

### 2.1 File Location and Format
- **Path**: `~/loop2/workspaces/cos/state/calendar-journal.md` (never committed to git repo; tracked in CoS workspace git).
- **Format**: Pipe-delimited Markdown table. Each entry is a single line appended to the table:

```markdown
| Timestamp | Event ID | Run ID | Domain | Action | Title | Start | End | Status | Attempt | Google Event ID | Details Ref |
```

### 2.2 Status Set for Loop 2
As proposed in `decisions/PENDING.md#L25`:

| Status | Meaning | Set By |
|---|---|---|
| `requested` | Calendar change requested by an agent (e.g. CHO) or CEO | CoS (agent turn) |
| `written` | CoS verified validity, assigned Event ID, and wrote local journal | CoS (agent turn) |
| `pushed` | Event successfully created or verified in Google Calendar | Sync Runner (code) |
| `failed` | API push failed after attempt (carries attempt count & error) | Sync Runner (code) |
| `conflict` | Scheduling conflict detected in Google Calendar or local state | CoS or Sync Runner |
| `moved` | Entry superseded by a new time/date (cites replacement Event ID) | CoS (agent turn) |
| `delete-pending-approval` | Removal requested with no replacement; awaiting CEO decision | CoS (agent turn) |
| `deleted` | CEO approved deletion; event removed from Google Calendar | Sync Runner (code) |

---

## 3. Move and Delete Workflows (APR-0057 & APR-0044)

### 3.1 The Move Workflow (APR-0057)
Under APR-0057 (`decisions/APPROVALS.md#L463-L473`), moving an event is **not** a delete and does **not** require CEO approval:
1. When a reschedule is ordered (e.g. moving a workout from 07:00 to 08:30):
   - CoS appends line 1: Old Event ID marked with status `moved`, referencing the new Event ID.
   - CoS appends line 2: New Event ID marked with status `written` with new start/end times.
2. The health check verifies that line count increased by 2 with 0 deleted lines (`git diff --numstat` shows `2 0`, verified in `deploy/loop1/STATE.md#L67`).
3. The Sync Runner reads the journal:
   - For the `moved` line: Calls Google Calendar API to delete or update the old event.
   - For the `written` line: Calls Google Calendar API to insert the new event.
   - Appends two `pushed` confirmation lines with respective Google event IDs.

### 3.2 The Delete Workflow (APR-0044)
Under APR-0044 (`decisions/APPROVALS.md#L470`), removing an event without replacement is a deletion and **must** have CEO approval:
1. CoS appends a line with status `delete-pending-approval` and reports the request to the CEO via the COO.
2. The CEO sends explicit approval in Slack.
3. CoS receives confirmation and appends a line with status `deleted`.
4. Sync Runner removes the event from Google Calendar and appends a `pushed` confirmation line.

---

## 4. Sync Engine Architecture (`calendar-sync.py`)

A background daemon/timer (Python 3, standard library + Google API / `gcalcli` wrapper) runs every 5 minutes (S-06, `decisions/PENDING.md#L22`).

```
+-----------------------------------------------------------------------------------+
| CoS Agent (OpenClaw)                                                              |
|   Appends new row to calendar-journal.md (status: written / moved)                |
+-----------------------------------------------------------------------------------+
                                    |
                             (File append)
                                    v
+-----------------------------------------------------------------------------------+
| Calendar Sync Daemon (Every 5 min - S-06)                                         |
| 1. Reads active calendar-journal.md                                               |
| 2. Reconstructs state machine per Event ID                                        |
| 3. Filters entries requiring action (written, failed, moved, deleted)             |
| 4. Idempotency Check: Queries Google Calendar for unique APR-0034 event name      |
| 5. Executes API call (Create / Move / Delete)                                     |
| 6. Appends result row to calendar-journal.md (pushed or failed)                   |
+-----------------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            | (Success)                                     | (Failure)
            v                                               v
+-------------------------------+               +-------------------------------+
| Append 'pushed' with GCal ID  |               | Increment attempt count       |
+-------------------------------+               | If attempts >= 5:             |
                                                |  - Alert COO / CEO            |
                                                | If token revoked (S-07):      |
                                                |  - Pause all sync             |
                                                |  - Alert CIO in #cio          |
                                                +-------------------------------+
```

### 4.1 Idempotency and Duplicate Prevention (APR-0034)
To ensure network interruptions do not cause duplicate Google Calendar events:
1. Every event has a strictly unique APR-0034 title (`contracts/policy/calendar.yaml#L12-L22`):  
   Format: `<DOMAIN> - <Title> - <MMDDYYYY>-<NNNN>` (e.g. `CHO - Doctor Appointment - 10202026-0001`).
2. Before calling `gcal.events().insert(...)`, the Sync Runner calls `gcal.events().list(q="CHO - Doctor Appointment - 10202026-0001")`.
3. If the event exists in Google Calendar:
   - The write succeeded in a prior attempt but the acknowledgement was dropped.
   - Sync runner captures the existing `id` and appends `pushed` to the journal without creating a second event.
4. If not found, the insert proceeds.

### 4.2 Failure Handling and Escalation (S-06, S-07)
- **Retry Schedule**: Retry every 5 minutes up to 5 attempts with exponential backoff.
- **Permanent Failure**: After 5 failed attempts, append `failed` (status final), post an alert to the COO channel, and notify the CEO.
- **Token Revocation (S-07)**:
  - If Google API returns `401 Unauthorized` or `invalid_grant` (refresh token revoked or expired):
  - Sync daemon immediately touches `~/loop2/state/GCAL_TOKEN_REVOKED.lock`.
  - All calendar pushes pause immediately.
  - An emergency alert is posted by the CIO to `#cio`:  
    `"ALERT (S-07): Google Calendar OAuth token has been revoked or expired. Calendar synchronization paused."`

---

## 5. Journal Size Management and Archival

Because the CoS reads `calendar-journal.md` on every calendar turn, large files increase token usage and LLM costs (`decisions/PENDING.md#L24`):
1. **Active Journal Window**:
   - `calendar-journal.md` maintains:
     - All future events (start time $>$ current time).
     - Events from the past 14 days.
     - Any event whose latest status is not yet `pushed` or `moved`.
2. **Monthly Archival Job**:
   - On the 1st of each month, a maintenance script archives completed past entries (older than 14 days) to `~/loop2/workspaces/cos/state/archive/calendar-YYYY-MM.md`.
   - Archival is committed to the CoS workspace git, ensuring full historical provenance is preserved while keeping active token overhead small.

---

## 6. Testing Strategy

1. **Unit Test (Append-Only Linter)**:
   - Execute simulated series of moves and deletes.
   - Verify `git diff --numstat HEAD -- state/calendar-journal.md` returns 0 deleted lines.
2. **Mock API Idempotency Drill**:
   - Simulate an insert timeout where the event is created in Google but the client times out.
   - Re-run sync; verify search finds the event, records `pushed`, and creates 0 duplicate events.
3. **Revocation Fault Injection (S-07)**:
   - Inject mock 401 response; verify `GCAL_TOKEN_REVOKED.lock` is written and CIO channel alert is dispatched.
