// CEO ledger writer (APR-0102). No OpenClaw imports: it is tested away from the gateway.
// Writes one JSON line per Slack message sent by the CEO's Slack user. It stores a hash of the text and the tokens that look like
// event IDs or run IDs, never the text. Every failure is swallowed (and counted) so that nothing can reach the gateway:
// no ledger line then means no delete (the push job fails closed).
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const DEFAULT_LEDGER = path.join(os.homedir(), "loop1", "ceo-ledger", "slack-ledger.jsonl");
export const DEFAULT_CEO_ID_FILE = path.join(os.homedir(), "loop1", "ceo-slack-id");
const TAIL_BYTES = 256 * 1024;

export const sha256 = (s) => createHash("sha256").update(s, "utf8").digest("hex");

// Tokens of letters, digits and hyphens with at least one hyphen and one digit, 3 to 64 chars (lower-cased, unique, at most 30).
export function extractTokens(text) {
  const out = [];
  for (const raw of String(text ?? "").split(/[^A-Za-z0-9-]+/)) {
    const t = raw.replace(/^-+|-+$/g, "").toLowerCase();
    if (t.length >= 3 && t.length <= 64 && t.includes("-") && /\d/.test(t) && !out.includes(t)) out.push(t);
    if (out.length >= 30) break;
  }
  return out;
}

export function makeLine({ now, account, conversation, messageId, text }) {
  return JSON.stringify({
    time: new Date(now).toISOString().replace(/\.\d{3}Z$/, "Z"),
    channel: "slack",
    account: account || "default",
    conversation: "c-" + sha256(String(conversation ?? "")).slice(0, 16),
    message_id: String(messageId ?? ""),
    sender: "CEO",
    text_sha256: sha256(String(text ?? "")),
    event_tokens: extractTokens(text),
  });
}

function readCeoId(file) {
  try { return fs.readFileSync(file, "utf8").trim(); } catch { return ""; }
}

function tailHas(file, needle) {
  try {
    const size = fs.statSync(file).size;
    const fd = fs.openSync(file, "r");
    try {
      const len = Math.min(size, TAIL_BYTES), buf = Buffer.alloc(len);
      fs.readSync(fd, buf, 0, len, size - len);
      return buf.toString("utf8").includes(needle);
    } finally { fs.closeSync(fd); }
  } catch { return false; }
}

export function createHandler({ ledgerPath = DEFAULT_LEDGER, ceoIdFile = DEFAULT_CEO_ID_FILE, now = () => Date.now(), logger = null } = {}) {
  const seen = new Set();
  const stats = { written: 0, ignored: 0, duplicates: 0, errors: 0 };
  const warn = (m) => { try { logger?.warn?.("[ceo-ledger] " + m); } catch { /* never throw */ } };
  async function handler(event, ctx) {
    try {
      if (!event || !ctx || ctx.channelId !== "slack" || typeof event.content !== "string" || !event.content) { stats.ignored++; return; }
      const ceoId = readCeoId(ceoIdFile);
      if (!ceoId) { stats.ignored++; return; }                       // no CEO ID configured: write nothing
      if (event.senderId !== ceoId) { stats.ignored++; return; }     // another sender (or none): write nothing
      const key = (ctx.conversationId ?? "") + "|" + (event.messageId || sha256(event.content) + ":" + (event.timestamp ?? ""));
      if (seen.has(key)) { stats.duplicates++; return; }
      if (event.messageId && tailHas(ledgerPath, JSON.stringify(String(event.messageId)))) { seen.add(key); stats.duplicates++; return; }
      const line = makeLine({ now: now(), account: ctx.accountId, conversation: ctx.conversationId, messageId: event.messageId, text: event.content });
      fs.mkdirSync(path.dirname(ledgerPath), { recursive: true, mode: 0o700 });
      const fd = fs.openSync(ledgerPath, fs.constants.O_WRONLY | fs.constants.O_APPEND | fs.constants.O_CREAT, 0o600);
      try { fs.writeSync(fd, line + "\n"); } finally { fs.closeSync(fd); }
      seen.add(key);
      if (seen.size > 5000) seen.clear();
      stats.written++;
    } catch (err) {
      stats.errors++;
      warn("no ledger line written: " + (err && err.code ? err.code : "error"));   // no text, no IDs in the log
    }
  }
  handler.stats = stats;
  return handler;
}
