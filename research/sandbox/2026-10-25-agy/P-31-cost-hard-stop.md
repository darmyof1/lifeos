# P-31 Design: Cost Hard-Stop and Kill Switch

**Document**: `sandbox/P-31-cost-hard-stop.md`  
**Status**: Proposal (Draft)  
**Governing Approvals**: APR-0056 (cost limits), APR-0047 (LLM call log), APR-0052 / ADR-0018 (Loop 1 context), APR-0071 (Loop 1 closed)  
**Verification Standard**: Every factual claim cites file and line or command output, or is labeled "not verified".

---

## 1. Context and Problem Statement

Under APR-0056 (`decisions/APPROVALS.md#L453-L462`):
- Each scenario run has a ceiling of **0.05 USD**. A run reaching it must stop and record a failure.
- Daily provider alert at **1.00 USD per day**.
- Monthly project limit of **5.00 USD** for the `life-os` project.

During Loop 1 operations, two critical operational issues were observed:
1. **Usage Lag**: The OpenAI usage dashboard/API lags by 5 to 20 minutes (`deploy/loop1/LOOP1-CLOSE-RECORD.md#L39`, `deploy/loop1/STATE.md#L97`). In an automated multi-agent cascade, an agent loop could burn tens of dollars before an external usage API reflects the spend.
2. **Provider Limit Enforcement**: While the CEO set the OpenAI project limit to enforced ($5.00/mo, `decisions/PENDING.md#L33`), OpenAI does not provide sub-monthly daily enforcement or sub-run enforcement.
3. **Current State in Health Check**: The current health check (`deploy/loop1/health-check.py#L276`) only outputs an informational string:  
   `rec("INFO", "OpenAI spend", "not automated: check usage page for life-os key ($5/mo enforced, APR-0056)")`. It does not stop processes.

Therefore, LifeOS requires an active local cost hard-stop and kill-switch mechanism.

---

## 2. Spend Reading Architecture

Because provider-side billing APIs exhibit 5–20 minute latency, spend cannot be governed solely by querying OpenAI's usage endpoints. The design implements a **two-tier spend monitoring architecture**:

```
+-----------------------------------------------------------------------------------+
| Tier 1: Real-Time Local Token Tracker (Pre/Post Turn)                             |
|  - Reads token metrics per LLM call (APR-0047 call log & OpenClaw turn telemetry)|
|  - Computes instantaneous cost = prompt_tokens * rate + completion * rate         |
|  - Latency: < 50 ms (synchronous with turn completion)                            |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
| Tier 2: Asynchronous Provider Polling (Health Check & Periodic Daemon)            |
|  - Periodic call to OpenAI Usage API (GET /v1/organization/usage/completions)     |
|  - Reconciles total daily/monthly invoice spend against local totals               |
|  - Latency: 5-20 min lag (catches out-of-band or unlogged calls)                  |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
| Tier 3: Upstream Provider Enforcement                                             |
|  - OpenAI Project Limit ($5.00/mo hard limit, enforced by OpenAI HTTP 429)        |
+-----------------------------------------------------------------------------------+
```

### 2.1 Tier 1: Real-Time Local Accounting
- **Data Source**: Every LLM request and response in LifeOS is logged pursuant to APR-0047 (`decisions/APPROVALS.md#L353-L360`: "exact request and response per call, local and cloud, outside git"). In addition, OpenClaw turn responses include usage objects containing `prompt_tokens`, `completion_tokens`, and `cached_tokens`.
- **Pricing Matrix**: Maintained in `contracts/models/pricing.yaml` (synthetic / standard model rates). For `openai/gpt-6-luna` (or current cloud model), the accumulator maps:
  $$\text{Cost} = (\text{input\_tokens} \times R_{\text{in}}) + (\text{cached\_tokens} \times R_{\text{cached}}) + (\text{output\_tokens} \times R_{\text{out}})$$
- **Accumulator State File**: Written to `~/loop2/state/cost-accumulator.json` (mode 0600):
  ```json
  {
    "date": "2026-10-25",
    "day_spend_usd": 0.0842,
    "current_run_id": "loop2-scn-001",
    "current_run_spend_usd": 0.0125,
    "last_updated": "2026-10-25T02:35:00-04:00"
  }
  ```

### 2.2 Tier 2: Asynchronous Reconciliation
- The health check (`health-check.py`) or a cron job reads `cost-accumulator.json` and compares it with the OpenAI Usage API daily aggregate for the `life-os` project key.
- If provider spend exceeds local spend by $> 10\%$, local counters are bumped upward to match provider reality.

---

## 3. Threshold Hierarchy and Actions

In strict compliance with APR-0056:

| Scope | Threshold (USD) | Action Triggered | Target Component |
|---|---|---|---|
| **Single Scenario Run** | **$0.05** | **Run Abort & Failure Record** | Active agent session / run |
| **Daily Warning** | **$0.80** (80% of daily limit) | **Warning Log & Slack Notice** | Notification to COO Slack channel |
| **Daily Hard Ceiling** | **$1.00** | **Gateway Kill Switch** | Entire OpenClaw Gateway process |
| **Monthly Project Hard Limit**| **$5.00** | **Provider Cutoff & Lockout** | OpenAI Project Enforcement (HTTP 429) |

---

## 4. What Gets Stopped (The Kill Switch Mechanism)

### 4.1 Run-Level Stop ($0.05 Ceiling)
1. **Trigger**: When the local cost accumulator for the active `run_id` exceeds `$0.05`.
2. **Execution**:
   - The orchestrator or pre-dispatch hook issues an immediate session abort signal to OpenClaw (`openclaw sessions abort <sessionId>`).
   - Any further inter-agent `sessions_send` calls tagged with this `run_id` are rejected immediately with error: `COST_RUN_CEILING_EXCEEDED (APR-0056: limit 0.05 USD reached)`.
   - The scenario test runner marks the run result as `FAIL (cost ceiling exceeded: $0.05X USD)`.
   - The gateway remains running so other unrelated operations or recovery checks can proceed.

### 4.2 System-Level Stop ($1.00 Daily Ceiling / Emergency)
1. **Trigger**: When `day_spend_usd >= 1.00`.
2. **Execution Sequence**:
   - **Step 1 - Slack Alert (Best Effort, 5s timeout)**: Post an emergency notification to the COO channel:  
     `"EMERGENCY: Daily cost hard stop triggered ($1.00 reached). Stopping gateway immediately."`
   - **Step 2 - Gateway Process Termination**:
     Execute `kill -TERM <pid>` on the gateway process. If the process does not terminate within 15 seconds, execute `kill -KILL <pid>`.
   - **Step 3 - Lockout Enforcement**:
     Write a lockout canary file: `~/loop2/state/COST_KILL_ACTIVATED.lock` containing the trigger timestamp, total spend, and incident details.
   - **Step 4 - Supervisor Prevention**:
     The gateway startup wrapper (`env.sh` / systemd unit) checks for `COST_KILL_ACTIVATED.lock`. If present, startup aborts immediately with code 42 without invoking OpenClaw.

---

## 5. Implementation in `health-check.py`

Replace the passive INFO check in `deploy/loop1/health-check.py#L276` with active validation:

```python
# deploy/loop2/health-check.py - Cost hard-stop check
cost_file = os.path.join(STATE, "cost-accumulator.json")
lock_file = os.path.join(STATE, "COST_KILL_ACTIVATED.lock")

if os.path.exists(lock_file):
    rec("FAIL", "cost hard-stop kill switch", "KILL SWITCH ACTIVE: gateway locked out", "APR-0056 daily ceiling exceeded")
elif os.path.exists(cost_file):
    try:
        with open(cost_file) as f:
            data = json.load(f)
        day_spend = data.get("day_spend_usd", 0.0)
        if day_spend >= 1.00:
            rec("FAIL", "daily spend ceiling", f"${day_spend:.4f} >= $1.00 limit", "APR-0056")
        elif day_spend >= 0.80:
            rec("WARN", "daily spend ceiling", f"${day_spend:.4f} approaching $1.00 limit", "APR-0056 warning")
        else:
            rec("PASS", "daily spend ceiling", f"${day_spend:.4f} / $1.00", "APR-0056")
    except Exception as e:
        rec("WARN", "daily spend ceiling", f"failed reading {cost_file}: {e}", "cost telemetry read error")
else:
    rec("WARN", "daily spend ceiling", "no cost-accumulator.json found", "cost tracking uninitialized")
```

---

## 6. How It Is Tested

To ensure reliability without incurring unnecessary spend or violating APR-0071 / APR-0052:

### 6.1 Unit Test (Synthetic / Mock)
- **Path**: `tests/unit/test_cost_hard_stop.py`
- **Method**:
  1. Generate synthetic stream of LLM usage records.
  2. Feed records into accumulator until spend reaches $0.0501.
  3. Assert that the run-abort callback is triggered and subsequent requests are rejected.
  4. Feed additional records until day spend reaches $1.0001.
  5. Assert that the kill-switch handler attempts process termination and writes `COST_KILL_ACTIVATED.lock`.

### 6.2 Canary Low-Threshold Integration Drill (Loop 2)
- Set an environment variable override during a canary drill:
  `LIFEOS_TEST_RUN_CEILING_USD=0.001`
- Run a single minimal scenario query.
- Verify:
  1. The run aborts after the first turn.
  2. The run output reports `FAIL: cost ceiling reached`.
  3. No subsequent agent hops (CHO -> CoS) are spawned.

### 6.3 Recovery Drill
- With `COST_KILL_ACTIVATED.lock` present:
  1. Verify gateway startup script refuses to start (`exit code != 0`).
  2. Run administrative unlock script: `python3 scripts/ops/cost-reset.py --confirm-ceo-clearance`.
  3. Verify lockfile is archived, accumulator resets cleanly, and gateway restarts successfully.
