#!/usr/bin/env python3
"""coo-send-clo-patch.py - adds "clo" to agents.entries.coo.tools.agentToAgent.send in an OpenClaw config (Loop 7, APR-0128).
The one key. Everything else must stay equal (the script checks); backup CONFIG.pre-coo-clo first; safe to run twice.
Usage: coo-send-clo-patch.py CONFIG [--dry-run]"""
import copy, json, os, shutil, sys


def apply(cfg):
    """Returns a new config, or None when clo is already in the list."""
    new = copy.deepcopy(cfg)
    send = new["agents"]["entries"]["coo"]["tools"]["agentToAgent"]["send"]
    if "clo" in send:
        return None
    send.append("clo")
    return new


def only_that_key(old, new):
    o, n = copy.deepcopy(old), copy.deepcopy(new)
    n["agents"]["entries"]["coo"]["tools"]["agentToAgent"]["send"].remove("clo")
    return o == n


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    path, dry = argv[0], "--dry-run" in argv[1:]
    with open(path) as fh:
        old = json.load(fh)
    new = apply(old)
    if new is None:
        print("coo: clo already in the send list, nothing to do")
        return 0
    if not only_that_key(old, new):
        print("STOP: more than the one key would change")
        return 1
    k = "agents.entries.coo.tools.agentToAgent.send"
    print("%s: %s -> %s" % (k, json.dumps(old["agents"]["entries"]["coo"]["tools"]["agentToAgent"]["send"]),
                            json.dumps(new["agents"]["entries"]["coo"]["tools"]["agentToAgent"]["send"])))
    if dry:
        print("dry run: nothing written")
        return 0
    bak = path + ".pre-coo-clo"
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
