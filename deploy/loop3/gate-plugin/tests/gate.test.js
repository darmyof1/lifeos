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
import { gateTurn, blockMessage, resolveMode, turnKinds, logFilePath, LOG_FILE } from "../index.js";

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
const opts = (d, extra = {}) => ({ logFile: path.join(d, "gate-log.jsonl"), mode: "enforce", ...extra });
const shadow = (d, extra = {}) => ({ logFile: path.join(d, "gate-log.jsonl"), ...extra });

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
  assert.equal(gateTurn({ prompt: "What is the capital of France?" }, ctx(), { logFile, logger, mode: "enforce" }).outcome, "pass");
  assert.equal(gateTurn({ prompt: "my doctor" }, ctx(), { logFile, logger, mode: "enforce" }).outcome, "block");
  assert.ok(warnings.length >= 2);
  assert.doesNotThrow(() => gateTurn({ prompt: "x" }, ctx(), { logFile, mode: "enforce", logger: { warn() { throw new Error("logger broke"); } } }));
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
  assert.deepEqual(m.configSchema, { type: "object", additionalProperties: false, properties: { mode: { type: "string", enum: ["shadow", "enforce"], default: "shadow" } } });
  const p = JSON.parse(fs.readFileSync(path.join(PLUGIN, "package.json"), "utf8"));
  assert.deepEqual(p.openclaw.extensions, ["./index.js"]);
});

// ---------------------------------------------------------------- shadow mode (APR-0119)
const PROMPTS = [
  "Remind me about my doctor appointment", "What is the capital of France?", "Schedule a meeting on Thursday", "Transfer 500 dollars to savings",
  "", "my private diary entry", "How do I cook rice?", "Move my workout to Friday",
];

test("shadow is the default mode; only the exact word enforce enforces", () => {
  assert.equal(resolveMode(undefined), "shadow");
  assert.equal(resolveMode({}), "shadow");
  assert.equal(resolveMode({ mode: "shadow" }), "shadow");
  assert.equal(resolveMode({ mode: "ENFORCE" }), "shadow");
  assert.equal(resolveMode({ mode: 1 }), "shadow");
  assert.equal(resolveMode(null), "shadow");
  assert.equal(resolveMode({ mode: "enforce" }), "enforce");
  const d = tmp();
  assert.equal(gateTurn({ prompt: "Remind me about my doctor appointment" }, ctx(), shadow(d)).outcome, "pass"); // no mode given: shadow
});

test("shadow never blocks, not for high, not for a missing prompt, not for a bad policy or rules file", () => {
  const d = tmp();
  for (const agentId of ["coo", "cho", "cos", "cfo", "unknown", undefined]) {
    for (const prompt of PROMPTS) {
      const r = gateTurn({ prompt }, ctx({ agentId }), shadow(d));
      assert.deepEqual(r, { outcome: "pass", shadow: true }, agentId + " / " + prompt);
    }
  }
  assert.equal(gateTurn(undefined, undefined, shadow(d)).outcome, "pass");
  assert.equal(gateTurn({ prompt: "my doctor" }, ctx(), shadow(d, { policyPath: path.join(d, "none.yaml") })).outcome, "pass");
  assert.equal(gateTurn({ prompt: "my doctor" }, ctx(), shadow(d, { rulesPath: path.join(d, "none.json") })).outcome, "pass");
});

test("shadow fails open when the prefilter, the clock or the context throws, and logs the error", () => {
  const d = tmp();
  const evil = { get prompt() { throw new Error("boom"); } };
  assert.deepEqual(gateTurn(evil, ctx(), shadow(d)), { outcome: "pass", shadow: true });
  assert.equal(gateTurn({ prompt: "x" }, ctx(), shadow(d, { nowMs: () => { throw new Error("clock"); } })).outcome, "pass");
  const badCtx = { get agentId() { throw new Error("ctx"); } };
  assert.equal(gateTurn({ prompt: "x" }, badCtx, shadow(d)).outcome, "pass");
  const lines = fs.readFileSync(path.join(d, "gate-log.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l));
  assert.ok(lines.length >= 2);
  assert.ok(lines.every((l) => l.error === "hook_error_failed_open"));
  // the log itself unwritable and the logger throwing: still a pass, never an exception
  const dir = path.join(d, "is-a-directory");
  fs.mkdirSync(dir);
  assert.doesNotThrow(() => gateTurn({ prompt: "x" }, ctx(), { logFile: dir, logger: { warn() { throw new Error("x"); } } }));
  assert.equal(gateTurn({ prompt: "x" }, ctx(), { logFile: dir, logger: { warn() { throw new Error("x"); } } }).outcome, "pass");
});

test("parity: shadow's would_block equals enforce's decision for the same input; enforce still blocks", () => {
  const d1 = tmp(), d2 = tmp();
  let blocks = 0, passes = 0;
  for (const agentId of ["coo", "cho", "cos", "cfo"]) {
    for (const channel of ["slack", "cli", undefined]) {
      for (const prompt of PROMPTS) {
        const ev = { prompt }, cx = ctx({ agentId, channel });
        const enf = gateTurn(ev, cx, opts(d1));
        const sh = gateTurn(ev, cx, shadow(d2));
        assert.equal(sh.outcome, "pass");
        const lines = fs.readFileSync(path.join(d2, "gate-log.jsonl"), "utf8").trim().split("\n");
        const last = JSON.parse(lines[lines.length - 1]);
        assert.equal(last.would_block, enf.outcome === "block", agentId + "/" + channel + "/" + prompt);
        if (enf.outcome === "block") { blocks++; assert.equal(last.reason, enf.reason); } else passes++;
      }
    }
  }
  assert.ok(blocks > 20 && passes > 0);
});

test("shadow log line: the agreed fields only, no text, mode 600, one line per turn", () => {
  const d = tmp();
  const secret = "my private diary entry zx81 about my doctor";
  gateTurn({ prompt: secret }, ctx({ agentId: "cho" }), shadow(d));
  gateTurn({ prompt: "What is the capital of France?" }, ctx(), shadow(d));
  const file = path.join(d, "gate-log.jsonl");
  const raw = fs.readFileSync(file, "utf8");
  assert.ok(!raw.includes("zx81") && !raw.includes("diary") && !raw.includes("France") && !raw.includes("run-1"));
  const lines = raw.trim().split("\n").map((l) => JSON.parse(l));
  assert.equal(lines.length, 2);
  assert.deepEqual(Object.keys(lines[0]).sort(), ["agent", "channel_kind", "label", "mode", "ms", "reason", "text_hash", "time", "trigger_kind", "would_block"]);
  assert.equal(lines[0].agent, "cho");
  assert.equal(lines[0].would_block, true);
  assert.equal(lines[0].label, "high");
  assert.match(lines[0].text_hash, /^[0-9a-f]{16}$/);
  assert.equal(typeof lines[0].ms, "number");
  assert.equal(lines[0].mode, "shadow");
  assert.equal((fs.statSync(file).mode & 0o777).toString(8), "600");
});

test("turn kinds: slack, main, cron, agent-to-agent, suite; human or internal", () => {
  const k = (event, c) => turnKinds(event, c);
  assert.deepEqual(k({}, { channel: "slack", agentId: "coo", sessionKey: "agent:coo:slack:channel:x", trigger: "user" }), { channelKind: "slack", triggerKind: "human" });
  assert.deepEqual(k({}, { agentId: "coo", sessionKey: "agent:coo:main" }), { channelKind: "main", triggerKind: "human" });
  assert.deepEqual(k({}, { agentId: "coo", sessionKey: "agent:coo:cron:job1", trigger: "cron" }), { channelKind: "cron", triggerKind: "internal" });
  assert.deepEqual(k({}, { agentId: "cho", sessionKey: "agent:cho:main", inputProvenance: { kind: "inter_session" } }), { channelKind: "agent-to-agent", triggerKind: "internal" });
  assert.deepEqual(k({}, { agentId: "coo", sessionKey: "agent:coo:explicit:loop5-scn-001-coo" }), { channelKind: "suite", triggerKind: "human" });
  assert.deepEqual(k({}, { agentId: "coo", sessionId: "reg-12-coo" }), { channelKind: "suite", triggerKind: "human" });
  assert.deepEqual(k({}, { agentId: "cfo", trigger: "heartbeat", sessionKey: "agent:cfo:main" }), { channelKind: "main", triggerKind: "internal" });
  assert.deepEqual(k(undefined, undefined), { channelKind: "main", triggerKind: "human" });
});

test("the plugin entry's hook returns pass in shadow and the gate's answer in enforce", async (t) => {
  let entry;
  try { entry = (await import("../index.js")).default; } catch (e) { t.skip("openclaw package not importable here: " + e.code); return; }
  const reg = (pluginConfig) => {
    const hooks = {};
    (entry.register || entry.default?.register)({ logger: {}, pluginConfig, on: (n, f) => { hooks[n] = f; } });
    return hooks.before_agent_run;
  };
  const high = { prompt: "Remind me about my doctor appointment" };
  const d = tmp();
  const saved = process.env.OPENCLAW_STATE_DIR;
  process.env.OPENCLAW_STATE_DIR = d;      // the hook writes under the state folder: point it at a temp folder
  try {
    assert.deepEqual(reg(undefined)(high, ctx()), { outcome: "pass" });
    assert.deepEqual(reg({ mode: "shadow" })(high, ctx()), { outcome: "pass" });
    assert.equal(reg({ mode: "enforce" })(high, ctx()).outcome, "block");
    assert.ok(fs.existsSync(path.join(d, "gate-shadow", "gate-log.jsonl")));
  } finally {
    if (saved === undefined) delete process.env.OPENCLAW_STATE_DIR; else process.env.OPENCLAW_STATE_DIR = saved;
  }
});

test("the log path: under the state folder when the gateway sets it, else the plugin folder; mode 700 folder, 600 file", () => {
  assert.equal(logFilePath({}), LOG_FILE);
  assert.equal(logFilePath({ OPENCLAW_STATE_DIR: "" }), LOG_FILE);
  assert.equal(logFilePath({ OPENCLAW_STATE_DIR: "/x/state" }), path.join("/x/state", "gate-shadow", "gate-log.jsonl"));
  const d = tmp();
  const file = logFilePath({ OPENCLAW_STATE_DIR: d });
  gateTurn({ prompt: "What is the capital of France?" }, ctx(), { logFile: file });
  assert.equal((fs.statSync(path.dirname(file)).mode & 0o777).toString(8), "700");
  assert.equal((fs.statSync(file).mode & 0o777).toString(8), "600");
});
