#!/usr/bin/env python3
"""bot-thread-mention-patch.py - sets channels.slack.accounts.<id>.requireMentionInBotThreads = false for the five Slack accounts
(default = COO, cho, cos, cfo, clo) (APR-0143). Touches only those five keys: after the edit it compares the whole config key by key
with the original and refuses unless the only differences are those five additions. Prints key paths and true/false only; never a
token or an ID (account labels are fixed names). Writes CONFIG.pre-mentionthreads first (never overwrites an existing backup).
Usage: bot-thread-mention-patch.py CONFIG [--dry-run]      Safe to run twice."""
import copy, json, os, shutil, sys

ACCOUNTS = ["default", "cho", "cos", "cfo", "clo"]
LABEL = {"default": "coo", "cho": "cho", "cos": "cos", "cfo": "cfo", "clo": "clo"}
KEY = "requireMentionInBotThreads"


def apply(cfg):
    """Returns (new config, list of changed account ids). Raises ValueError if an account is missing."""
    new = copy.deepcopy(cfg)
    accs = new.get("channels", {}).get("slack", {}).get("accounts")
    if not isinstance(accs, dict):
        raise ValueError("channels.slack.accounts missing")
    changed = []
    for a in ACCOUNTS:
        if a not in accs or not isinstance(accs[a], dict):
            raise ValueError("slack account %s missing" % LABEL[a])
        if accs[a].get(KEY) is not False:
            accs[a][KEY] = False
            changed.append(a)
    return new, changed


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


def diff_paths(old, new):
    """Key paths added, removed or changed (account ids replaced by their labels)."""
    a, b = flat(old), flat(new)
    def lab(path):
        parts = path.split("/")
        if len(parts) > 4 and parts[1:4] == ["channels", "slack", "accounts"]:
            parts[4] = LABEL.get(parts[4], "<account>")
        return "/".join(parts[:5] + (["..."] if len(parts) > 6 else parts[5:]))
    added = sorted(lab(k) for k in b if k not in a)
    removed = sorted(lab(k) for k in a if k not in b)
    changed = sorted(lab(k) for k in a if k in b and a[k] != b[k])
    return added, removed, changed


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__.split("Usage:")[1].strip()); return 2
    path = argv[0]; dry = "--dry-run" in argv
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    try:
        new, changed = apply(cfg)
    except ValueError as e:
        print(str(e) + ". Stop."); return 1
    if not changed:
        print("already set on all five accounts, nothing to do"); return 0
    added, removed, other = diff_paths(cfg, new)
    expected = sorted("/channels/slack/accounts/%s/%s" % (LABEL[a], KEY) for a in changed)
    if added != expected or removed or other:
        print("unexpected difference; refusing. Stop."); return 1
    for p in added:
        print("add", p, "= false")
    if dry:
        print("Dry run only. Nothing was changed."); return 0
    backup = path + ".pre-mentionthreads"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    tmp = path + ".tmp-mentionthreads"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(new, fh, indent=2); fh.write("\n")
    os.chmod(tmp, os.stat(path).st_mode & 0o777)
    os.replace(tmp, path)
    print("written; backup:", os.path.basename(backup))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
