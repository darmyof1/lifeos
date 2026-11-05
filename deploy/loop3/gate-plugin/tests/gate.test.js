// Node tests for the gate plugin (APR-0113). Run: node --test deploy/loop3/gate-plugin/tests/
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { runTable, REPO, REAL_POLICY } from "./table.js";
import { classify } from "../prefilter.js";
import { gateTurn, blockMessage } from "../index.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PLUGIN = path.join(HERE, "..");
const sha = (f) => crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex");
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), "gate-plugin-"));

test("the JS gate gives the stored answer for every case in the shared table", () => {
  const rows = runTable();
  assert.ok(rows.length >= 80);
  for (const r of rows) assert.deepEqual(r.answer, r.expect, r.name);
});

test("the policy and the rules file in the plugin folder are byte-identical copies of the repo files", () => {
  assert.equal(sha(path.join(PLUGIN, "privacy.yaml")), sha(REAL_POLICY));
  assert.equal(sha(path.join(PLUGIN, "prefilter_rules.json")), sha(path.join(REPO, "src", "lifeos", "router", "prefilter_rules.json")));
});

test("the JS prefilter gives the stored label for every sentence in the prefilter table", () => {
  const cases = JSON.parse(fs.readFileSync(path.join(REPO, "tests", "data", "prefilter_cases.json"), "utf8"));
  assert.ok(cases.length >= 40);
  for (const c of cases) assert.equal(classify(c.channel, c.agent, c.text).label, c.expect, c.text);
});

const ctx = (extra = {}) => ({ agentId: "coo", channel: "slack", runId: "run-1", ...extra });
const opts = (d, extra = {}) => ({ logFile: path.join(d, "gate-log.jsonl"), ...extra });

test("a high turn is blocked, a low turn passes, a missing prompt is blocked", () => {
  const d = tmp();
  const high = gateTurn({ prompt: "Remind me about my doctor appointment" }, ctx(), opts(d));
  assert.equal(high.outcome, "block");
  assert.match(high.message, /privacy gate/);
  assert.equal(gateTurn({ prompt: "What is the capital of France?" }, ctx(), opts(d)).outcome, "pass");
  assert.equal(gateTurn({}, ctx(), opts(d)).outcome, "block");
  assert.equal(gateTurn({ prompt: "" }, ctx(), opts(d)).outcome, "block");
  assert.equal(gateTurn(undefined, undefined, opts(d)).outcome, "block");
});

test("medium turns are blocked too (no sensitivity label is given), CHO and CFO turns are always blocked", () => {
  const d = tmp();
  assert.equal(gateTurn({ prompt: "Schedule a meeting on Thursday" }, ctx(), opts(d)).reason, "medium_not_low_sensitivity");
  assert.equal(gateTurn({ prompt: "What is the capital of France?" }, ctx({ agentId: "cho" }), opts(d)).outcome, "block");
  assert.equal(gateTurn({ prompt: "What is the capital of France?" }, ctx({ agentId: "cfo" }), opts(d)).outcome, "block");
});

test("an error inside the hook blocks (policy unreadable, rules unreadable)", () => {
  const d = tmp();
  const r1 = gateTurn({ prompt: "What is the capital of France?" }, ctx(), opts(d, { policyPath: path.join(d, "none.yaml") }));
  assert.equal(r1.outcome, "block");
  assert.equal(r1.reason, "policy_unreadable");
  const r2 = gateTurn({ prompt: "What is the capital of France?" }, ctx(), opts(d, { rulesPath: path.join(d, "none.json") }));
  assert.equal(r2.outcome, "block");
  // a thrown error from deep inside: a prompt getter that throws
  const evil = { get prompt() { throw new Error("boom"); } };
  const r3 = gateTurn(evil, ctx(), opts(d));
  assert.equal(r3.outcome, "block");
  assert.equal(r3.reason, "gate_plugin_error");
  assert.equal(gateTurn({ prompt: "x" }, ctx(), opts(d, { nowMs: () => { throw new Error("clock"); } })).outcome, "block");
});

test("the log has labels, reason codes and a hash only, never the text", () => {
  const d = tmp();
  const secret = "my private diary entry zx81 about my doctor";
  gateTurn({ prompt: secret }, ctx(), opts(d));
  gateTurn({ prompt: "What is the capital of France?" }, ctx(), opts(d));
  const raw = fs.readFileSync(path.join(d, "gate-log.jsonl"), "utf8");
  assert.ok(!raw.includes("zx81") && !raw.includes("diary entry") && !raw.includes("France"));
  const lines = raw.trim().split("\n").map((l) => JSON.parse(l));
  assert.equal(lines.length, 2);
  assert.deepEqual(Object.keys(lines[0].prefilter).sort(), ["agent", "channel", "event", "label", "reason", "text_hash"]);
  assert.equal(lines[0].gate.decision, "deny");
  assert.equal(lines[1].gate.decision, "allow");
  assert.equal((fs.statSync(path.join(d, "gate-log.jsonl")).mode & 0o777).toString(8), "600");
});

test("an unwritable log never changes the decision and never throws", () => {
  const d = tmp();
  const warnings = [];
  const logFile = path.join(d, "is-a-directory");
  fs.mkdirSync(logFile);
  const logger = { warn: (m) => warnings.push(m) };
  assert.equal(gateTurn({ prompt: "What is the capital of France?" }, ctx(), { logFile, logger }).outcome, "pass");
  assert.equal(gateTurn({ prompt: "my doctor" }, ctx(), { logFile, logger }).outcome, "block");
  assert.ok(warnings.length >= 2);
  assert.doesNotThrow(() => gateTurn({ prompt: "x" }, ctx(), { logFile, logger: { warn() { throw new Error("logger broke"); } } }));
});

test("the block message is plain and carries only the reason code", () => {
  const m = blockMessage("privacy_high_cloud_denied");
  assert.match(m, /not sent to the model/);
  assert.ok(!/[A-Z]{3,}[0-9]/.test(m));
});

test("the plugin entry registers only before_agent_run (needs the OpenClaw package on this VM)", async (t) => {
  let entry;
  try { entry = (await import("../index.js")).default; } catch (e) { t.skip("openclaw package not importable here: " + e.code); return; }
  const registered = [];
  const api = { logger: {}, on: (name, fn) => registered.push([name, typeof fn]), registerTool() { throw new Error("tool"); }, registerCommand() { throw new Error("command"); },
                registerService() { throw new Error("service"); }, registerHttpRoute() { throw new Error("route"); } };
  (entry.register || entry.default?.register)(api);
  assert.deepEqual(registered, [["before_agent_run", "function"]]);
  assert.equal(entry.id, "gate-plugin");
});

test("manifest and package: hook-only shape, no extra config", () => {
  const m = JSON.parse(fs.readFileSync(path.join(PLUGIN, "openclaw.plugin.json"), "utf8"));
  assert.equal(m.id, "gate-plugin");
  assert.deepEqual(m.configSchema, { type: "object", additionalProperties: false });
  const p = JSON.parse(fs.readFileSync(path.join(PLUGIN, "package.json"), "utf8"));
  assert.deepEqual(p.openclaw.extensions, ["./index.js"]);
});
