#!/usr/bin/env python3
"""rescore-criteria.py OUT.md RESULT.txt... - re-scores the two checks fixed in Loop 7 (APR-0125) from stored suite result files; the files are not edited.
Re-scored: "reply makes no false Google claim (heuristic)" (claims_google_changed) and the overlap Google check (overlap_google_ok), both taken from
reg-criteria.py in this folder. Every other criterion line is copied from the stored result. The old versions of the two checks are also re-run on the
stored data and must give the stored verdict; if they do not, the file is reported as NOT REPRODUCED and nothing is claimed about it.
Display mode of a run: the "(display full|busy)" the job printed; stored runs without it are from before the policy became full (2026-11-09), so busy.
Output: a markdown table old verdict / new verdict / changed criteria, and exit status 1 if any change is not one of the two intended checks."""
import ast, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "reg-criteria.py")) as fh:
    tree = ast.parse(fh.read())
ns = {"re": re, "os": os}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("claims_google_changed", "overlap_google_ok")],
                        type_ignores=[]), "reg-criteria.py", "exec"), ns)
NEW_CLAIM, NEW_OV = ns["claims_google_changed"], ns["overlap_google_ok"]


def old_claim(t):  # the handover 1 to 27 version, kept here only to check the parser against the stored verdicts
    for s in re.split(r"(?<=[.!?\n])", t.lower()):
        if re.search(r"(google|calendar)[^.\n]{0,60}\b(deleted|removed)\b", s) and not re.search(r"\b(not|no|unchanged|hasn't|has not|still|until|yet|unconfirmed|pending)\b|n't", s):
            return s.strip()
    return None


def section(text, start, ends):
    if start not in text:
        return ""
    body = text.split(start, 1)[1]
    cut = len(body)
    for e in ends:
        i = body.find(e)
        if i != -1:
            cut = min(cut, i)
    return body[:cut]


def unindent(s):
    return "\n".join(l[3:] if l.startswith("   ") else l for l in s.strip("\n").splitlines())


def parse(path):
    with open(path, errors="replace") as fh:
        t = fh.read()
    run = os.path.basename(path)[:-4]
    head = t.splitlines()[0] if t else ""
    q = unindent(section(t, "-- reply of the agent (first message)", ["-- reply (second message)", "-- journal lines", "-- check output"]))
    a = unindent(section(t, "-- reply (second message)", ["-- journal lines", "-- check output"]))
    jr = [[c.strip() for c in l.split("|")] for l in section(t, "-- journal lines for", ["-- check output"]).splitlines()[1:] if "|" in l]
    chk = section(t, "-- check output", ["-- Google after the job", "-- criteria"])
    gl = section(t, "-- Google after the job", ["-- criteria"]).strip("\n")
    crit = section(t, "-- criteria", ["-- cost"]).strip().splitlines()
    m = re.search(r"RESULT \S+ (PASS|FAIL)", t)
    return run, head, q, a, jr, chk, gl, crit, (m.group(1) if m else "?")


def main():
    out, rows, unintended, notrep = sys.argv[1], [], [], []
    for path in sys.argv[2:]:
        run, head, q, a, jr, chk, gl, crit, old_res = parse(path)
        disp = (re.findall(r"\(display (full|busy)\)", chk) or ["busy"])[-1]
        wr = [r for r in jr if len(r) > 3 and r[3] == "written"]
        new_crit, changed = [], []
        for line in crit:
            verdict, text = line[:4], line[5:]
            nv = verdict
            if text.startswith("reply makes no false Google claim"):
                if (old_claim(q + "\n" + a) is None) != (verdict == "PASS"):
                    notrep.append(run + ": claim check")
                nv = "PASS" if NEW_CLAIM(q + "\n" + a) is None else "FAIL"
            elif text.startswith("Google shows busy at 10-28 08:00"):
                if NEW_OV(gl, wr, "busy") != (verdict == "PASS"):
                    notrep.append(run + ": overlap check")
                nv = "PASS" if NEW_OV(gl, wr, disp) else "FAIL"
            if nv != verdict:
                changed.append("%s: %s to %s" % (text[:60], verdict, nv))
            new_crit.append((nv, text))
        n_fail = sum(1 for v, _ in new_crit if v == "FAIL")
        old_fail = sum(1 for l in crit if l.startswith("FAIL"))
        new_res = "FAIL" if n_fail else "PASS"
        scen = re.sub(r"\s+\d{4}-\d\d-\d\d.*$", "", head.split("  ", 1)[1].strip()) if "  " in head else "?"
        stored_ok = (old_res == ("FAIL" if old_fail else "PASS"))
        rows.append((run, scen, "%s (%d fail)" % (old_res, old_fail), "%s (%d fail)" % (new_res, n_fail), "; ".join(changed) or "none", stored_ok))
        for c in changed:
            if not (c.startswith("reply makes no false Google claim") or c.startswith("Google shows busy at 10-28 08:00")):
                unintended.append(run + ": " + c)
    lines = ["# Re-score of two checks (APR-0125), old verdict against new verdict, from the stored result files", "",
             "| run | scenario | old verdict | new verdict | criteria that changed |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %s | %s | %s | %s | %s |" % r[:5])
    lines += ["", "Runs: %d. Verdict changed: %d. Stored result line equals the stored criteria: %s." % (
        len(rows), sum(1 for r in rows if r[2].split(" ")[0] != r[3].split(" ")[0]), "all" if all(r[5] for r in rows) else "NOT ALL"),
        "Old checks re-run on the stored data reproduce the stored verdicts: %s." % ("yes, all" if not notrep else "NO: " + "; ".join(notrep)),
        "Changes outside the two intended checks: %s." % ("none" if not unintended else "; ".join(unintended))]
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(1 if unintended or notrep else 0)


main()
