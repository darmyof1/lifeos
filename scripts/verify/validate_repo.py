#!/usr/bin/env python3
"""Validate the lifeos repo. Exits 1 if any BLOCKING check fails. Warnings never fail."""
import json, os, re, subprocess, sys

ROOT = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
os.chdir(ROOT)
errors, warnings = [], []
err = errors.append
warn = warnings.append

def git_lines(*args):
    return [l for l in subprocess.check_output(["git", *args], text=True).split("\n") if l]

def read(p):
    try:
        return open(p, "rb").read()
    except FileNotFoundError:
        return b""

files = git_lines("ls-files")
REG = "contracts/registry/artifacts.yaml"
LEDGER = "decisions/APPROVALS.md"
ALIASES = "contracts/models/aliases.yaml"

# BLOCKING 1: junk in the tree
for p in files:
    b = os.path.basename(p)
    if b == ".DS_Store" or re.match(r"^fix-.*\.sh$", b) or b == "remote-files.txt" or p.endswith(".bk"):
        err(f"junk file tracked: {p}")

# BLOCKING 2: no symlinks (private links must stay local)
for line in git_lines("ls-files", "-s"):
    if line.startswith("120000"):
        err(f"symlink tracked: {line.split()[-1]}")

# BLOCKING 3: registry matches the tree
try:
    reg = {a["path"]: a["status"] for a in json.loads(read(REG))["artifacts"]}
except Exception as e:
    err(f"registry unreadable ({REG}): {e}")
    reg = {}
for p in reg:
    if not os.path.exists(p):
        err(f"registry lists a missing file: {p}")
for p in files:
    if p == REG or p.endswith(".gitkeep"):
        continue
    if p not in reg:
        err(f"tracked file not in registry: {p}")

# BLOCKING 4: an empty file must be marked planned
for p in files:
    if p.endswith(".gitkeep") or not os.path.exists(p):
        continue
    if os.path.getsize(p) == 0 and reg.get(p) != "planned":
        err(f"empty file not marked planned in registry: {p}")

# BLOCKING 5: approvals ledger is well formed
ledger = read(LEDGER).decode("utf-8", "replace")
blocks = re.split(r"^## (?=APR-\d{4})", ledger, flags=re.M)[1:]
ledger_ids = set()
for b in blocks:
    aid = b.split()[0]
    ledger_ids.add(aid)
    m = re.search(r"^Status: (\w+)", b, re.M)
    if not m or m.group(1) not in ("approved", "revoked", "pending"):
        err(f"{aid}: missing or invalid Status line")
if not ledger_ids:
    err(f"no approvals found in {LEDGER}")

# BLOCKING 6: every APR reference in the repo exists in the ledger
for p in files:
    if p == LEDGER or p == REG:
        continue
    for ref in set(re.findall(rb"APR-\d{4}", read(p))):
        rid = ref.decode()
        if rid not in ledger_ids:
            err(f"{p} cites {rid}, which is not in {LEDGER}")

# BLOCKING 7: triage resolves to a local provider (APR-0001)
al = read(ALIASES).decode("utf-8", "replace")
m = re.search(r"^  triage:\n    model: (\S+)", al, re.M)
if not m:
    err("triage alias is missing in " + ALIASES)
else:
    target = m.group(1)
    blk = re.search(rf"^  {re.escape(target)}:\n((?:    .*\n?)*)", al, re.M)
    prov = re.search(r"provider: (\S+)", blk.group(1)) if blk else None
    if not prov:
        err(f"triage points at '{target}', which has no provider")
    elif prov.group(1) != "ollama":
        err(f"triage points at a non-local provider ({prov.group(1)}); APR-0001 requires local")

# BLOCKING 8: no IP addresses or personal emails in the repo
EMAIL = re.compile(rb"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
IP = re.compile(rb"\b(?:\d{1,3}\.){3}\d{1,3}\b")
for p in files:
    data = read(p)
    if IP.search(data):
        err(f"IP address found in {p}")
    for e in EMAIL.findall(data):
        if b"noreply.github.com" not in e:
            err(f"email address found in {p}: {e.decode()}")

# BLOCKING 9: spikes carry a valid status
for p in files:
    if p.startswith("research/spikes/") and p.endswith(".md") and not p.endswith("_TEMPLATE.md"):
        m = re.search(r"^Status: (\w+)", read(p).decode("utf-8", "replace"), re.M)
        if not m or m.group(1) not in ("planned", "running", "partial", "done", "failed"):
            err(f"{p}: missing or invalid Status line")

# WARNINGS (never block)
n_draft = sum(1 for s in reg.values() if s == "draft")
n_planned = sum(1 for s in reg.values() if s == "planned")
n_zero = sum(1 for p in files if os.path.exists(p) and os.path.getsize(p) == 0 and not p.endswith(".gitkeep"))
warn(f"{n_planned} planned, {n_draft} draft, {n_zero} zero-byte files")
for aid in sorted(ledger_ids):
    if re.search(rf"{aid}.*?Status: pending", ledger, re.S):
        warn(f"{aid} is still pending")

for w in warnings:
    print("WARN ", w)
for e in errors:
    print("FAIL ", e)
print(f"\n{len(errors)} blocking failure(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
