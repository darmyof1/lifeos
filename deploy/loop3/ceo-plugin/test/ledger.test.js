// Run: node --test test/   (from ~/handover/ceo-plugin). Fake sender IDs only.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createHandler, extractTokens, approveWord, sha256 } from "../ledger.js";

const FAKE_CEO = "UFAKECEO01", OTHER = "UFAKEOTHER2";
const ctx = { channelId: "slack", accountId: "default", conversationId: "CFAKECHAN01" };
function setup() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ceoledger-"));
  const idFile = path.join(dir, "ceo-slack-id"); fs.writeFileSync(idFile, FAKE_CEO + "\n", { mode: 0o600 });
  const ledger = path.join(dir, "ledger", "slack-ledger.jsonl");
  const h = createHandler({ ledgerPath: ledger, ceoIdFile: idFile, now: () => Date.UTC(2026, 9, 28, 1, 2, 3) });
  const lines = () => (fs.existsSync(ledger) ? fs.readFileSync(ledger, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
  return { dir, idFile, ledger, h, lines };
}
const ev = (over = {}) => ({ content: "Yes, approve deleting loop2-scn-021-cho-01", senderId: FAKE_CEO, messageId: "1792815144.482899", timestamp: 1, ...over });

test("a CEO message writes exactly one line with the fixed fields", async () => {
  const s = setup(); await s.h(ev(), ctx);
  const [l] = s.lines();
  assert.equal(s.lines().length, 1);
  assert.deepEqual(Object.keys(l), ["time", "channel", "account", "conversation", "message_id", "sender", "text_sha256", "event_tokens", "approve_word"]);
  assert.equal(l.time, "2026-10-28T01:02:03Z"); assert.equal(l.channel, "slack"); assert.equal(l.sender, "CEO");
  assert.deepEqual(l.event_tokens, ["loop2-scn-021-cho-01"]);
  assert.equal(l.text_sha256, sha256("Yes, approve deleting loop2-scn-021-cho-01"));
});

test("the text and the raw IDs are not stored", async () => {
  const s = setup(); await s.h(ev({ content: "secret words loop2-scn-021-cho-01" }), ctx);
  const raw = fs.readFileSync(s.ledger, "utf8");
  assert.ok(!raw.includes("secret words")); assert.ok(!raw.includes(FAKE_CEO)); assert.ok(!raw.includes("CFAKECHAN01"));
});

test("another sender, no sender, a non-Slack channel or empty text write nothing", async () => {
  const s = setup();
  await s.h(ev({ senderId: OTHER }), ctx); await s.h(ev({ senderId: undefined }), ctx);
  await s.h(ev(), { ...ctx, channelId: "webchat" }); await s.h(ev({ content: "" }), ctx); await s.h(null, ctx);
  assert.equal(s.lines().length, 0); assert.equal(s.h.stats.written, 0);
});

test("a duplicate message ID writes once, also after a restart (new handler, same ledger)", async () => {
  const s = setup(); await s.h(ev(), ctx); await s.h(ev(), ctx);
  assert.equal(s.lines().length, 1); assert.equal(s.h.stats.duplicates, 1);
  const h2 = createHandler({ ledgerPath: s.ledger, ceoIdFile: s.idFile }); await h2(ev(), ctx);
  assert.equal(s.lines().length, 1);
  await s.h(ev({ messageId: "1792815999.000001" }), ctx); assert.equal(s.lines().length, 2);
});

test("no CEO ID file or an empty one writes nothing", async () => {
  const s = setup(); fs.rmSync(s.idFile); await s.h(ev(), ctx);
  fs.writeFileSync(s.idFile, "\n"); await s.h(ev({ senderId: "" }), ctx);
  assert.equal(s.lines().length, 0);
});

test("an unwritable ledger directory writes nothing and does not throw", async () => {
  const s = setup(); fs.mkdirSync(path.dirname(s.ledger), { recursive: true, mode: 0o500 });
  fs.chmodSync(path.dirname(s.ledger), 0o500);
  const warnings = []; const h = createHandler({ ledgerPath: s.ledger, ceoIdFile: s.idFile, logger: { warn: (m) => warnings.push(m) } });
  if (process.getuid && process.getuid() === 0) return;   // root ignores modes
  await assert.doesNotReject(h(ev(), ctx));
  assert.equal(h.stats.errors, 1); assert.equal(h.stats.written, 0);
  assert.ok(warnings[0].includes("EACCES")); assert.ok(!warnings[0].includes("loop2"));
  fs.chmodSync(path.dirname(s.ledger), 0o700);
});

test("a logger that throws still does not throw into the caller", async () => {
  const s = setup(); fs.mkdirSync(path.dirname(s.ledger), { recursive: true }); fs.chmodSync(path.dirname(s.ledger), 0o500);
  const h = createHandler({ ledgerPath: s.ledger, ceoIdFile: s.idFile, logger: { warn() { throw new Error("x"); } } });
  if (process.getuid && process.getuid() === 0) return;
  await assert.doesNotReject(h(ev(), ctx)); fs.chmodSync(path.dirname(s.ledger), 0o700);
});

test("file and directory modes are 600 and 700", async () => {
  const s = setup(); await s.h(ev(), ctx);
  assert.equal(fs.statSync(s.ledger).mode & 0o777, 0o600); assert.equal(fs.statSync(path.dirname(s.ledger)).mode & 0o777, 0o700);
});

test("token extraction", () => {
  assert.deepEqual(extractTokens("Approve `loop2-scn-021-cho-01` and SEED-3, not 2026."), ["loop2-scn-021-cho-01", "seed-3"]);
  assert.deepEqual(extractTokens("abc-def no digits; 12345 no hyphen; a-1 ok? -9-"), ["a-1"].filter((t) => t.length >= 3));
  assert.deepEqual(extractTokens("x".repeat(70) + "-1"), []);
  assert.deepEqual(extractTokens("seed-3 seed-3 SEED-3"), ["seed-3"]);
  assert.deepEqual(extractTokens(undefined), []);
});

test("the plugin entry registers only message_received (needs the OpenClaw package on this VM)", async () => {
  const sdk = path.join(os.homedir(), ".npm-global/lib/node_modules/openclaw");
  if (!fs.existsSync(sdk)) return;
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ceoplug-"));
  for (const f of ["index.js", "ledger.js", "package.json"]) fs.copyFileSync(new URL("../" + f, import.meta.url), path.join(dir, f));
  fs.mkdirSync(path.join(dir, "node_modules")); fs.symlinkSync(sdk, path.join(dir, "node_modules", "openclaw"));
  const mod = await import(path.join(dir, "index.js"));
  const calls = []; const api = { logger: {}, on: (n, fn) => calls.push([n, typeof fn]) };
  for (const k of ["registerTool", "registerService", "registerHttpRoute", "registerCommand"]) api[k] = () => { throw new Error("must not be called: " + k); };
  const entry = mod.default; (entry.register ?? entry.default?.register)(api);
  assert.deepEqual(calls, [["message_received", "function"]]);
});

test("approve_word: true only for a whole-word approval with no blocking word", () => {
  const yes = ["approve loop2-x-01", "approved: loop2-x-01", "approve", "APPROVE loop2-x-01", "ApPrOvEd!", "  approve, loop2-x-01.  ",
    "Yes, approve deleting loop2-scn-021-cho-01", "I am approving loop2-x-01", "approve\nloop2-x-01", "\u201capprove loop2-x-01\u201d"];
  const no = ["do not approve loop2-x-01", "Do NOT approve loop2-x-01", "Reply: approve, explain more, or keep", "please keep it", "no", "",
    "approve loop2-x-01 but wait", "approve without delay", "don't approve loop2-x-01", "don\u2019t approve loop2-x-01", "can't approve",
    "never approve", "cancel, approve", "stop. approve", "hold off, approve", "I won't approve", "cannot approve", "approve? explain",
    "yes", "disapprove loop2-x-01", "approval loop2-x-01", "approves loop2-x-01", null, undefined];
  for (const t of yes) assert.equal(approveWord(t), true, JSON.stringify(t));
  for (const t of no) assert.equal(approveWord(t), false, JSON.stringify(t));
});

test("approve_word is written to the ledger line and the text is still not stored", async () => {
  const s = setup();
  await s.h(ev({ content: "approve loop2-x-01", messageId: "m1" }), ctx);
  await s.h(ev({ content: "do not approve loop2-x-01", messageId: "m2" }), ctx);
  await s.h(ev({ content: "Reply: approve, explain more, or keep", messageId: "m3" }), ctx);
  assert.deepEqual(s.lines().map((l) => l.approve_word), [true, false, false]);
  assert.ok(!fs.readFileSync(s.ledger, "utf8").includes("explain"));
});
