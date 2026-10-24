#!/usr/bin/env python3
"""Loop 1 health check. Standard library only. Run on the Oracle VM as the ubuntu user.

  python3 ~/loop1/health-check.py          offline checks: no model calls, no gateway changes
  python3 ~/loop1/health-check.py --live   offline checks, plus one cheap CoS turn and one refused CFO-to-CHO send

Each check prints PASS, WARN, FAIL or INFO, with the incident it would have caught.
Exit code 1 if any check FAILs. The script never reads or prints a key or a gateway token.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
STATE = os.path.join(HOME, "loop1", "state")
WS = os.path.join(HOME, "loop1", "workspaces")
ENV = dict(os.environ, OPENCLAW_STATE_DIR=STATE, OPENCLAW_CONFIG_PATH=os.path.join(STATE, "openclaw.json"))
PINNED = "2026.10.5"
MODEL = "openai/gpt-6-luna"
AGENTS = ["coo", "cho", "cos", "cfo"]
SEND = {"coo": ["cfo", "cho", "cos"], "cho": ["coo", "cos"], "cos": ["cho", "coo"], "cfo": ["coo"]}
BANNER = ("OpenClaw ", "│", "◇", "Dry run", "Applied ")
results = []


def rec(status, name, detail="", incident=""):
    results.append((status, name, detail, incident))


def run(args, timeout=120):
    try:
        p = subprocess.run(args, env=ENV, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, str(e)


def clean(out):
    keep = [l for l in out.splitlines() if l.strip() and not l.lstrip().startswith(BANNER)]
    return "\n".join(keep).strip()


def cfg(path):
    rc, out = run(["openclaw", "config", "get", path])
    text = clean(out)
    if not text or "unset" in text or "not found" in text:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


def js(args, timeout=120):
    rc, out = run(args, timeout)
    try:
        return json.loads(clean(out))
    except ValueError:
        return None


def git_deleted_lines(path):
    rc, out = run(["git", "-C", path, "diff", "--numstat", "HEAD", "--", "state"])
    total = 0
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1].isdigit():
            total += int(parts[1])
    return total


# 1. Environment and version
rc, out = run(["openclaw", "config", "file"])
rec("PASS" if "loop1" in out else "FAIL", "state folder is the Loop 1 folder", clean(out)[:120],
    "default ~/.openclaw folder used by mistake")
rc, out = run(["openclaw", "--version"])
rec("PASS" if PINNED in out else "FAIL", "OpenClaw pinned version", out.strip()[:80], "unpinned upgrade mid-test")
rc, out = run(["openclaw", "config", "validate"])
rec("PASS" if rc == 0 and "Config valid" in out else "FAIL", "config validates", clean(out)[:120],
    "patch with a bad key or a missing file")

# 2. Gateway process
rc, out = run(["pgrep", "-af", "openclaw.*gateway"])
procs = [l for l in out.splitlines() if l.strip()]
if len(procs) == 1:
    rec("PASS", "gateway running exactly once", "1 process")
elif not procs:
    rec("WARN", "gateway running exactly once", "gateway stopped (fine offline; --live needs it running)")
else:
    rec("FAIL", "gateway running exactly once", str(len(procs)) + " processes", "two gateways on one state folder")

# 3. Settings that must hold for Loop 1
def want(name, path, expected, incident):
    got = cfg(path)
    rec("PASS" if got == expected else "FAIL", name, path + " = " + repr(got), incident)


want("cron scheduler off (heartbeats off)", "cron.enabled", False, "heartbeat job ran unplanned")
want("gateway mode local", "gateway.mode", "local", "gateway refused to start")
want("tool profile messaging", "tools.profile", "messaging", "agents gained shell or other tools")
want("memory search off", "memory.search.enabled", False, "embeddings sent outside the privacy gate (ADR-0003)")
want("dreaming off", "plugins.entries.memory-core.config.dreaming.enabled", False, "nightly model calls nobody asked for")

model_cfg = cfg("agents.defaults.model") or {}
primary = model_cfg.get("primary") if isinstance(model_cfg, dict) else model_cfg
rec("PASS" if primary == MODEL else "FAIL", "default model", "primary = " + repr(primary), "a different model billed")
utility = cfg("agents.defaults.utilityModel")
rec("PASS" if utility == MODEL else "FAIL", "utility model", "utilityModel = " + repr(utility),
    "side calls billed to another model (SPK-04)")

models = cfg("agents.defaults.models") or {}
runtime = ((models.get(MODEL) or {}).get("agentRuntime") or {}).get("id") if isinstance(models, dict) else None
rec("PASS" if runtime == "openclaw" else "FAIL", "runtime pinned to openclaw for " + MODEL,
    "agentRuntime.id = " + repr(runtime), "harness changed during tests (P-30)")

# 4. Agent-to-agent and sessions
ata = cfg("tools.agentToAgent") or {}
allow = ata.get("allow") if isinstance(ata, dict) else None
rec("PASS" if isinstance(ata, dict) and ata.get("enabled") is True and sorted(allow or []) == sorted(AGENTS) else "FAIL",
    "agent-to-agent enabled and limited to the four agents", "allow = " + repr(allow),
    "agent pair outside the approved list")
want("sessions visibility agent", "tools.sessions.visibility", "agent", "one agent reads another agent's transcript")
sub = cfg("agents.defaults.subagents") or {}
ok_sub = isinstance(sub, dict) and sub.get("maxSpawnDepth") == 1 and sub.get("maxChildrenPerAgent") == 2 \
    and sub.get("runTimeoutSeconds") == 120
rec("PASS" if ok_sub else "FAIL", "sub-agent limits (depth 1, 2 children, 120 s)", json.dumps(sub)[:120],
    "runaway sub-agent chain")

for a in AGENTS:
    s = cfg("agents.entries." + a + ".tools.agentToAgent.send")
    rec("PASS" if sorted(s or []) == sorted(SEND[a]) else "FAIL", a + " send list",
        "send = " + repr(s), "send list drifted from APR-0044 routing")
    also = cfg("agents.entries." + a + ".tools.alsoAllow") or []
    fs = cfg("agents.entries." + a + ".tools.fs") or {}
    if a == "coo":
        rec("PASS" if not set(also) & {"read", "write", "edit"} else "WARN", "coo has no file tools",
            "alsoAllow = " + repr(also), "COO given state access it should not have")
    else:
        good = sorted(also) == ["edit", "read", "write"] and isinstance(fs, dict) and fs.get("workspaceOnly") is True
        rec("PASS" if good else "FAIL", a + " file tools limited to workspace",
            "alsoAllow = " + repr(also) + ", workspaceOnly = " + repr(fs.get("workspaceOnly") if isinstance(fs, dict) else None),
            "agent cannot write its state, or can read outside its workspace")

# 5. Agents and workspaces
agent_rows = js(["openclaw", "agents", "list", "--json"]) or []
if isinstance(agent_rows, dict):
    agent_rows = agent_rows.get("agents", [])
by_id = {r.get("id"): r for r in agent_rows if isinstance(r, dict)}
for a in AGENTS:
    r = by_id.get(a, {})
    w = os.path.join(WS, a)
    problems = []
    if r.get("model") != MODEL:
        problems.append("model " + repr(r.get("model")))
    if not os.path.isdir(w):
        problems.append("workspace missing")
    if os.path.exists(os.path.join(w, "BOOTSTRAP.md")):
        problems.append("BOOTSTRAP.md still present")
    try:
        text = open(os.path.join(w, "AGENTS.md"), encoding="utf-8").read()
    except OSError:
        text = ""
        problems.append("AGENTS.md missing")
    if "instruction set v1.2" not in text:
        problems.append("instructions older than v1.2")
    rc, log = run(["git", "-C", w, "log", "-1", "--pretty=%s", "--", "AGENTS.md"])
    if "Loop 1 instructions" not in log:
        problems.append("instruction commit missing")
    rec("PASS" if not problems else "FAIL", "workspace ready: " + a, "; ".join(problems) or "ok",
        "agent started without its instructions")

for a in ["cos", "cho", "cfo"]:
    n = git_deleted_lines(os.path.join(WS, a))
    rec("PASS" if n == 0 else "FAIL", "state append-only: " + a, str(n) + " line(s) removed from state/ since last commit",
        "journal edited in place (APR-0058)")

# 6. Log scan for known error strings
today = datetime.date.today().isoformat()
logpath = os.path.join(os.environ.get("LOOP1_LOG_DIR", "/tmp/openclaw"), "openclaw-" + today + ".log")
if os.path.exists(logpath):
    with open(logpath, encoding="utf-8", errors="replace") as fh:
        tail = fh.readlines()[-4000:]
    patterns = [
        ("database integrity verification failed", "FAIL", "state database damaged"),
        ("gateway cron.list requires credentials", "FAIL", "gateway calls without a token"),
        ("tools policy: profile", "WARN", "file tools missing alsoAllow (2026-10-22 incident)"),
        ("memory] sync failed", "WARN", "memory sync failing (should be off)"),
        ("control-command-unauthorized", "WARN", "/new refused (P-29, open)"),
        ("Path escapes sandbox root", "WARN", "expected only in the outside-path test"),
        ("Agent-to-agent messaging denied", "WARN", "expected only in the refused-send test"),
    ]
    for needle, status, why in patterns:
        hits = sum(1 for l in tail if needle in l)
        rec("PASS" if hits == 0 else status, "log: " + needle, str(hits) + " line(s) in the last 4000", why)
    # Known OpenClaw startup warning (2026-10-23): one per gateway start, from per-agent session-store maintenance.
    # INFO while it stays at one per start; WARN if it repeats, which could mean listeners growing at runtime.
    starts = sum(1 for l in tail if "startup phase: ready" in l)
    warns = sum(1 for l in tail if "MaxListenersExceededWarning" in l)
    if warns == 0:
        rec("PASS", "log: MaxListenersExceededWarning", "0 line(s)")
    elif warns <= starts:
        rec("INFO", "log: MaxListenersExceededWarning", "{} warning(s), {} gateway start(s): known startup warning".format(warns, starts))
    else:
        rec("WARN", "log: MaxListenersExceededWarning", "{} warning(s), {} gateway start(s)".format(warns, starts),
            "more warnings than gateway starts: listeners may be growing")
else:
    rec("WARN", "log file for today", "no " + logpath + " yet", "no gateway has run today")

# 7. Disk and spend
total, used, free = shutil.disk_usage(HOME)
free_pct = free * 100.0 / total
rec("PASS" if free_pct >= 15 else ("WARN" if free_pct >= 5 else "FAIL"), "disk free space",
    "{:.0f}% free".format(free_pct), "disk full stops writes")
rec("INFO", "OpenAI spend", "not automated: check the usage page for the life-os key (the limit is alert-only, P-31)")

# 8. Live round trips (only with --live)
if "--live" in sys.argv:
    rc, out = run(["openclaw", "agent", "--agent", "cos", "--timeout", "120",
                   "-m", "Health check. Reply with the single word ok."], timeout=180)
    text = clean(out)
    rec("PASS" if rc == 0 and "ok" in text.lower() else "FAIL", "live: CoS turn answers", text[-120:] or "no output",
        "gateway down or model unreachable")
    rc, out = run(["openclaw", "agent", "--agent", "cfo", "--timeout", "120",
                   "-m", "Health check permission test. Try to send the message 'test' to the agent cho with "
                         "sessions_send. You are not allowed to. Report the tool result in one line."], timeout=180)
    text = clean(out)
    refused = any(word in text.lower() for word in ("denied", "forbidden", "not allowed"))
    rec("PASS" if refused else "FAIL", "live: CFO to CHO refused by allowlist", text[-160:] or "no output",
        "allowlist not enforced")

# Report
width = max(len(r[1]) for r in results) + 2
counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}
for status, name, detail, incident in results:
    counts[status] += 1
    line = "{:<5} {:<{w}}{}".format(status, name, detail, w=width)
    if status in ("WARN", "FAIL") and incident:
        line += "  [" + incident + "]"
    print(line)
print("")
print("PASS {PASS}  WARN {WARN}  FAIL {FAIL}  INFO {INFO}".format(**counts))
sys.exit(1 if counts["FAIL"] else 0)
