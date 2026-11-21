// Run: node --test tests/   (from deploy/after-loop7/send-log-plugin). Fake IDs and synthetic text only.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createHandlers, maskError, targetAgent, runIdOf, sha256 } from "../log.js";

const FAKE_CEO = "UFAKECEO01";
const T = Date.UTC(2026, 10, 21, 5, 8, 0);          // 2026-11-21 01:08 AST
const SECRET = "distinctive synthetic purchase words zebra";
function setup(over = {}) {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), "sendlog-"));
  const idFile = path.join(base, "ceo-slack-id"); fs.writeFileSync(idFile, FAKE_CEO + "\n");
  const dir = path.join(base, "ws", "state");
  let t = T; const h = createHandlers({ dir, ceoIdFile: idFile, now: () => t, ...over });
  const file = (m = "2026-11") => path.join(dir, `send-log-${m}.md`);
  const read = (m) => (fs.existsSync(file(m)) ? fs.readFileSync(file(m), "utf8").split("\n").filter(Boolean) : []);
  return { base, idFile, dir, h, file, read, setNow: (x) => { t = x; } };
}
const send = (o = {}) => ({ toolName: "sessions_send", params: { sessionKey: "agent:cfo:main", message: SECRET + " coo-20261121-0108", ...(o.params || {}) }, ...(o.ev || {}) });

test("registers exactly two hooks and nothing else; before_tool_call never", async () => {
  const src = fs.readFileSync(new URL("../index.js", import.meta.url), "utf8");
  const calls = [];
  const api = new Proxy({ logger: {}, on: (n) => calls.push(n) }, { get(t, k) { if (k in t) return t[k]; return () => { throw new Error("forbidden register call " + String(k)); }; } });
  // the OpenClaw SDK is not installed away from the gateway: stub the one import and load the real entry text
  const code = src.replace(/import \{ definePluginEntry \} from "openclaw\/plugin-sdk\/plugin-entry";/, "const definePluginEntry = (x) => x;")
    .replace('"./log.js"', JSON.stringify(new URL("../log.js", import.meta.url).href));
  const mod = (await import("data:text/javascript;base64," + Buffer.from(code).toString("base64"))).default;
  mod.register(api);
  assert.deepEqual(calls.sort(), ["after_tool_call", "message_received"]);
  assert.ok(!/before_tool_call/.test(src.replace(/\/\/.*$/gm, "")));
});

test("a sessions_send event writes the exact line, header first", () => {
  const s = setup(); const r = s.h.afterToolCall(send(), { agentId: "coo" });
  assert.equal(r, undefined);
  assert.deepEqual(s.read(), ["# send log (written by code, no message text) - 2026-11", "2026-11-21 01:08 | send | coo -> cfo | coo-20261121-0108 | ok"]);
});

test("header is written once", () => {
  const s = setup(); s.h.afterToolCall(send(), { agentId: "coo" }); s.h.afterToolCall(send(), { agentId: "cfo" });
  assert.equal(s.read().filter((l) => l.startsWith("# send log")).length, 1); assert.equal(s.read().length, 3);
});

test("other tools write nothing", () => {
  const s = setup(); s.h.afterToolCall({ toolName: "exec", params: {} }, { agentId: "cfo" }); s.h.afterToolCall(null, null);
  assert.equal(s.read().length, 0);
});

test("run ID token found or none; target parsing", () => {
  assert.equal(runIdOf("x coo-20261121-0108 y"), "coo-20261121-0108"); assert.equal(runIdOf("no id here"), "none"); assert.equal(runIdOf(undefined), "none");
  assert.equal(targetAgent("agent:clo:slack:channel:C1"), "clo"); assert.equal(targetAgent("weird"), "unknown"); assert.equal(targetAgent(undefined), "unknown");
  const s = setup(); s.h.afterToolCall(send({ params: { sessionKey: "oops", message: "hi" } }), { agentId: "cho" });
  assert.equal(s.read()[1], "2026-11-21 01:08 | send | cho -> unknown | none | ok");
});

test("no message text in any line, even with an error", () => {
  const s = setup(); s.h.afterToolCall(send(), { agentId: "coo" });
  s.h.afterToolCall(send({ ev: { error: "failed to deliver: " + SECRET, result: { content: SECRET } } }), { agentId: "coo" });
  const raw = fs.readFileSync(s.file(), "utf8"); assert.ok(!raw.includes("zebra")); assert.ok(!raw.includes("distinctive"));
  assert.ok(raw.includes("error (text withheld)"));
});

test("masked error text", () => {
  const e = maskError("session change   error\nfor agent:coo:slack:channel:C0ABC12345:thread:1731.2 id ABCD1234XYZ9 and 1234567 token xoxb-abc-123", "other");
  assert.ok(!/agent:|C0ABC|ABCD1234|1234567|xoxb/.test(e)); assert.ok(e.includes("<id>")); assert.ok(e.length <= 80); assert.ok(!/\n/.test(e));
  assert.equal(maskError("x".repeat(200), "m").length, 80);
  assert.equal(maskError("plain gateway error: busy", "hello"), "plain gateway error: busy");
  assert.equal(maskError("could not send: the quick synthetic words here ok", "the quick synthetic words here ok go"), "error (text withheld)");
});

test("error line: result error plus masked text", () => {
  const s = setup(); s.h.afterToolCall(send({ ev: { error: "session busy for agent:cfo:main" } }), { agentId: "coo" });
  assert.equal(s.read()[1], "2026-11-21 01:08 | send | coo -> cfo | coo-20261121-0108 | error | session busy for <id>");
});

test("ceo-message line only for the CEO id", () => {
  const s = setup(); const c = { channelId: "slack", accountId: "cfo" };
  assert.equal(s.h.messageReceived({ content: SECRET, senderId: FAKE_CEO }, c), undefined);
  s.h.messageReceived({ content: SECRET, senderId: "UOTHER" }, c); s.h.messageReceived({ content: SECRET }, c);
  s.h.messageReceived({ content: SECRET, senderId: FAKE_CEO }, { channelId: "webchat", accountId: "cfo" }); s.h.messageReceived({ content: "", senderId: FAKE_CEO }, c);
  s.h.messageReceived({ content: "ping", senderId: FAKE_CEO }, { channelId: "slack", accountId: "default" });
  s.h.messageReceived({ content: "ping", senderId: FAKE_CEO }, { channelId: "slack", accountId: "weird" });
  const l = s.read();
  assert.equal(l.length, 4);
  assert.equal(l[1], "2026-11-21 01:08 | ceo-message | cfo channel | " + sha256(SECRET).slice(0, 8));
  assert.ok(l[2].includes("coo channel")); assert.ok(l[3].includes("unknown channel"));
  assert.ok(!fs.readFileSync(s.file(), "utf8").includes("zebra"));
});

test("empty or missing CEO id file writes nothing", () => {
  const s = setup(); fs.writeFileSync(s.idFile, "\n");
  s.h.messageReceived({ content: "ping", senderId: "", }, { channelId: "slack", accountId: "cfo" });
  s.h.messageReceived({ content: "ping", senderId: "UX" }, { channelId: "slack", accountId: "cfo" });
  fs.rmSync(s.idFile); s.h.messageReceived({ content: "ping", senderId: "UX" }, { channelId: "slack", accountId: "cfo" });
  assert.equal(s.read().length, 0);
});

test("write failure is swallowed and counted", () => {
  const s = setup(); fs.mkdirSync(path.dirname(s.dir), { recursive: true }); fs.writeFileSync(s.dir, "i am a file, not a folder");
  const warned = []; const h = createHandlers({ dir: s.dir, ceoIdFile: s.idFile, now: () => T, logger: { warn: (m) => warned.push(m) } });
  assert.doesNotThrow(() => h.afterToolCall(send(), { agentId: "coo" }));
  assert.equal(h.stats.errors, 1); assert.equal(warned.length, 1); assert.ok(!warned[0].includes("zebra"));
});

test("month rollover starts a new file with its own header", () => {
  const s = setup(); s.h.afterToolCall(send(), { agentId: "coo" });
  s.setNow(Date.UTC(2026, 11, 1, 6, 0, 0)); s.h.afterToolCall(send(), { agentId: "coo" });
  assert.equal(s.read("2026-11").length, 2); assert.equal(s.read("2026-12")[0], "# send log (written by code, no message text) - 2026-12"); assert.equal(s.read("2026-12").length, 2);
});

test("AST month boundary: 03:30 UTC on the 1st is still the previous month", () => {
  const s = setup(); s.setNow(Date.UTC(2026, 11, 1, 3, 30, 0)); s.h.afterToolCall(send(), { agentId: "coo" });
  assert.equal(s.read("2026-11").length, 2); assert.equal(s.read("2026-12").length, 0);
});
