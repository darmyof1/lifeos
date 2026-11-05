"""Parity (APR-0113): the SAME case tables go through the Python gate/prefilter and the JS gate/prefilter; every answer must match."""
import json, os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lifeos.router import gate, prefilter  # noqa: E402

PLUGIN = os.path.join(ROOT, "deploy", "loop3", "gate-plugin")
CASES = os.path.join(ROOT, "tests", "data", "gate_cases.json")
PRE_CASES = os.path.join(ROOT, "tests", "data", "prefilter_cases.json")
REAL = os.path.join(ROOT, "contracts", "policy", "privacy.yaml")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def policy_path(spec, d):
    if spec == "real":
        return REAL
    if spec == "missing":
        return os.path.join(d, "no-such-file.yaml")
    p = os.path.join(d, "policy.yaml")
    with open(REAL, encoding="utf-8") as f:
        real = f.read()
    text = spec["text"] if "text" in spec else real.replace(spec["replace"][0], spec["replace"][1])
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


class PythonGateMatchesStoredAnswers(unittest.TestCase):
    def test_every_case(self):
        d = tempfile.mkdtemp()
        try:
            for c in load(CASES):
                self.assertEqual(gate.decide(c["request"], policy_path(c["policy"], d), now=c["now"]), c["expect"], c["name"])
        finally:
            shutil.rmtree(d)

    def test_table_is_big_enough_and_has_both_outcomes(self):
        cases = load(CASES)
        self.assertGreaterEqual(len(cases), 80)
        self.assertEqual({c["expect"]["allow"] for c in cases}, {True, False})


@unittest.skipUnless(shutil.which("node"), "node not installed")
class JsMatchesPython(unittest.TestCase):
    def test_gate_table_answers_are_identical(self):
        out = subprocess.run(["node", os.path.join(PLUGIN, "tests", "table.js")], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        js = json.loads(out.stdout)
        cases = load(CASES)
        self.assertEqual(len(js), len(cases))
        d = tempfile.mkdtemp()
        try:
            for c, j in zip(cases, js):
                self.assertEqual(j["name"], c["name"])
                self.assertEqual(j["answer"], gate.decide(c["request"], policy_path(c["policy"], d), now=c["now"]), c["name"])
        finally:
            shutil.rmtree(d)

    def test_prefilter_answers_are_identical(self):
        cases = load(PRE_CASES)
        script = ("import {classify} from %s; const cs=JSON.parse(process.argv[1]);"
                  "process.stdout.write(JSON.stringify(cs.map(c=>classify(c.channel,c.agent,c.text))));"
                  % json.dumps("file://" + os.path.join(PLUGIN, "prefilter.js")))
        out = subprocess.run(["node", "--input-type=module", "-e", script, json.dumps(cases)], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        for c, j in zip(cases, json.loads(out.stdout)):
            self.assertEqual(j, prefilter.classify(c["channel"], c["agent"], c["text"]), c["text"])

    def test_plugin_copies_equal_repo_files(self):
        for a, b in (("privacy.yaml", os.path.join("contracts", "policy", "privacy.yaml")),
                     ("prefilter_rules.json", os.path.join("src", "lifeos", "router", "prefilter_rules.json"))):
            with open(os.path.join(PLUGIN, a), "rb") as f1, open(os.path.join(ROOT, b), "rb") as f2:
                self.assertEqual(f1.read(), f2.read(), a)


if __name__ == "__main__":
    unittest.main()
