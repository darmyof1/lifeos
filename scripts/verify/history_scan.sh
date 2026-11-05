#!/usr/bin/env bash
# history_scan.sh [REPO_DIR] - scan EVERY commit of a git repo for things that must not be public (APR-0113, APR-0114).
# Looks at all lines ever added (all branches, all history) and at commit messages for: token shapes (Slack, Google, OpenAI, AWS, GitHub),
# private keys, IPv4 addresses other than 127.0.0.1 and 0.0.0.0, Slack-ID-shaped strings (other than the known fake test ones), and email
# addresses (other than example domains). Prints COUNTS and FILE NAMES only, never the matches. Exit 1 on any hit, 0 if clean.
# Author and committer email addresses in the commit metadata are reported as an INFO count (they are public with the repo); they do not fail the scan.
set -uo pipefail
DIR="${1:-.}"
cd "$DIR" || { echo "cannot enter $DIR"; exit 2; }
git rev-parse --git-dir >/dev/null 2>&1 || { echo "$DIR is not a git repository"; exit 2; }
python3 - <<'PY'
import re, subprocess, sys, collections, os

ALLOW_IDS = {"UFAKECEO01", "UFAKEOTHER2", "CFAKECHAN01", "C0123456789", "U0ANYONE", "U0FAKE0000", "U0FAKEID01", "U123456789", "UFAKE00001", "UXXXXXXXXXX"}
ALLOW_IDS |= set(filter(None, os.environ.get("HISTORY_SCAN_ALLOW_IDS", "").split(",")))
EMAIL_OK = ("example.com", "example.org", "example.net", "example.invalid", "anthropic.com", "users.noreply.github.com")

PAT = collections.OrderedDict([
    ("slack token", r"xox[abprs]-[0-9A-Za-z-]{10,}|xapp-[0-9A-Za-z-]{10,}"),
    ("google credential", r"AIza[0-9A-Za-z_-]{35}|GOCSPX-[0-9A-Za-z_-]{20,}|ya29\.[0-9A-Za-z_-]{20,}|\"client_secret\"\s*:\s*\"[^\"]{8,}\""),
    ("openai key", r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    ("aws key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("github token", r"\bgh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{22,}"),
    ("private key", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY"),
    ("ipv4 address", r"(?<![\w.])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\w.])"),
    ("slack-id shape", r"\b[UWCTB](?=[A-Z0-9]*\d)[A-Z0-9]{8,11}\b"),
    ("email address", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
])
RX = {k: re.compile(v) for k, v in PAT.items()}

def hit(cat, line):
    for m in RX[cat].finditer(line):
        s = m.group(0)
        if cat == "ipv4 address" and s in ("127.0.0.1", "0.0.0.0"):
            continue
        if cat == "slack-id shape" and s in ALLOW_IDS:
            continue
        if cat == "email address" and s.lower().endswith(EMAIL_OK):
            continue
        return True
    return False

counts = collections.Counter()
files = collections.defaultdict(set)
def scan(path, line):
    for cat in RX:
        if hit(cat, line):
            counts[cat] += 1
            files[cat].add(path)

# all added lines, all history
p = subprocess.Popen(["git", "log", "--all", "-p", "--no-color", "--no-ext-diff", "--format=@@COMMIT %H", "--no-renames"],
                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, errors="replace")
cur, ncommits = "(unknown)", 0
for raw in p.stdout:
    if raw.startswith("@@COMMIT "):
        ncommits += 1
        continue
    if raw.startswith("+++ b/"):
        cur = raw[6:].rstrip("\n")
        continue
    if raw.startswith("+++ ") or raw.startswith("--- "):
        continue
    if raw.startswith("+"):
        scan(cur, raw[1:])
p.wait()
# commit messages
msgs = subprocess.run(["git", "log", "--all", "--format=%B%x00"], capture_output=True, text=True, errors="replace").stdout
for m in msgs.split("\0"):
    for line in m.splitlines():
        scan("(commit messages)", line)

emails = subprocess.run(["git", "log", "--all", "--format=%ae%n%ce"], capture_output=True, text=True, errors="replace").stdout.split()
distinct = len({e.lower() for e in emails if "@" in e})

print("history scan: %d commits" % ncommits)
bad = 0
for cat in PAT:
    n = counts[cat]
    if n:
        bad += 1
        print("HIT  %-18s %d line(s) in %d file(s):" % (cat, n, len(files[cat])))
        for f in sorted(files[cat])[:50]:
            print("       " + f)
    else:
        print("ok   %-18s none" % cat)
print("INFO author/committer email addresses in the commit metadata: %d distinct (public with the repo; not printed)" % distinct)
print("RESULT: %s" % ("HITS FOUND" if bad else "clean"))
sys.exit(1 if bad else 0)
PY
