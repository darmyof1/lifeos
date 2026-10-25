# P-26: Slack `files:read` Scope Design and Tradeoffs

**Status**: Proposal  
**Needs CEO**: yes  
**Reference Decisions**: P-26, ADR-0003 (Privacy gate), APR-0048 / APR-0062 (Slack apps), APR-0056 (Cost limits), APR-0071 (Loop 1 close)  
**Configuration Modified**: None (Strictly design proposal; no scopes or credentials altered)

---

## 1. Context and Problem Statement

During Loop 1 and earlier spikes (`research/spikes/SPK-04-slack-multi-identity.md#L89`, `guides/local-model-setup.md#L127`, `guides/openclaw-and-ollama-install.md#L136`), Slack image and file uploads were observed to fail with permission errors because the agent Slack bot apps were not granted the `files:read` OAuth scope. OpenClaw logs the failure and continues processing the accompanying text message.

In `decisions/PENDING.md#L17-L20`, P-26 was deferred:
> "Proposed: do not add files:read. Attachments would reach the cloud model with no privacy gate (ADR-0003). Revisit after the privacy gate exists."

Now that Loop 1 is closed (APR-0071), this document analyzes the architectural, security, and cost tradeoffs for Loop 2 and provides concrete options.

---

## 2. Key Risks of Adding `files:read` Scope

1. **Privacy Gate Bypass (ADR-0003 Violation)**:
   - When a user uploads an attachment (e.g., photo, health document, medical lab report, financial statement, screenshot containing family communications), OpenClaw downloads the raw file via Slack API and injects the raw image/file bytes or base64 into the LLM context.
   - If cloud models (OpenAI `gpt-6-luna` or `gpt-4o`) are used, this unredacted personal data egresses directly to OpenAI without passing through the in-code privacy gate (`src/lifeos/router/gate.py`, ADR-0003).

2. **Multimodal Prompt Injection and Malicious Content**:
   - Files and images can contain adversarial prompt injection (steganographic text, hidden white-on-white text, or malicious instructions embedded in document metadata).
   - Without an isolated local preprocessing scanner, these payloads enter the agent's prompt directly, potentially hijacking agent tool calls.

3. **Cost and Token Limit Violations (APR-0056)**:
   - High-resolution images and multi-page PDFs consume large numbers of vision/context tokens (e.g., 1,000–5,000+ tokens per image).
   - In a multi-agent routing dialogue (COO -> CHO -> CoS), forwarding file payloads between agents will quickly breach the $0.05/run and $1.00/day hard caps established in APR-0056.

4. **Storage and Memory Footprint**:
   - Agent scratch directories (`.openclaw/tmp/`) on the VM would accumulate downloaded media files, increasing disk usage and backup overhead.

---

## 3. Options and Tradeoffs

### Option A (Recommended): Keep `files:read` Deferred; Explicit User Warning on Upload

- **Mechanism**:
  - Do not add `files:read` to any Slack bot app OAuth scopes.
  - Maintain current behavior where file downloads fail cleanly at the Slack API boundary.
  - Add an instruction or handler rule so that when OpenClaw detects an unreadable attachment, it replies:
    > "Attachments and image uploads are disabled for privacy protection (ADR-0003). Please describe the request in text."
- **Tradeoffs**:
  - *Pros*:
    - 100% compliant with ADR-0003 (zero risk of sensitive media egressing to cloud LLMs).
    - Zero unexpected vision token consumption (protects APR-0056 cost limits).
    - Eliminates multimodal prompt injection attack vectors.
    - Requires zero new code, dependencies, or VM infrastructure in Loop 2.
  - *Cons*:
    - Alex cannot send photos of receipts, meal photos, or workout screenshots via Slack. All input must be textual.

---

### Option B: Grant `files:read` Directly to Cloud Models (Reject)

- **Mechanism**:
  - Add `files:read` OAuth scope to the Slack app manifest in the Slack API Developer Portal.
  - Allow OpenClaw to download attachments and pass them directly to cloud LLM multimodal endpoints.
- **Tradeoffs**:
  - *Pros*:
    - User convenience: can upload images and PDFs directly into Slack channels.
  - *Cons*:
    - **Violates ADR-0003**: Personal photos, medical records, and financial receipts leave the machine unredacted.
    - **Violates APR-0056**: Vision tokens rapidly exceed the $0.05/run budget.
    - Vulnerable to prompt injection in image inputs.

---

### Option C: Grant `files:read` via Local Preprocessing Gate & Local Vision Model (Future Roadmap)

- **Mechanism**:
  - Add `files:read` to Slack app.
  - Slack bot intercepts the file download and routes it strictly to a local containerized OCR / vision model (e.g., Ollama running `qwen2.5-vl` or `tesseract` on local hardware).
  - An in-code privacy gate (`src/lifeos/router/gate.py`) inspects the extracted text.
  - If triage labels the content as high-privacy (health, financial, personal), the file data stays local.
  - Only sanitized textual summaries are allowed to reach cloud agents.
- **Tradeoffs**:
  - *Pros*:
    - Enables multimodal capabilities while preserving ADR-0003 privacy invariants.
  - *Cons*:
    - Requires substantial engineering: `src/lifeos/router/gate.py` must be implemented and tested (`tests/unit/test_gate.py`).
    - Requires local vision model hardware/runtime (which was deferred under SPK-06 and APR-0070).
    - Complex architecture not suitable for immediate Loop 2 start.

---

## 4. Recommendation and Decision Summary

**Recommended Choice**: **Option A** (Keep `files:read` deferred).

**Rationale**:
Under APR-0007 and ADR-0003, *privacy wins over convenience and complexity*. Until an automated, code-enforced privacy gate and local redaction pipeline are implemented and verified, granting `files:read` introduces an unacceptable data exfiltration risk. Retaining text-only Slack interaction maintains absolute data hygiene and predictable operational costs.

**Needs CEO**: yes
