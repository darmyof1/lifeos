// Privacy gate, JavaScript port of src/lifeos/router/gate.py (ADR-0003, APR-0112, APR-0113). Ported line by line; tests/unit/test_gate_parity.py
// runs the same case table (tests/data/gate_cases.json) through both and compares every answer. Pure: no network, no model call, no file write
// (it reads the policy file). No OpenClaw imports, so it is tested away from the gateway.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

export const POLICY_DEFAULT = path.join(path.dirname(fileURLToPath(import.meta.url)), "privacy.yaml");
export const LEVELS = ["high", "medium", "low"];
export const COMPLEXITIES = ["low", "medium", "high", "critical"];
export const DESTINATIONS = ["local", "cloud"];
export const CHANNELS = ["slack", "cli", "api"];
export const OVERRIDE_MAX_AGE_SECONDS = 600;

export class PolicyError extends Error {}

const isDict = (x) => x !== null && typeof x === "object" && !Array.isArray(x);
const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
const absent = (v) => v === undefined || v === null;

export function parsePolicyText(text) {
  const root = {};
  const stack = [[-1, root]];
  const lines = text.split(/\r?\n|\r/);            // like Python splitlines for the files we read
  for (let n = 1; n <= lines.length; n++) {
    const raw = lines[n - 1];
    const line = raw.includes("  #") ? raw.split("  #")[0] : raw;
    const lstripped = line.replace(/^\s+/, "");
    if (lstripped.startsWith("#") || line.trim() === "") continue;
    const lead = line.slice(0, line.length - lstripped.length);
    if (lead.includes("\t")) throw new PolicyError("tab indentation on line " + n);
    const indent = line.length - line.replace(/^ +/, "").length;
    const body = line.trim();
    if (!body.includes(":")) throw new PolicyError("line " + n + " has no key");
    const i = body.indexOf(":");
    const key = body.slice(0, i).trim();
    let val = body.slice(i + 1).trim();
    if (key === "") throw new PolicyError("empty key on line " + n);
    while (stack.length && stack[stack.length - 1][0] >= indent) stack.pop();
    if (!stack.length) throw new PolicyError("bad indentation on line " + n);
    const parent = stack[stack.length - 1][1];
    if (has(parent, key)) throw new PolicyError("duplicate key " + key + " on line " + n);
    if (val === "") {
      const child = {};
      parent[key] = child;
      stack.push([indent, child]);
    } else {
      if (val.length >= 2 && val[0] === val[val.length - 1] && "\"'".includes(val[0])) val = val.slice(1, -1);
      parent[key] = val;
    }
  }
  return root;
}

function get(d, ...p) {
  for (const k of p) {
    if (!isDict(d) || !has(d, k)) throw new PolicyError("policy lacks " + p.join("."));
    d = d[k];
  }
  return d;
}

export function loadPolicy(file = null) {
  const p = file || POLICY_DEFAULT;
  let text;
  try {
    text = fs.readFileSync(p, { encoding: "utf8" });
  } catch (e) {
    throw new PolicyError("policy unreadable");
  }
  const pol = parsePolicyText(text);
  if (get(pol, "precedence") !== "privacy_wins") throw new PolicyError("precedence is not privacy_wins");
  if (get(pol, "gate", "high", "cloud") !== "denied") throw new PolicyError("gate.high.cloud is not denied");
  if (get(pol, "gate", "medium", "cloud") !== "low_sensitivity_only") throw new PolicyError("gate.medium.cloud is not low_sensitivity_only");
  if (get(pol, "gate", "low", "cloud") !== "allowed") throw new PolicyError("gate.low.cloud is not allowed");
  if (get(pol, "channels", "slack", "model_calls") !== "gate_applies") throw new PolicyError("the Slack exemption must not reach model calls");
  if (get(pol, "triage", "runs_before_gate") !== "true") throw new PolicyError("triage must run before the gate");
  return pol;
}

function norm(value, allowed) {
  if (typeof value === "string" && allowed.includes(value.trim().toLowerCase())) return value.trim().toLowerCase();
  return null;
}

function hash(value) {
  let s;
  if (typeof value === "boolean") s = value ? "True" : "False";
  else s = String(value);
  return crypto.createHash("sha256").update(s, "utf8").digest("hex").slice(0, 16);
}

export function requestHash(requestId) {
  const ok = typeof requestId === "string" || typeof requestId === "boolean" || (typeof requestId === "number" && Number.isInteger(requestId));
  return hash(ok ? requestId : "");
}

function answer(allow, reason, req, used, extra = {}) {
  req = isDict(req) ? req : {};
  const log = {
    event: "privacy_gate",
    request_hash: requestHash(has(req, "request_id") ? req.request_id : ""),
    privacy_in: norm(req.privacy, LEVELS) || (absent(req.privacy) ? "absent" : "invalid"),
    privacy_used: used,
    complexity: norm(req.complexity, COMPLEXITIES) || "unknown",
    destination: norm(req.destination, DESTINATIONS) || "invalid",
    channel: norm(req.channel, CHANNELS) || (absent(req.channel) ? "absent" : "other"),
    decision: allow ? "allow" : "deny",
    reason,
    override_requested: req.override === true,
    override_confirmed: extra.override_confirmed || false,
  };
  return { allow, reason, privacy_used: used, ciso_notice: extra.ciso_notice || null, budget_gate: extra.budget_gate || false, log };
}

function epoch(value) {
  if (typeof value === "boolean") return null;
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.endsWith("Z")) {
    const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z$/.exec(value);
    if (!m) return null;
    const [y, mo, d, h, mi, s] = m.slice(1).map(Number);
    const t = Date.UTC(y, mo - 1, d, h, mi, s);
    const back = new Date(t);
    if (back.getUTCFullYear() !== y || back.getUTCMonth() !== mo - 1 || back.getUTCDate() !== d || back.getUTCHours() !== h ||
        back.getUTCMinutes() !== mi || back.getUTCSeconds() !== s) return null;
    return t / 1000;
  }
  return null;
}

function overrideCheck(req, now) {
  const c = req.confirmation;
  if (!(req.override === true && isDict(c) && c.confirmed === true && c.confirmed_by === "CEO" && typeof c.confirmation_id === "string" &&
        c.confirmation_id.trim() !== "")) return "override_without_confirmation";
  if (c.request_hash !== requestHash(has(req, "request_id") ? req.request_id : "")) return "override_confirmation_not_for_this_request";
  const at = epoch(c.confirmed_at);
  const current = epoch(now);
  if (at === null || current === null) return "override_confirmation_expired";
  const age = current - at;
  if (age < 0 || age > OVERRIDE_MAX_AGE_SECONDS) return "override_confirmation_expired";
  return null;
}

export function decide(request, policyPath = null, now = null) {
  try {
    loadPolicy(policyPath);
  } catch (e) {
    return answer(false, "policy_unreadable", request, "high");
  }
  try {
    if (!isDict(request)) return answer(false, "malformed_request", request, "high");
    const dest = norm(request.destination, DESTINATIONS);
    if (dest === null) return answer(false, "malformed_request", request, "high");
    const level = norm(request.privacy, LEVELS);
    const used = level || "high";
    if (dest === "local") return answer(true, "local_destination", request, used);
    if (used === "high") {
      if (request.override === true) {
        const problem = overrideCheck(request, now);
        if (problem === null) {
          const notice = { required: true, kind: "privacy_override", to: "CISO", request_hash: requestHash(has(request, "request_id") ? request.request_id : "") };
          return answer(true, "override_confirmed_by_ceo", request, used, { override_confirmed: true, ciso_notice: notice });
        }
        return answer(false, problem, request, used);
      }
      const reason = level === "high" ? "privacy_high_cloud_denied" : "privacy_missing_or_unknown_treated_as_high";
      return answer(false, reason, request, used);
    }
    if (used === "medium") {
      if (request.sensitivity === "low") return answer(true, "medium_low_sensitivity", request, used);
      return answer(false, "medium_not_low_sensitivity", request, used);
    }
    return answer(true, "privacy_low", request, used, { budget_gate: true });
  } catch (e) {
    return answer(false, "internal_error_fail_closed", request, "high");
  }
}
