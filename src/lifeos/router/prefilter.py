"""Privacy prefilter (ADR-0003, ADR-0004, APR-0113): a rules-only label for a turn BEFORE the gate. A pure function: no network, no model call,
no file write. Input: channel, agent and the turn text. Output: a label (high, medium or low), a reason code and a log record.

Rules live in one data file the CEO can read and edit: src/lifeos/router/prefilter_rules.json (health, finance, family and journal words are
high; the CHO and CFO agents are high because their channels carry health and finance topics). Conservative on purpose: any doubt means
high. A turn is low only if it matches a low topic and nothing else; medium only if it matches a medium word and no high word. The text is
matched in memory, never stored or logged: the log record holds labels and a short hash only. If the rules file is unreadable or malformed,
every turn is high.

STATUS: built and tested, NOT wired into the live gateway.
"""
import hashlib
import json
import os
import re

RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefilter_rules.json")
AGENTS = ("coo", "cho", "cos", "cfo")
CHANNELS = ("slack", "cli", "api")
MAX_TEXT = 200000


class RulesError(Exception):
    pass


def _phrase_regex(terms):
    """One regex for a list of words/phrases: whole words, any case, optional plural s/es, spaces and hyphens interchangeable."""
    parts = []
    for t in terms:
        t = t.strip().lower()
        if not t:
            continue
        parts.append(r"[ \-]+".join(re.escape(x) for x in re.split(r"[ \-]+", t)))
    if not parts:
        return None
    return re.compile(r"(?<![a-z0-9])(?:" + "|".join(parts) + r")(?:s|es)?(?![a-z0-9])")


def load_rules(path=None):
    try:
        with open(path or RULES_FILE, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        high = {k: _phrase_regex(v) for k, v in d["high"].items()}
        if set(high) != {"health", "finance", "family", "journal"} or not all(high.values()):
            raise RulesError("high categories")
        return {
            "high_agents": tuple(str(a).lower() for a in d["high_agents"]),
            "high": high,
            "patterns": [re.compile(p, re.I) for p in d["high_patterns"]],
            "medium": _phrase_regex(d["medium"]),
            "low": _phrase_regex(d["low"]),
        }
    except Exception as exc:
        raise RulesError(type(exc).__name__)


def _norm(text):
    return text.replace("\u2019", "'").replace("\u2018", "'").lower()


def _hash(text):
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


def _known(value, allowed):
    return value.strip().lower() if isinstance(value, str) and value.strip().lower() in allowed else None


def _result(label, reason, channel, agent, text):
    h = _hash(text) if isinstance(text, str) else _hash("")
    return {"label": label, "reason": reason,
            "log": {"event": "privacy_prefilter", "label": label, "reason": reason,
                    "channel": _known(channel, CHANNELS) or ("absent" if channel is None else "other"),
                    "agent": _known(agent, AGENTS) or ("absent" if agent is None else "other"),
                    "text_hash": h}}


def classify(channel, agent, text, rules_path=None):
    """Return {"label", "reason", "log"}. Never raises. Any doubt is high."""
    try:
        try:
            rules = load_rules(rules_path)
        except RulesError:
            return _result("high", "rules_unreadable_treated_as_high", channel, agent, text)
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
            return _result("high", "invalid_input_treated_as_high", channel, agent, text)
        a = _known(agent, AGENTS)
        if a is None and agent is not None:
            return _result("high", "unknown_agent_treated_as_high", channel, agent, text)
        if a in rules["high_agents"]:
            return _result("high", "agent_" + a, channel, agent, text)
        t = _norm(text)
        for cat, rx in rules["high"].items():
            if rx.search(t):
                return _result("high", "category_" + cat, channel, agent, text)
        for rx in rules["patterns"]:
            if rx.search(t):
                return _result("high", "category_amount_or_dose", channel, agent, text)
        if rules["medium"] and rules["medium"].search(t):
            return _result("medium", "medium_topic", channel, agent, text)
        if rules["low"] and rules["low"].search(t):
            return _result("low", "low_topic", channel, agent, text)
        return _result("high", "no_rule_matched_treated_as_high", channel, agent, text)
    except Exception:
        return _result("high", "internal_error_treated_as_high", channel, agent, text)
