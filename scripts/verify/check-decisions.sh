#!/usr/bin/env bash
# check-decisions.sh — read-only checks that the approved decisions are present in the repo.
# Prints PASS, FAIL, or TODO for each. Exit 1 if any FAIL. TODO does not fail.
cd "$(git rev-parse --show-toplevel)"
pass=0; fail=0; todo=0
ok()   { echo "PASS  $1"; pass=$((pass+1)); }
bad()  { echo "FAIL  $1"; fail=$((fail+1)); }
todo() { echo "TODO  $1"; todo=$((todo+1)); }

# APR-0030 and APR-0031 exist and are approved
grep -q '^## APR-0030' decisions/APPROVALS.md && grep -A3 '^## APR-0030' decisions/APPROVALS.md | grep -q 'Status: approved' && ok "APR-0030 approved (CoS sole calendar writer)" || bad "APR-0030 missing or not approved"
grep -q '^## APR-0031' decisions/APPROVALS.md && grep -A3 '^## APR-0031' decisions/APPROVALS.md | grep -q 'Status: approved' && ok "APR-0031 approved (Google Calendar)" || bad "APR-0031 missing or not approved"

# P-10 and P-11 are no longer open
grep -q '^## P-10' decisions/PENDING.md && bad "P-10 still listed as pending" || ok "P-10 resolved"
grep -q '^## P-11' decisions/PENDING.md && bad "P-11 still listed as pending" || ok "P-11 resolved"

# ADR-0004: triage resolves to a local provider
python3 - <<'PY' && ok "ADR-0004 triage is local (checked against aliases.yaml)" || bad "ADR-0004 triage is NOT local"
import re, sys
al = open("contracts/models/aliases.yaml").read()
m = re.search(r"^  triage:\n    model: (\S+)", al, re.M)
b = re.search(rf"^  {re.escape(m.group(1))}:\n((?:    .*\n?)*)", al, re.M) if m else None
p = re.search(r"provider: (\S+)", b.group(1)) if b else None
sys.exit(0 if p and p.group(1) == "ollama" else 1)
PY

# ADR-0007: CISO escalation bypasses the COO
grep -qi 'bypass' decisions/adr/ADR-0007-direct-ciso-p1-escalation.md && grep -q 'APR-0008' decisions/adr/ADR-0007-direct-ciso-p1-escalation.md && ok "ADR-0007 cites APR-0008 and bypasses the COO" || bad "ADR-0007 incomplete"

# ADR-0016: per-domain access, and the contract it depends on
grep -q 'APR-0029' decisions/adr/ADR-0016-per-domain-access-not-universal-symlinks.md && ok "ADR-0016 cites APR-0029" || bad "ADR-0016 does not cite APR-0029"
[ -s contracts/identity-access.yaml ] && [ "$(grep -c 'Status: planned' contracts/identity-access.yaml)" = "0" ] && ok "identity-access contract written" || todo "identity-access contract not written yet (needed before Genesis)"

# ADR-0003: privacy gate status
grep -q 'Status: accepted' decisions/adr/ADR-0003-privacy-gate-in-code.md && ok "ADR-0003 accepted" || todo "ADR-0003 is proposed: approve the 'enforced in code' mechanism to accept it"

echo
echo "$pass passed, $fail failed, $todo to do"
[ "$fail" -eq 0 ]
