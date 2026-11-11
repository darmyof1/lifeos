#!/usr/bin/env python3
"""clo-config-patch.py - adds the CLO (Chief Lifestyle Officer) to an OpenClaw config (Loop 7 part 3, APR-0126, APR-0127).
Adds only new keys: agents.entries.clo, "clo" in tools.agentToAgent.allow, and with --slack the Slack account clo, its channel
allowlist and two bindings. Every other key stays equal; the script checks that itself and refuses otherwise.
Reads the CLO channel ID from slack-channels.env (line lifestyle-clo=) and the allowed user list from the CFO account's channel.
Prints only key paths (Slack IDs are masked), never tokens. Writes a backup CONFIG.pre-clo first. Safe to run twice.
Usage: clo-config-patch.py CONFIG [--slack] [--channels-env FILE] [--workspace DIR] [--agent-dir DIR] [--dry-run]"""
import copy, json, os, re, shutil, sys

HOME = os.path.expanduser("~")


def is_id(s):
    return isinstance(s, str) and re.fullmatch(r"[CGUW][0-9A-Z]{8,}", s) is not None


def mask(p):
    return "/".join("<SLACK-ID>" if is_id(x) else x for x in p.split("/"))


def apply(cfg, workspace, agent_dir, slack=None):
    """Returns a new config. slack = (channel_id, users) or None."""
    new = copy.deepcopy(cfg)
    ents = new["agents"]["entries"]
    if "clo" in ents:
        return None
    ents["clo"] = {
        "name": "clo", "workspace": workspace, "agentDir": agent_dir,
        "identity": {"name": "CLO", "emoji": ":clapper:"},
        "model": new["agents"]["defaults"]["model"]["primary"],
        "tools": {"agentToAgent": {"send": ["coo", "cos"]}, "fs": {"workspaceOnly": True}, "alsoAllow": ["read", "write", "edit"]},
    }
    allow = new["tools"]["agentToAgent"]["allow"]
    if "clo" not in allow:
        allow.append("clo")
    if slack:
        cid, users = slack
        new["channels"]["slack"]["accounts"]["clo"] = {
            "enabled": True, "mode": "socket",
            "botToken": {"source": "env", "provider": "default", "id": "SLACK_BOT_TOKEN_CLO"},
            "appToken": {"source": "env", "provider": "default", "id": "SLACK_APP_TOKEN_CLO"},
            "channels": {cid: {"enabled": True, "users": list(users)}},
        }
        b = new["bindings"]
        peer = {"match": {"channel": "slack", "peer": {"kind": "channel", "id": cid}}, "agentId": "clo"}
        route = {"type": "route", "agentId": "clo", "match": {"channel": "slack", "accountId": "clo"}}
        last_peer = max(i for i, x in enumerate(b) if "peer" in x.get("match", {}))
        b.insert(last_peer + 1, peer)
        b.append(route)
    return new


def flat(o, p=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flat(v, p + "/" + str(k)))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flat(v, p + "/" + str(i)))
    else:
        out[p] = o
    return out


def check_only_additions(old, new):
    """Every old leaf must still exist with the same value, except list positions shifted by the binding insert.
    Returns a list of problems (empty = fine)."""
    problems = []
    for k in old:
        if k not in ("agents", "tools", "channels", "bindings", "meta", "session", "plugins", "gateway", "cron", "memory", "commands", "talk"):
            pass
    for key in set(old) | set(new):
        if key == "bindings":
            ob = [json.dumps(x, sort_keys=True) for x in old.get(key, [])]
            nb = [json.dumps(x, sort_keys=True) for x in new.get(key, [])]
            it = iter(nb)
            if not all(any(x == y for y in it) for x in ob):
                problems.append("bindings: an old binding changed or moved out of order")
        elif key == "agents":
            o2, n2 = copy.deepcopy(old[key]), copy.deepcopy(new[key])
            n2["entries"].pop("clo", None)
            if o2 != n2:
                problems.append("agents: something besides entries.clo changed")
        elif key == "tools":
            o2, n2 = copy.deepcopy(old[key]), copy.deepcopy(new[key])
            n2["agentToAgent"]["allow"] = [x for x in n2["agentToAgent"]["allow"] if x != "clo"]
            if o2 != n2:
                problems.append("tools: something besides the allow entry clo changed")
        elif key == "channels":
            o2, n2 = copy.deepcopy(old[key]), copy.deepcopy(new[key])
            n2["slack"]["accounts"].pop("clo", None)
            if o2 != n2:
                problems.append("channels: something besides slack.accounts.clo changed")
        elif old.get(key) != new.get(key):
            problems.append(key + " changed")
    return problems


def read_env_value(path, name):
    with open(path) as fh:
        for line in fh:
            k, _, v = line.strip().partition("=")
            if k == name and v.strip():
                return v.strip()
    return None


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    path, rest = argv[0], argv[1:]
    use_slack, dry = "--slack" in rest, "--dry-run" in rest

    def opt(name, default):
        return rest[rest.index(name) + 1] if name in rest else default
    ws = opt("--workspace", os.path.join(HOME, "loop1", "workspaces", "clo"))
    ad = opt("--agent-dir", os.path.join(HOME, "loop1", "state", "agents", "clo", "agent"))
    env = opt("--channels-env", os.path.join(HOME, "loop1", "slack-channels.env"))
    with open(path) as fh:
        old = json.load(fh)
    slack = None
    if use_slack:
        cid = read_env_value(env, "lifestyle-clo")
        if not cid or not is_id(cid):
            print("STOP: no valid lifestyle-clo line in " + env)
            return 1
        chans = old["channels"]["slack"]["accounts"]["cfo"]["channels"]
        users = next(iter(chans.values()))["users"]
        slack = (cid, users)
    new = apply(old, ws, ad, slack)
    if new is None:
        print("clo: already in the config, nothing to do")
        return 0
    problems = check_only_additions(old, new)
    if problems:
        print("STOP: " + "; ".join(problems))
        return 1
    fo, fn = flat(old), flat(new)
    print("new or changed keys (values of Slack IDs masked, tokens are env references only):")
    added = [k for k in fn if k not in fo and "/bindings/" not in k]
    for k in added:
        v = fn[k]
        print("  + %s = %s" % (mask(k), "<SLACK-ID>" if is_id(v) else json.dumps(v).replace(HOME, "~")))
    oldb = [json.dumps(x, sort_keys=True) for x in old.get("bindings", [])]
    for x in new.get("bindings", []):
        if json.dumps(x, sort_keys=True) not in oldb:
            print("  + binding: " + json.dumps(x).replace(json.dumps(x["match"].get("peer", {}).get("id", "")), '"<SLACK-ID>"') .replace(HOME, "~"))
    print("keys of the old config that differ in value at the same path (list shifts of the binding insert and the allow list excluded): " +
          str(len([k for k in fo if k in fn and fo[k] != fn[k] and "/bindings/" not in k])))
    if dry:
        print("dry run: nothing written")
        return 0
    bak = path + ".pre-clo"
    if os.path.exists(bak):
        print("STOP: backup " + bak + " already exists. Move it aside first.")
        return 1
    shutil.copy2(path, bak)
    with open(path, "w") as fh:
        json.dump(new, fh, indent=2)
        fh.write("\n")
    print("written; backup at " + bak)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
