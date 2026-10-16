#!/usr/bin/env python3
"""Generates contracts/agents.yaml from design/roster.md (APR-0038, APR-0039).

Do not edit contracts/agents.yaml by hand. Change design/roster.md, then run this script.
  python3 scripts/verify/roster_to_agents.py          write contracts/agents.yaml
  python3 scripts/verify/roster_to_agents.py --check  exit 1 if agents.yaml differs from the roster (used by the validator)
Exits 1 if the roster is inconsistent (unknown code, title mismatch, duplicate code).
Warns when an agent has no folder under agent-files/.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "design" / "roster.md"
OUT = ROOT / "contracts" / "agents.yaml"
AGENT_FILES = ROOT / "agent-files"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse():
    chiefs, abbr, section = [], {}, None
    for line in SRC.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.startswith("|"):
            continue
        c = cells(line)
        if set("".join(c)) <= set("-: "):      # separator row
            continue
        if c[0] in ("Department", "Abbrev"):   # header rows
            continue
        if section.startswith("Abbreviation"):
            abbr[c[0]] = {"title": c[1], "tier": c[2]}
        elif len(c) == 4 and re.fullmatch(r"[A-Z]{2,5}", c[2]):
            chiefs.append({"department": c[0], "title": c[1], "code": c[2], "function": c[3]})
    return chiefs, abbr


def render():
    """Return (yaml_text, warnings). Exits with an error message if the roster is inconsistent."""
    chiefs, abbr = parse()
    errors, warnings, seen = [], [], set()
    agents = []
    for ch in chiefs:
        code = ch["code"]
        if code in seen:
            errors.append(f"duplicate code {code}")
        seen.add(code)
        if code not in abbr:
            errors.append(f"{code} is not in the abbreviation table")
            continue
        if abbr[code]["title"] != ch["title"]:
            errors.append(f"{code}: title '{ch['title']}' differs from abbreviation table '{abbr[code]['title']}'")
        folder = None
        for group in ("executive", "department"):
            if (AGENT_FILES / group / code.lower()).is_dir():
                folder = f"agent-files/{group}/{code.lower()}"
        if folder is None:
            warnings.append(f"{code}: no folder under agent-files/ yet")
        spawns = []
        m = re.search(r"Spawns: ([^.]*)\.", ch["function"])
        if m:
            spawns = [s.strip() for s in m.group(1).split(",") if s.strip()]
        agents.append({
            "code": code,
            "title": ch["title"],
            "tier": abbr[code]["tier"],
            "department": ch["department"],
            "function": ch["function"],
            "spawns": spawns,
            "folder": folder,
        })
    if errors:
        for e in errors:
            print("ERROR", e)
        sys.exit("roster is inconsistent. agents.yaml not written.")

    lines = [
        "# GENERATED from design/roster.md by scripts/verify/roster_to_agents.py.",
        "# Do not edit by hand. Change the roster, then run the script.",
        "# Status: draft",
        'schema_version: "1.0"',
        'source: "design/roster.md"',
        "agents:",
    ]
    for a in agents:
        lines += [
            f"  - code: {json.dumps(a['code'])}",
            f"    title: {json.dumps(a['title'])}",
            f"    tier: {json.dumps(a['tier'])}",
            f"    department: {json.dumps(a['department'])}",
            f"    function: {json.dumps(a['function'])}",
            f"    spawns: {json.dumps(a['spawns'])}",
            f"    folder: {json.dumps(a['folder'])}",
        ]
    return "\n".join(lines) + "\n", warnings, len(agents)


def main():
    text, warnings, count = render()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("DRIFT: contracts/agents.yaml differs from design/roster.md. Run scripts/verify/roster_to_agents.py.")
            sys.exit(1)
        print(f"agents.yaml matches design/roster.md ({count} agents)")
        return
    OUT.write_text(text, encoding="utf-8")
    print(f"agents written: {count} -> {OUT.relative_to(ROOT)}")
    for w in warnings:
        print("WARN", w)


if __name__ == "__main__":
    main()
