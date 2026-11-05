// Privacy gate plugin (APR-0113). Registers ONE hook, before_agent_run, and nothing else (no tool, command, service or route).
// For every model call it asks the rules prefilter for a label, then the privacy gate (destination: cloud, because every OpenClaw model call
// goes to the cloud model today). If the gate denies, it returns a block with a plain message and the model never reads the turn.
// Fails closed: any error inside the hook blocks the turn. Logs labels, reason codes and a hash only, to gate-log.jsonl in its own folder.
// BUILT AND TESTED ON A SCRATCH STATE FOLDER ONLY. NOT INSTALLED IN THE LIVE GATEWAY.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { classify } from "./prefilter.js";
import { decide } from "./gate.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const LOG_FILE = path.join(HERE, "gate-log.jsonl");

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
export function gateTurn(event, ctx, { policyPath = null, rulesPath = null, logFile = LOG_FILE, logger = null, nowMs = () => Date.now() } = {}) {
  let started = Date.now();
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

export default definePluginEntry({
  id: "gate-plugin",
  name: "Privacy gate",
  description: "Blocks a model turn when the privacy gate denies it. Fails closed.",
  register(api) {
    api.on("before_agent_run", (event, ctx) => gateTurn(event, ctx, { logger: api.logger }));
  },
});
