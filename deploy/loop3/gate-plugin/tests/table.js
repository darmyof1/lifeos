// Runs the shared gate case table (tests/data/gate_cases.json) through the JS gate. Used by gate.test.js and by tests/unit/test_gate_parity.py.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { decide } from "../gate.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.join(HERE, "..", "..", "..", "..");
export const REAL_POLICY = path.join(REPO, "contracts", "policy", "privacy.yaml");
export const CASES_FILE = path.join(REPO, "tests", "data", "gate_cases.json");

export function policyFile(spec, dir) {
  if (spec === "real") return REAL_POLICY;
  if (spec === "missing") return path.join(dir, "no-such-file.yaml");
  const p = path.join(dir, "policy.yaml");
  const text = Object.prototype.hasOwnProperty.call(spec, "text") ? spec.text : fs.readFileSync(REAL_POLICY, "utf8").replace(spec.replace[0], () => spec.replace[1]);
  fs.writeFileSync(p, text, "utf8");
  return p;
}

export function runTable(file = CASES_FILE) {
  const cases = JSON.parse(fs.readFileSync(file, "utf8"));
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "gate-table-"));
  try {
    return cases.map((c) => ({ name: c.name, answer: decide(c.request, policyFile(c.policy, dir), c.now), expect: c.expect }));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  process.stdout.write(JSON.stringify(runTable(process.argv[2] || CASES_FILE).map((r) => ({ name: r.name, answer: r.answer }))));
}
