#!/usr/bin/env bash
# fix-all.sh — applies the agreed fixes to the lifeos repo and COMMITS them.
# It does NOT push. You push with the command printed at the end.
#
# Run from inside the repo:
#   cd "$HOME/Desktop/Command & Control/ArchitectureOS/LifeOS2.0/lifeos"
#   NOREPLY_EMAIL="<your id>+darmyof1@users.noreply.github.com" bash fix-all.sh
# (NOREPLY_EMAIL is optional. Without it, the commit uses your current git identity.)

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
echo "Repo: $ROOT"

[ "$(git branch --show-current)" = "main" ] || { echo "Not on branch main. Stop."; exit 1; }
git diff --quiet && git diff --cached --quiet || { echo "Uncommitted tracked changes exist. Commit or stash them first. Stop."; exit 1; }

if [ -n "${NOREPLY_EMAIL:-}" ]; then
  git config user.name "darmyof1"
  git config user.email "$NOREPLY_EMAIL"
  echo "Commit author set (repo-local): darmyof1 <$NOREPLY_EMAIL>"
fi

# -----------------------------------------------------------------
# FIX 1: remove the empty duplicate registry and the invented routing file
# -----------------------------------------------------------------
echo "[1] removing stray files"
git rm -q --ignore-unmatch contracts/artifacts.yaml contracts/routing/rules.yaml
rm -f contracts/artifacts.yaml contracts/routing/rules.yaml
rmdir contracts/routing 2>/dev/null || true

# -----------------------------------------------------------------
# FIX 2: record approved decisions in the ledger, in the CEO's own words
#        Only what you explicitly answered is approved. The rest is in PENDING.
# -----------------------------------------------------------------
echo "[2] writing decisions/APPROVALS.md"
cat > decisions/APPROVALS.md <<'EOF'
# Approvals ledger

Only entries with `Status: approved` are binding. Quotes are the CEO's own answers from the
decision review (2026-10-10). Open items are in `decisions/PENDING.md`.
Each ADR cites these IDs. A change to an approved decision needs a new entry, not an edit.

## APR-0001 — Triage runs locally
Status: approved
Decided by: CEO
Your words: "triage is local, it has always been"
Applies to: ADR-0004; contracts/models/aliases.yaml (triage)

## APR-0002 — Cloud code model is GPT-6 Luna
Status: approved
Decided by: CEO
Your answer: "change to GPT-6 Luna"
Applies to: contracts/models/aliases.yaml (cloud-code)

## APR-0003 — Genesis model is Opus 5.5
Status: approved
Decided by: CEO
Your answer: "b" (move to claude-opus-5-5)
Applies to: contracts/models/aliases.yaml (genesis-brain, cloud-reasoning-high). Model ID still needs a probe (PENDING P-06).

## APR-0004 — Local model is a smaller model, about 12–14B
Status: approved
Decided by: CEO
Your answer: "a" (smaller local model, about 12–14B)
Applies to: contracts/models/aliases.yaml (local-primary). The exact model is not yet chosen (PENDING P-05).

## APR-0005 — Genesis inputs are a sanitized seed set you approve
Status: approved
Decided by: CEO
Your answer: "b"
Applies to: bootstrap/genesis-primer.md (when written); ADR-0017

## APR-0006 — Genesis Slack posts use a bounded, Genesis-only token
Status: approved
Decided by: CEO
Your answer: "b" (bounded Genesis-only scope)
Applies to: bootstrap/genesis-runbook.md (when written). The token is revoked when Genesis ends.

## APR-0007 — Privacy wins over critical complexity
Status: approved
Decided by: CEO
Your answer: "a" (privacy always wins; the CEO can override with explicit confirmation)
Applies to: contracts/policy/privacy.yaml; ADR-0003

## APR-0008 — CISO escalates P1 directly to the CEO
Status: approved
Decided by: CEO
Your answer: "a" (direct CISO to CEO)
Applies to: contracts/policy/escalation.yaml (when written); ADR-0007

## APR-0009 — The COO is the event dispatcher
Status: approved
Decided by: CEO
Your answer: "b" (COO)
Applies to: design/event-bus.md (when written); ADR-0008

## APR-0010 — Archive is local and encrypted until Phase 2; no AWS in the pilot
Status: approved
Decided by: CEO
Your answer: "b" (local encrypted archive until Phase 2)
Applies to: contracts/policy/archive.yaml (when written); ADR-0012

## APR-0011 — Archive uses S3 Object Lock (Compliance) with lifecycle to Glacier
Status: approved
Decided by: CEO
Your answer: "Object Lock Compliance with lifecycle to Glacier"
Applies to: contracts/policy/archive.yaml (when written); ADR-0012. Phase 2 only (see APR-0010).

## APR-0012 — One ADR per core decision
Status: approved
Decided by: CEO
Your answer: "one per core decision"
Applies to: decisions/adr/ (the ADR set)

## APR-0013 — Append-only logs plus state snapshots
Status: approved
Decided by: CEO
Your answer: "b" (state snapshots plus append-only logs)
Applies to: design/memory-and-data.md (when written); ADR-0011

## APR-0014 — Heartbeat files are renamed without spaces
Status: approved
Decided by: CEO
Your answer: "yes"
Applies to: agent-files/**/HEARTBEAT-*.md

## APR-0015 — Quiet hours use AST
Status: approved
Decided by: CEO
Your answer: "ast"
Applies to: ops/notification-strategy.md (when written)

## APR-0016 — Transient specialists are prompt templates
Status: approved
Decided by: CEO
Your answer: "prompt template"
Applies to: agent-files/transient/*/PROMPT.md; ADR-0010

## APR-0017 — CKO heartbeat is part of Phase 1
Status: approved
Decided by: CEO
Your answer: "yes from phase 1"
Applies to: agent-files/executive/cko/ (HEARTBEAT); design/agent-lifecycle.md

## APR-0018 — Cloud cheap model is gemini-3.8-flash-medium
Status: approved
Decided by: CEO
Your answer: "gemini-3.8-flash-medium" (the Claude Haiku 5.5 toggle is NOT approved; see PENDING P-01)
Applies to: contracts/models/aliases.yaml (cloud-cheap)
EOF

# -----------------------------------------------------------------
# FIX 3: open decisions, so nothing is treated as approved by accident
# -----------------------------------------------------------------
echo "[3] writing decisions/PENDING.md"
cat > decisions/PENDING.md <<'EOF'
# Pending decisions

Nothing here is binding. Each item moves to APPROVALS.md only when you answer it.

## P-01 — Haiku 5.5 toggle for cloud-cheap
Your answer was partial: "there must be something i can toggle".
Proposal: keep one `provider` field per alias in contracts/models/aliases.yaml. Switching to Haiku 5.5 is then a one-line change.
Needs: your yes or no.

## P-02 — Minimum Genesis seed set
Your answer was: "need help later".
Proposal: five hand-written documents only (ceo-soul, ceo-identity, 2026-vision, constitution, genesis-interview-answers) plus health-baseline. Everything else is generated.
Needs: your yes or no.

## P-03 — Calendar owner
Your answer was: "need help on what is this".
Proposal: CoS aggregates the calendar. CFA (family) and CLO (lifestyle) supply their events.
Needs: your yes or no.

## P-04 — How many ADRs must exist before Genesis
Your answer was: "dont understand this part".
Proposal: ADR-0003 (privacy), ADR-0004 (triage), ADR-0007 (CISO escalation), ADR-0016 (per-domain access). The rest can follow after Genesis.
Needs: your yes or no.

## P-05 — Exact local model
The size is approved (APR-0004). The exact model is not. Candidate: qwen2.5:14b-instruct-q4_K_M. Needs a test on the VM (research/spikes/SPK-06).

## P-06 — Verify model IDs against each provider's own CLI or API
Needs probes for: claude-opus-5-5 (genesis-brain), GPT-6-Luna (cloud-code), gemini-3.8-flash-medium (cloud-cheap), and the local model tag. Record the results in research/spikes/.

## P-07 — Draft ADRs not yet approved
The following were proposed by the audit, not approved by you: per-domain access instead of universal symlinks; OpenClaw as the initial runtime; repo, runtime, and seed separation. Keep them as drafts until you approve each one.
EOF

# -----------------------------------------------------------------
# FIX 4: model aliases — triage is local (APR-0001); cloud models per APR-0002/0003/0018
# -----------------------------------------------------------------
echo "[4] writing contracts/models/aliases.yaml"
cat > contracts/models/aliases.yaml <<'EOF'
# contracts/models/aliases.yaml
# Routing code uses ONLY these alias names. To change a model, edit this file only.
# Approvals: decisions/APPROVALS.md (APR-0001, 0002, 0003, 0004, 0018).
# Status: draft. Model IDs are unverified until probes pass (PENDING P-06).
schema_version: "1.0"
status: draft

aliases:
  triage:
    model: local-primary              # APR-0001: triage is always local
  local-primary:
    provider: ollama
    model_id: "qwen2.5:14b-instruct-q4_K_M"   # APR-0004 size; exact model pending P-05
    endpoint: "http://localhost:11434"
    privacy_max: high
  cloud-cheap:
    provider: cli:agy
    model_id: "gemini-3.8-flash-medium"        # APR-0018
    privacy_max: low
  cloud-code:
    provider: cli:codex
    model_id: "GPT-6-Luna"                     # APR-0002
    privacy_max: low
  genesis-brain:
    provider: cli:claude
    model_id: "claude-opus-5-5"                # APR-0003
    scope: genesis-only                        # APR-0006
    privacy_max: low
  cloud-reasoning-high:
    provider: cli:claude
    model_id: "claude-opus-5-5"                # APR-0003
    privacy_max: low
EOF

# -----------------------------------------------------------------
# FIX 5: privacy policy draft, backed by approved decisions
# -----------------------------------------------------------------
echo "[5] writing contracts/policy/privacy.yaml"
cat > contracts/policy/privacy.yaml <<'EOF'
# contracts/policy/privacy.yaml
# Status: draft, enforced in code (ADR-0003). Approvals: APR-0001, APR-0007.
schema_version: "1.0"
status: draft
precedence: privacy_wins            # APR-0007: critical complexity never unlocks cloud for high privacy
gate:
  high:
    cloud: denied
    override: "--override-privacy with explicit CEO confirmation; logged; CISO notified"
  medium:
    cloud: low_sensitivity_only
  low:
    cloud: allowed
    budget_gate: true
triage:
  runs_before_gate: true
  model_alias: triage               # APR-0001: local only
EOF

# -----------------------------------------------------------------
# FIX 6: empty core files get an explicit status, not silent zero bytes
# -----------------------------------------------------------------
echo "[6] marking core files as planned, with owner and blocker"
planned() { # $1 = path, $2 = title, $3 = owner, $4 = blocked by
  mkdir -p "$(dirname "$1")"
  cat > "$1" <<EOF
# $2

Status: planned
Owner: $3
Blocked by: $4

This file is intentionally empty of content until the blocker is resolved.
EOF
}
planned bootstrap/genesis-primer.md        "Genesis primer" "CEO + Aurelius design" "PENDING P-02 (seed set), APR-0005, APR-0006"
planned bootstrap/genesis-runbook.md       "Genesis runbook" "CEO" "PENDING P-02 (seed set), P-06 (model probes)"
planned contracts/agents.yaml              "Agent roster contract" "CEO" "PENDING P-03 (calendar owner) and roster review"
planned contracts/identity-access.yaml     "Identity and access contract" "CEO + CSTO" "PENDING P-04, design/identity-and-access.md"
planned design/routing-and-privacy.md      "Routing and privacy design" "CEO" "APR-0001, APR-0003, APR-0007 (approved); spec not yet written"
cat > scripts/verify/validate-repo.sh <<'EOF'
#!/usr/bin/env bash
# validate-repo.sh — NOT IMPLEMENTED YET.
# A placeholder must not pass silently. This exits non-zero on purpose.
echo "validate-repo: not implemented. Status: planned."
exit 2
EOF
chmod +x scripts/verify/validate-repo.sh

# -----------------------------------------------------------------
# FIX 7: regenerate the registry from the actual tree (replaces the stale one)
# -----------------------------------------------------------------
echo "[7] regenerating contracts/registry/artifacts.yaml from the tree"
python3 - <<'PY'
import json, os
root = "."
skip_dirs = {".git"}
skip_files = {".DS_Store", "contracts/registry/artifacts.yaml"}
arts = []
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in skip_dirs]
    for f in fn:
        p = os.path.relpath(os.path.join(dp, f), root)
        if p in skip_files or p.endswith(".gitkeep") and os.path.getsize(p) == 0:
            continue
        data = open(p, "rb").read() if os.path.getsize(p) > 0 else b""
        planned_marker = b"Status: planned" in data or b"NOT IMPLEMENTED" in data
        status = "planned" if (not data or planned_marker) else "draft"
        arts.append({"path": p, "status": status})
arts.sort(key=lambda a: a["path"])
doc = {
    "schema_version": "1.0",
    "generated_by": "fix-all.sh",
    "note": "Generated from the tree. No entry is approved here. Approvals live in decisions/APPROVALS.md.",
    "artifacts": arts,
}
with open("contracts/registry/artifacts.yaml", "w") as fh:
    json.dump(doc, fh, indent=2)
    fh.write("\n")
from collections import Counter
print("   registry entries:", len(arts), dict(Counter(a["status"] for a in arts)))
PY

# -----------------------------------------------------------------
# COMMIT (new commit, not an amend: the history stays honest)
# -----------------------------------------------------------------
echo "[8] committing"
git add -A
if git diff --cached --quiet; then
  echo "   nothing to commit"
else
  git commit -q -F - <<'MSG'
fix: reconcile repo with approvals and remove stale artifacts

- Remove empty duplicate contracts/artifacts.yaml and invented contracts/routing/rules.yaml
- Add decisions/APPROVALS.md (18 approved items, CEO's own answers) and PENDING.md (7 open)
- Set triage alias to local-primary (APR-0001); add cloud aliases per APR-0002/0003/0018
- Draft contracts/policy/privacy.yaml (privacy wins, APR-0007)
- Mark empty core files as planned with owner and blocker
- Make validate-repo.sh fail on purpose until implemented
- Regenerate contracts/registry/artifacts.yaml from the actual tree (replaces stale registry)
MSG
  echo "   committed: $(git log -1 --oneline)"
fi

# -----------------------------------------------------------------
# VERIFY (read-only)
# -----------------------------------------------------------------
echo "[9] verification"
echo "   tracked files: $(git ls-files | wc -l | tr -d ' ')"
echo "   zero-byte files: $(git ls-files | while read f; do [ -s "$f" ] || echo x; done | wc -l | tr -d ' ')"
echo "   .DS_Store tracked: $(git ls-files | grep -c DS_Store || true)"
echo "   symlinks tracked: $(git ls-files -s | awk '$1=="120000"' | wc -l | tr -d ' ')"
echo "   triage alias: $(grep -A1 '^  triage:' contracts/models/aliases.yaml | tail -1 | sed 's/^ *//')"

echo
echo "Done. Nothing was pushed. Review, then push:"
echo "  git show --stat HEAD | tail -5"
echo "  git push origin main"
