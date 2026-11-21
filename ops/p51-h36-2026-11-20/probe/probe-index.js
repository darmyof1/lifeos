// Throwaway observe-only probe (handover 36). Writes: time, hook, tool, agent id, masked session-key shape, field NAMES, text LENGTHS, run-id token. Never text.
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import fs from "node:fs";
const OUT = process.env.PROBE36_OUT || "/tmp/probe36.jsonl";
const RUN = /coo-\d{8}-\d{4}/;
const mask = (k) => typeof k === "string" ? k.replace(/(channel|thread):[^:]+/g, "$1:<id>").replace(/[A-Z0-9]{9,}/g, "<id>").replace(/\d{6,}(\.\d+)?/g, "<n>") : undefined;
const shape = (o) => { if (!o || typeof o !== "object") return typeof o; const r = {}; for (const [k, v] of Object.entries(o)) r[k] = typeof v === "string" ? "str(" + v.length + ")" : Array.isArray(v) ? "arr(" + v.length + ")" : v && typeof v === "object" ? "obj" : typeof v; return r; };
const runTok = (o) => { try { const m = JSON.stringify(o).match(RUN); return m ? m[0] : null; } catch { return null; } };
function rec(hook, e, c) {
  try {
    const p = e && e.params;
    const line = { t: new Date().toISOString(), hook, tool: e && e.toolName, ctxAgent: c && c.agentId, ctxSession: mask(c && c.sessionKey), ctxRunIdPresent: !!(c && c.runId) || !!(e && e.runId),
      evKeys: shape(e), ctxKeys: Object.keys(c || {}), paramsShape: p ? shape(p) : undefined,
      paramTarget: p ? mask(p.sessionKey || p.agentId || p.target || p.to) : undefined,
      msgLen: p && typeof p.message === "string" ? p.message.length : (e && typeof e.content === "string" ? e.content.length : undefined),
      runToken: p ? runTok(p) : runTok(e && e.content), provenance: c && c.inputProvenance ? { kind: c.inputProvenance.kind, tool: c.inputProvenance.sourceTool, src: mask(c.inputProvenance.sourceSessionKey) } : undefined,
      resultKeys: e && e.result && typeof e.result === "object" ? Object.keys(e.result) : undefined, err: !!(e && e.error) };
    fs.appendFileSync(OUT, JSON.stringify(line) + "\n");
  } catch (x) { try { fs.appendFileSync(OUT, JSON.stringify({ hook, probeError: String(x && x.message).slice(0, 80) }) + "\n"); } catch {} }
}
export default definePluginEntry({
  id: "probe36", name: "probe36", description: "observe-only probe",
  register(api) {
    for (const h of ["before_tool_call", "after_tool_call", "message_received", "before_dispatch", "before_prompt_build", "before_agent_run", "agent_end", "session_start", "subagent_spawned", "message_sending", "message_sent"]) {
      api.on(h, (e, c) => { rec(h, e, c); });   // returns nothing
    }
  },
});
