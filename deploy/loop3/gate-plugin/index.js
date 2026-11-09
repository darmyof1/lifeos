// Privacy gate plugin (APR-0113). Registers ONE hook, before_agent_run, and nothing else (no tool, command, service or route).
// For every model call it asks the rules prefilter for a label, then the privacy gate (destination: cloud, because every OpenClaw model call
// goes to the cloud model today). If the gate denies, it returns a block with a plain message and the model never reads the turn.
// Two modes (plugin config key "mode", APR-0119):
//   shadow (the default, and the only mode installed live): NEVER blocks. Every turn passes. The gate decision is only logged as would_block.
//          Fails OPEN: any error inside the hook is logged and the turn goes on.
//   enforce: as built in Loop 3. Blocks when the gate denies. Fails closed: any error blocks the turn.
// Logs labels, reason codes and a hash only, never the text, to gate-log.jsonl in its own folder (mode 600).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { classify } from "./prefilter.js";
import { decide } from "./gate.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const LOG_FILE = path.join(HERE, "gate-log.jsonl");

// Where the hook writes. OpenClaw runs the plugin from a temporary staged copy, so the plugin folder is no place to keep a log that must
// last for days. With OPENCLAW_STATE_DIR set (the gateway always has it) the log is <state>/gate-shadow/gate-log.jsonl; otherwise LOG_FILE.
export function logFilePath(env = process.env) {
  const dir = env && typeof env.OPENCLAW_STATE_DIR === "string" ? env.OPENCLAW_STATE_DIR.trim() : "";
  return dir ? path.join(dir, "gate-shadow", "gate-log.jsonl") : LOG_FILE;
}

export const MODES = ["shadow", "enforce"];

// "enforce" only when the config says exactly that. Anything else (missing, unknown, unreadable) is shadow, which cannot block.
export function resolveMode(cfg) {
  try {
    return cfg && typeof cfg === "object" && cfg.mode === "enforce" ? "enforce" : "shadow";
  } catch (_) {
    return "shadow";
  }
}

const SUITE_RE = /(^|[:\-_])(loop\d+|scn|suite|reg|regression)([:\-_]|$)/i;

// Labels for the shadow log. They come from the hook context only; no text and no identifier is kept.
export function turnKinds(event, ctx) {
  const c = ctx && typeof ctx === "object" ? ctx : {};
  const e = event && typeof event === "object" ? event : {};
  const str = (v) => (typeof v === "string" ? v : "");
  const prov = c.inputProvenance && typeof c.inputProvenance === "object" ? str(c.inputProvenance.kind) : "";
  const trigger = str(c.trigger).toLowerCase();
  const sessionKey = str(c.sessionKey);
  const sessionId = str(c.sessionId);
  const provider = (str(c.channel) || str(c.messageProvider) || str(e.channelId)).toLowerCase();
  let channelKind;
  if (SUITE_RE.test(sessionId) || SUITE_RE.test(sessionKey.replace(/^agent:[a-z]+:/, ""))) channelKind = "suite";
  else if (prov === "inter_session") channelKind = "agent-to-agent";
  else if (trigger === "cron" || /(^|:)cron:/.test(sessionKey)) channelKind = "cron";
  else if (provider === "slack") channelKind = "slack";
  else channelKind = "main";
  const internal = prov === "inter_session" || prov === "internal_system" || (trigger !== "" && trigger !== "user" && trigger !== "manual");
  return { channelKind, triggerKind: internal ? "internal" : "human" };
}

export function blockMessage(reason) {
  return "This message was held back by the privacy gate and was not sent to the model (" + reason + "). Nothing was changed.";
}

function appendLog(file, record, logger) {
  try {
    fs.mkdirSync(path.dirname(file), { recursive: true, mode: 0o700 });
    const fd = fs.openSync(file, fs.constants.O_WRONLY | fs.constants.O_APPEND | fs.constants.O_CREAT, 0o600);
    try { fs.writeSync(fd, JSON.stringify(record) + "\n"); } finally { fs.closeSync(fd); }
  } catch (e) {
    try { logger && logger.warn && logger.warn("[gate-plugin] log line not written: " + (e && e.code ? e.code : "error")); } catch (_) { /* never throw */ }
  }
}

// Exported for tests: the whole decision for one turn. Returns { outcome: "pass" } or { outcome: "block", reason, message, category }.
export function gateTurn(event, ctx, { policyPath = null, rulesPath = null, logFile = LOG_FILE, logger = null, nowMs = () => Date.now(), mode = "shadow" } = {}) {
  let started = Date.now();
  if (mode !== "enforce") return shadowTurn(event, ctx, { policyPath, rulesPath, logFile, logger, nowMs });
  try {
    started = nowMs();
    const e = event && typeof event === "object" ? event : {};
    const c = ctx && typeof ctx === "object" ? ctx : {};
    const channel = typeof c.channel === "string" ? c.channel : (typeof e.channelId === "string" ? "other" : null);
    const pre = classify(channel, typeof c.agentId === "string" ? c.agentId : null, typeof e.prompt === "string" ? e.prompt : null, rulesPath);
    const request = {
      request_id: typeof c.runId === "string" ? c.runId : "",
      privacy: pre.label,
      complexity: "unknown",
      destination: "cloud",
      channel,
    };
    const g = decide(request, policyPath, Math.floor(nowMs() / 1000));
    appendLog(logFile, { time: new Date(started).toISOString(), prefilter: pre.log, gate: g.log, ms: nowMs() - started }, logger);
    if (g.allow) return { outcome: "pass" };
    return { outcome: "block", reason: g.reason, message: blockMessage(g.reason), category: "privacy" };
  } catch (err) {
    appendLog(logFile, { time: new Date(started).toISOString(), error: "hook_error_blocked" }, logger);
    return { outcome: "block", reason: "gate_plugin_error", message: blockMessage("gate_plugin_error"), category: "privacy" };
  }
}

// Shadow: the same prefilter and the same gate as enforce, but the answer is only written to the log. Always { outcome: "pass" }.
function shadowTurn(event, ctx, { policyPath, rulesPath, logFile, logger, nowMs }) {
  let started = Date.now();
  try {
    started = nowMs();
    const e = event && typeof event === "object" ? event : {};
    const c = ctx && typeof ctx === "object" ? ctx : {};
    const channel = typeof c.channel === "string" ? c.channel : (typeof e.channelId === "string" ? "other" : null);
    const agent = typeof c.agentId === "string" ? c.agentId : null;
    const pre = classify(channel, agent, typeof e.prompt === "string" ? e.prompt : null, rulesPath);
    const request = { request_id: typeof c.runId === "string" ? c.runId : "", privacy: pre.label, complexity: "unknown", destination: "cloud", channel };
    const g = decide(request, policyPath, Math.floor(nowMs() / 1000));
    const kinds = turnKinds(e, c);
    appendLog(logFile, {
      time: new Date(started).toISOString(), mode: "shadow", agent: pre.log.agent, channel_kind: kinds.channelKind, trigger_kind: kinds.triggerKind,
      label: pre.label, would_block: !g.allow, reason: g.reason, text_hash: pre.log.text_hash, ms: nowMs() - started,
    }, logger);
  } catch (err) {
    try { appendLog(logFile, { time: new Date(started).toISOString(), mode: "shadow", error: "hook_error_failed_open" }, logger); } catch (_) { /* never throw */ }
  }
  return { outcome: "pass", shadow: true };
}

export default definePluginEntry({
  id: "gate-plugin",
  name: "Privacy gate",
  description: "Privacy gate. Shadow mode (default): logs what it would block, blocks nothing, fails open. Enforce mode: blocks, fails closed.",
  register(api) {
    const mode = resolveMode(api.pluginConfig);
    api.on("before_agent_run", (event, ctx) => {
      const r = gateTurn(event, ctx, { logger: api.logger, mode, logFile: logFilePath() });
      return mode === "enforce" ? r : { outcome: "pass" };
    });
  },
});
