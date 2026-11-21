// Send log writer (APR-0136). No OpenClaw imports: it is tested away from the gateway.
// One line per sessions_send call and one per CEO message in an agent's Slack channel. Never message text, never a return value.
// Every failure is swallowed and counted in memory: no line then means unknown, never a wrong answer.
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const DEFAULT_DIR = path.join(os.homedir(), "loop1", "workspaces", "coo", "state");
export const DEFAULT_CEO_ID_FILE = path.join(os.homedir(), "loop1", "ceo-slack-id");
// Slack account name -> agent id (the default account is the COO's)
export const ACCOUNT_AGENT = { default: "coo", coo: "coo", cho: "cho", cos: "cos", cfo: "cfo", clo: "clo" };
const RUN_ID = /coo-\d{8}-\d{4}/;

export const sha256 = (s) => createHash("sha256").update(s, "utf8").digest("hex");

// "YYYY-MM-DD HH:MM" and "YYYY-MM" in America/Puerto_Rico (AST, no daylight saving)
export function astParts(ms) {
  const f = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Puerto_Rico", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
  const p = Object.fromEntries(f.formatToParts(new Date(ms)).map((x) => [x.type, x.value]));
  return { stamp: `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}`, month: `${p.year}-${p.month}` };
}

export const targetAgent = (sessionKey) => {
  const m = /^agent:([A-Za-z0-9_-]+):/.exec(typeof sessionKey === "string" ? sessionKey : "");
  return m ? m[1] : "unknown";
};
export const runIdOf = (message) => { const m = RUN_ID.exec(typeof message === "string" ? message : ""); return m ? m[0] : "none"; };

// Masked error text: whitespace collapsed; session keys, long mixed letter-digit runs, 6+ digits and token-looking strings -> <id>; cut to 80.
// If it still holds any 20-character piece of the message, only "error (text withheld)" is written.
export function maskError(error, message) {
  let t = String(error ?? "").replace(/\s+/g, " ").trim();
  t = t.replace(/agent:[^\s"'`,;)\]]*/gi, "<id>")
    .replace(/\b(?:xox[a-z]-|xapp-|sk-|ghp_|gho_)[A-Za-z0-9_-]*/gi, "<id>")
    .replace(/[A-Za-z0-9_-]*\d[A-Za-z0-9_-]*/g, (w) => (/\d{6,}/.test(w) || (w.length >= 9 && /[A-Za-z]/.test(w)) ? "<id>" : w))
    .replace(/[A-Za-z]*[A-Za-z0-9]{9,}[A-Za-z0-9]*/g, (w) => (/\d/.test(w) ? "<id>" : w))
    .replace(/(?:<id>[\s-]*){2,}/g, "<id> ");
  t = t.trim().slice(0, 80);
  const msg = typeof message === "string" ? message.replace(/\s+/g, " ").trim() : "";
  for (let i = 0; i + 20 <= msg.length; i++) if (t.includes(msg.slice(i, i + 20))) return "error (text withheld)";
  return t;
}

export function sendLine({ now, from, event }) {
  const p = (event && event.params) || {};
  const err = event && event.error ? true : false;
  const base = [astParts(now).stamp, "send", `${from || "unknown"} -> ${targetAgent(p.sessionKey)}`, runIdOf(p.message), err ? "error" : "ok"];
  if (err) base.push(maskError(event.error, p.message));
  return base.join(" | ");
}

export const ceoLine = ({ now, agent, text }) =>
  [astParts(now).stamp, "ceo-message", agent ? `${agent} channel` : "unknown channel", sha256(String(text ?? "")).slice(0, 8)].join(" | ");

function readCeoId(file) {
  try { return fs.readFileSync(file, "utf8").trim(); } catch { return ""; }
}

export function createHandlers({ dir = DEFAULT_DIR, ceoIdFile = DEFAULT_CEO_ID_FILE, now = () => Date.now(), logger = null } = {}) {
  const stats = { written: 0, ignored: 0, errors: 0 };
  const warn = (m) => { try { logger?.warn?.("[send-log] " + m); } catch { /* never throw */ } };
  function append(line) {
    const file = path.join(dir, `send-log-${astParts(now()).month}.md`);
    const mk = fs.existsSync(file) ? "" : `# send log (written by code, no message text) - ${astParts(now()).month}\n`;
    fs.mkdirSync(dir, { recursive: true });
    fs.appendFileSync(file, mk + line + "\n");   // one write per event
    stats.written++;
  }
  function afterToolCall(event, ctx) {
    try {
      if (!event || event.toolName !== "sessions_send") { stats.ignored++; return; }
      append(sendLine({ now: now(), from: ctx && ctx.agentId, event }));
    } catch (err) {
      stats.errors++;
      warn("no line written: " + (err && err.code ? err.code : "error"));
    }
  }
  function messageReceived(event, ctx) {
    try {
      if (!event || !ctx || ctx.channelId !== "slack" || typeof event.content !== "string" || !event.content) { stats.ignored++; return; }
      const ceoId = readCeoId(ceoIdFile);
      if (!ceoId || event.senderId !== ceoId) { stats.ignored++; return; }   // no CEO ID configured, or another sender: write nothing
      append(ceoLine({ now: now(), agent: ACCOUNT_AGENT[String(ctx.accountId || "default")], text: event.content }));
    } catch (err) {
      stats.errors++;
      warn("no line written: " + (err && err.code ? err.code : "error"));
    }
  }
  return { afterToolCall, messageReceived, stats };
}
