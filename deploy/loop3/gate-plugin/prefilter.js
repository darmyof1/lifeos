// Privacy prefilter, JavaScript port of src/lifeos/router/prefilter.py (APR-0113). Same rules file (prefilter_rules.json, a byte-identical copy
// of src/lifeos/router/prefilter_rules.json, checked by a test). Pure: no network, no model call; the text is matched in memory and never stored
// or logged. The log record holds labels and a short hash. Any doubt, any error, an unreadable rules file: high.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

export const RULES_FILE = path.join(path.dirname(fileURLToPath(import.meta.url)), "prefilter_rules.json");
const AGENTS = ["coo", "cho", "cos", "cfo"];
const CHANNELS = ["slack", "cli", "api"];
const MAX_TEXT = 200000;

class RulesError extends Error {}

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\\-]/g, "\\$&");

function phraseRegex(terms) {
  const parts = [];
  for (let t of terms) {
    t = String(t).trim().toLowerCase();
    if (!t) continue;
    parts.push(t.split(/[ \-]+/).map(esc).join("[ \\-]+"));
  }
  if (!parts.length) return null;
  return new RegExp("(?<![a-z0-9])(?:" + parts.join("|") + ")(?:s|es)?(?![a-z0-9])");
}

export function loadRules(file = null) {
  try {
    const d = JSON.parse(fs.readFileSync(file || RULES_FILE, "utf8"));
    const high = {};
    for (const [k, v] of Object.entries(d.high)) high[k] = phraseRegex(v);
    const keys = Object.keys(high).sort().join(",");
    if (keys !== "family,finance,health,journal" || !Object.values(high).every(Boolean)) throw new RulesError("high categories");
    return {
      high_agents: d.high_agents.map((a) => String(a).toLowerCase()),
      high,
      patterns: d.high_patterns.map((p) => new RegExp(p, "i")),
      medium: phraseRegex(d.medium),
      low: phraseRegex(d.low),
    };
  } catch (e) {
    throw new RulesError(e && e.constructor ? e.constructor.name : "error");
  }
}

const normText = (t) => t.replace(/\u2019/g, "'").replace(/\u2018/g, "'").toLowerCase();
const hash = (t) => crypto.createHash("sha256").update(t, "utf8").digest("hex").slice(0, 16);
const known = (v, allowed) => (typeof v === "string" && allowed.includes(v.trim().toLowerCase()) ? v.trim().toLowerCase() : null);

function result(label, reason, channel, agent, text) {
  return {
    label, reason,
    log: {
      event: "privacy_prefilter", label, reason,
      channel: known(channel, CHANNELS) || (channel === undefined || channel === null ? "absent" : "other"),
      agent: known(agent, AGENTS) || (agent === undefined || agent === null ? "absent" : "other"),
      text_hash: hash(typeof text === "string" ? text : ""),
    },
  };
}

export function classify(channel, agent, text, rulesPath = null) {
  try {
    let rules;
    try {
      rules = loadRules(rulesPath);
    } catch (e) {
      return result("high", "rules_unreadable_treated_as_high", channel, agent, text);
    }
    if (typeof text !== "string" || text.trim() === "" || text.length > MAX_TEXT) return result("high", "invalid_input_treated_as_high", channel, agent, text);
    const a = known(agent, AGENTS);
    if (a === null && agent !== undefined && agent !== null) return result("high", "unknown_agent_treated_as_high", channel, agent, text);
    if (a !== null && rules.high_agents.includes(a)) return result("high", "agent_" + a, channel, agent, text);
    const t = normText(text);
    for (const [cat, rx] of Object.entries(rules.high)) if (rx.test(t)) return result("high", "category_" + cat, channel, agent, text);
    for (const rx of rules.patterns) if (rx.test(t)) return result("high", "category_amount_or_dose", channel, agent, text);
    if (rules.medium && rules.medium.test(t)) return result("medium", "medium_topic", channel, agent, text);
    if (rules.low && rules.low.test(t)) return result("low", "low_topic", channel, agent, text);
    return result("high", "no_rule_matched_treated_as_high", channel, agent, text);
  } catch (e) {
    return result("high", "internal_error_treated_as_high", channel, agent, text);
  }
}
