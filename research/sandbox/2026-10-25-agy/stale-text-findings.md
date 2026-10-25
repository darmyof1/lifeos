# Stale Text Findings: Loop 1 and P-35 Status Audit

**Audit Date**: 2026-10-25 AST  
**Audit Purpose**: Identify every repository file that still states Loop 1 is open or refers to P-35 as open, following the formal closure of Loop 1 (APR-0071) and closure of P-35 (APR-0068).  
**Constraint Compliance**: Per TASK2 instructions, fixes are **PROPOSED ONLY AND NOT APPLIED**. No repository files outside `sandbox/` have been modified.

---

## 1. Summary of Repository Findings

| File Path | Line(s) | Topic | Current Text / Status | Proposed Fix | Applied? |
|---|---|---|---|---|---|
| `deploy/loop1/STATE.md` | 99 | Loop 1 Open | `## Still to do before Loop 1 closes` | Change heading to `## Status and Open Items at Loop 1 Close` | **NO** (Proposed only) |
| `deploy/loop1/loop1-v16-upgrade.sh` | 2 | P-35 Open | `# loop1-v16-upgrade.sh - Loop 1 instruction set v1.6 (APR-0067, P-35 stays open)...` | Change comment to note P-35 was subsequently closed under APR-0068 | **NO** (Proposed only) |
| `deploy/loop1/loop1-v16-upgrade.sh` | 18 | Gateway state | `echo "Done. Start the gateway again with slack.env and openai.env sourced."` | Note that under APR-0071 the gateway remains stopped | **NO** (Proposed only) |
| `ops/install-log.md` | 229 | Loop 1 Open | `- deploy/loop1/LOOP1-CLOSE-RECORD.md added. Loop 1 is not closed yet...` | Append inline clarification: `(Note: Loop 1 subsequently closed under APR-0071 in fix-62 below)` | **NO** (Proposed only) |
| `guides/loop1-baseline.md` | 3 | Loop 1 Status | `Status: partial` | Update status to `Status: closed (APR-0071)` | **NO** (Proposed only) |
| `decisions/APPROVALS.md` | 586, 593 | P-35 Open | `(P-35 stays open)` in APR-0067 heading and body | **Do NOT modify**: Append-only immutable historical log. Retain as-is; APR-0068 documents the closure. | **NO** (Strictly immutable) |
| `tests/scenario/bad-sleep-reschedule.md` | 65, 67 | P-35 phrasing | Mentions `(P-35)` in scenario run log tables | Retain as historical observation log; no edit required | **NO** (Historical log) |

---

## 2. Detailed Findings and Proposed Fixes

### Finding 1: `deploy/loop1/STATE.md` (Line 99)
- **File**: [`deploy/loop1/STATE.md`](file:///home/sandbox/lifeos-sandbox/deploy/loop1/STATE.md#L99-L106)
- **Current Text**:
  ```markdown
  ## Still to do before Loop 1 closes
  1. P-35 is closed (APR-0068). P-37 (COO SQLite warning) is for Loop 2.
  2. Scenario closed (APR-0069). Loop 1 closed (APR-0071); the gateway stays stopped.
  3. Daily reset check: P-36, pending. The CEO asked not to raise it for now.
  4. SPK-03: deferred by the CEO (APR-0070). Code Mode and the Docker sandbox were not tested.
  5. Health check: updated on the VM by the VM agent (it reported 41 PASS). The repo copy, deploy/loop1/health-check.py, is not updated yet; bring the VM patch in through a fix script.
  6. CEO housekeeping on the Mac: delete ~/Downloads/spk04-transfer (it holds old secrets) and old copies of health-check.py and the upgrade scripts.
  7. Loop 1 close record: deploy/loop1/LOOP1-CLOSE-RECORD.md, signed off (APR-0071).
  ```
- **Why Stale**:
  - The section heading states "Still to do before Loop 1 closes", yet line 3 of the same file states "Loop 1 is closed (APR-0071)", and items 1, 2, 4, and 7 within the list confirm that Loop 1 and P-35 are already closed.
- **Proposed Fix**:
  Replace line 99 with:
  ```markdown
  ## Carried forward at Loop 1 close (APR-0071)
  ```
  And update item 5 to reflect that the health check update was brought into `deploy/loop1/health-check.py` on branch `sandbox/agy-2026-10-25`.

---

### Finding 2: `deploy/loop1/loop1-v16-upgrade.sh` (Lines 2 and 18)
- **File**: [`deploy/loop1/loop1-v16-upgrade.sh`](file:///home/sandbox/lifeos-sandbox/deploy/loop1/loop1-v16-upgrade.sh#L1-L18)
- **Current Text**:
  ```bash
  # loop1-v16-upgrade.sh - Loop 1 instruction set v1.6 (APR-0067, P-35 stays open). Run on the VM after v1.4 on the CoS.
  ...
  echo "Done. Start the gateway again with slack.env and openai.env sourced."
  ```
- **Why Stale**:
  - The file header explicitly says "P-35 stays open" based on the interim decision APR-0067. However, the subsequent decision APR-0068 closed P-35 ("APR-0068: P-35 closed. SESSION_WORK_START_CHANGED is a retryable race...").
  - Line 18 instructs the operator to restart the gateway, which directly conflicts with APR-0071: "The Loop 1 gateway stays stopped unless a new APR entry allows it."
- **Proposed Fix**:
  Replace line 2 with:
  ```bash
  # loop1-v16-upgrade.sh - Loop 1 instruction set v1.6 (APR-0067; P-35 subsequently closed in APR-0068). Run on the VM after v1.4 on the CoS.
  ```
  Replace line 18 with:
  ```bash
  echo "Done. (Note: per APR-0071, gateway stays stopped unless a new APR entry authorizes Loop 2)."
  ```

---

### Finding 3: `ops/install-log.md` (Line 229)
- **File**: [`ops/install-log.md`](file:///home/sandbox/lifeos-sandbox/ops/install-log.md#L226-L233)
- **Current Text**:
  ```markdown
  ## 2026-10-25 - Scenario closed; SPK-03 deferred; Loop 1 close record drafted (fix-61)
  - APR-0069: scenario bad-sleep-reschedule closed after Claude's log review (run 019 clean under v1.6); cost deferred.
  - APR-0070: SPK-03 deferred by the CEO.
  - deploy/loop1/LOOP1-CLOSE-RECORD.md added. Loop 1 is not closed yet: that needs the CEO's sign-off and ends the APR-0052 exception.

  ## 2026-10-25 - Loop 1 closed (fix-62)
  - APR-0071: the CEO closed Loop 1. APR-0052 and ADR-0018 expire; the suspended entries apply again.
  - The Loop 1 gateway stays stopped unless a new APR entry allows it. Close record signed off.
  ```
- **Why Stale / Ambiguous**:
  - Line 229 states: "Loop 1 is not closed yet". Although this accurately reflected the sequence at fix-61, fix-62 directly below it completed the sign-off. Readers scanning the document can easily misinterpret line 229 out of context.
- **Proposed Fix**:
  Amend line 229 with a parenthetical cross-reference:
  ```markdown
  - deploy/loop1/LOOP1-CLOSE-RECORD.md added. Loop 1 is not closed yet at this step (subsequently signed off and closed in fix-62 / APR-0071 below).
  ```

---

### Finding 4: `guides/loop1-baseline.md` (Line 3)
- **File**: [`guides/loop1-baseline.md`](file:///home/sandbox/lifeos-sandbox/guides/loop1-baseline.md#L1-L6)
- **Current Text**:
  ```markdown
  # Loop 1 baseline on the Oracle VM, and OpenClaw CLI reference

  Status: partial
  Last verified: 2026-10-22 on the Oracle VM (Ubuntu, user ubuntu), OpenClaw 2026.10.5 (1b58cb9)
  Tool version: OpenClaw 2026.10.5 (1b58cb9)
  ```
- **Why Stale**:
  - The guide status remains marked as "Status: partial" from the initial baseline setup on 2026-10-22. However, Loop 1 baseline setup, agent bindings, Slack multi-identity routing, and instruction sets v1.2–v1.6 were fully proven and Loop 1 is closed (APR-0071).
- **Proposed Fix**:
  Update line 3 to:
  ```markdown
  Status: complete / closed (APR-0071)
  ```

---

### Finding 5: `decisions/APPROVALS.md` (Lines 586 and 593)
- **File**: [`decisions/APPROVALS.md`](file:///home/sandbox/lifeos-sandbox/decisions/APPROVALS.md#L586-L594)
- **Current Text**:
  ```markdown
  ## APR-0067 - Loop 1 instruction set v1.6: the CoS reports an acknowledgement error as delivered, not as FAILURE (P-35 stays open)
  ...
  - This changes the wording only. It does not fix the cause. P-35 stays open.
  ```
- **Rule and Architectural Note**:
  - `decisions/APPROVALS.md` is an **append-only, immutable decision ledger**.
  - APR-0067 correctly recorded the CEO's directive at that point in time ("Keep P-35 open and change the CoS's wording").
  - The subsequent entry, APR-0068 (lines 599–608), formally recorded: "APR-0068 - P-35 closed: SESSION_WORK_START_CHANGED is a retryable timing race".
  - **Proposed Action**: **DO NOT MODIFY**. Decision logs must preserve exact chronological fidelity. No retrospective edits should ever be made to past APR records.

---

### Finding 6: `tests/scenario/bad-sleep-reschedule.md` (Lines 65 and 67)
- **File**: [`tests/scenario/bad-sleep-reschedule.md`](file:///home/sandbox/lifeos-sandbox/tests/scenario/bad-sleep-reschedule.md#L65-L68)
- **Current Text**:
  - Line 65: `The CoS reported 'logged as delivered, but its acknowledgement failed (P-35)' before the CHO replied;...`
  - Line 67: `The CoS reported the P-35 acknowledgement error in v1.6 wording.`
- **Why It Exists**:
  - These lines document test run observations under instruction set v1.6, which specifically addressed the P-35 error scenario.
  - Line 5 of the same file already records that the scenario was formally closed under APR-0069 on 2026-10-25.
- **Proposed Action**: **DO NOT MODIFY**. These entries represent immutable empirical execution records.

---

## 3. Verification

All repo files were scanned using `grep -rn -iE "loop 1 (is|stays|remains) (open|active|running|not closed)" .` and `grep -rn "P-35" .`.
No other files in the repository assert that Loop 1 or P-35 remains open.
All proposed fixes have remained strictly within this report and have not modified any source files.
