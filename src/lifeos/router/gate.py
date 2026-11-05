"""Privacy gate (ADR-0003, APR-0112). A pure function: no network, no model call, no file write.

It runs after triage and before any adapter. It reads the privacy level that triage produced and the rules in
contracts/policy/privacy.yaml. A high-privacy request cannot reach a cloud adapter, and no prompt text can change that:
the gate never sees the prompt, only the labels. Privacy wins over complexity (APR-0007). A missing, unknown or unsure label
counts as high. The CEO can override only with an explicit confirmation, which the log record shows; the CISO notice is a
field in the answer (nothing is sent from here). Any malformed input or unreadable policy denies.

STATUS: built and tested, NOT wired. No router, adapter or agent calls it yet (see research/ and the Loop 3 report).
"""
import datetime
import hashlib
import os

POLICY_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "contracts", "policy", "privacy.yaml")

LEVELS = ("high", "medium", "low")
COMPLEXITIES = ("low", "medium", "high", "critical")
DESTINATIONS = ("local", "cloud")
CHANNELS = ("slack", "cli", "api")
OVERRIDE_MAX_AGE_SECONDS = 600       # APR-0113: an override confirmation is good for 10 minutes and for one request only


class PolicyError(Exception):
    """The policy file is missing, unreadable, malformed or says something this gate does not implement."""


def parse_policy_text(text):
    """Minimal reader for the shape of privacy.yaml: nested maps by two-space (or any consistent) indentation, 'key: value'
    lines, '#' comments. No lists, anchors or multi-line values. Anything else raises PolicyError (fail closed)."""
    root, stack = {}, [(-1, {})]
    stack[0] = (-1, root)
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("  #", 1)[0] if "  #" in raw else raw
        if line.lstrip().startswith("#") or not line.strip():
            continue
        if "\t" in line[: len(line) - len(line.lstrip())]:
            raise PolicyError("tab indentation on line %d" % n)
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if ":" not in body:
            raise PolicyError("line %d has no key" % n)
        key, _, val = body.partition(":")
        key, val = key.strip(), val.strip()
        if not key:
            raise PolicyError("empty key on line %d" % n)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            raise PolicyError("bad indentation on line %d" % n)
        parent = stack[-1][1]
        if key in parent:
            raise PolicyError("duplicate key %r on line %d" % (key, n))
        if val == "":
            child = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            parent[key] = val
    return root


def _get(d, *path):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            raise PolicyError("policy lacks " + ".".join(path))
        d = d[p]
    return d


def load_policy(path=None):
    """Read and check the policy. Raises PolicyError on anything unexpected."""
    p = path or POLICY_DEFAULT
    try:
        with open(p, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise PolicyError("policy unreadable: %s" % type(exc).__name__)
    pol = parse_policy_text(text)
    if _get(pol, "precedence") != "privacy_wins":
        raise PolicyError("precedence is not privacy_wins")
    if _get(pol, "gate", "high", "cloud") != "denied":
        raise PolicyError("gate.high.cloud is not denied")
    if _get(pol, "gate", "medium", "cloud") != "low_sensitivity_only":
        raise PolicyError("gate.medium.cloud is not low_sensitivity_only")
    if _get(pol, "gate", "low", "cloud") != "allowed":
        raise PolicyError("gate.low.cloud is not allowed")
    if _get(pol, "channels", "slack", "model_calls") != "gate_applies":
        raise PolicyError("the Slack exemption must not reach model calls")
    if _get(pol, "triage", "runs_before_gate") != "true":
        raise PolicyError("triage must run before the gate")
    return pol


def _norm(value, allowed):
    if isinstance(value, str) and value.strip().lower() in allowed:
        return value.strip().lower()
    return None


def _hash(value):
    return hashlib.sha256(str(value).encode("utf-8", "replace")).hexdigest()[:16]


def _answer(allow, reason, req, used, **extra):
    """The log record carries labels and a hash of the request ID only: no content, no text, no names."""
    req = req if isinstance(req, dict) else {}
    log = {
        "event": "privacy_gate",
        "request_hash": request_hash(req.get("request_id", "")),
        "privacy_in": _norm(req.get("privacy"), LEVELS) or ("absent" if req.get("privacy") is None else "invalid"),
        "privacy_used": used,
        "complexity": _norm(req.get("complexity"), COMPLEXITIES) or "unknown",
        "destination": _norm(req.get("destination"), DESTINATIONS) or "invalid",
        "channel": _norm(req.get("channel"), CHANNELS) or ("absent" if req.get("channel") is None else "other"),
        "decision": "allow" if allow else "deny",
        "reason": reason,
        "override_requested": req.get("override") is True,
        "override_confirmed": extra.get("override_confirmed", False),
    }
    out = {"allow": allow, "reason": reason, "privacy_used": used, "ciso_notice": extra.get("ciso_notice"),
           "budget_gate": extra.get("budget_gate", False), "log": log}
    return out


def request_hash(request_id):
    """The short hash the gate logs for a request ID. A confirmation must carry this value to name the request."""
    return _hash(request_id if isinstance(request_id, (str, int)) else "")


def _epoch(value):
    """Seconds since 1970 from a number or an ISO 8601 UTC string ending in Z; None if it is neither."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.endswith("Z"):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
        except ValueError:
            return None
    return None


def _override_check(req, now):
    """Return None if the override is valid, else the reason code. A valid override: the flag is True, the confirmation is by the CEO with a
    confirmation ID, it names THIS request (request_hash equals the request's hash) and it is not older than 10 minutes (and not from
    the future). `now` is passed in by the caller (seconds or an ISO Z string) so the gate stays a pure function; no `now` means unverifiable."""
    c = req.get("confirmation")
    if not (req.get("override") is True and isinstance(c, dict) and c.get("confirmed") is True and c.get("confirmed_by") == "CEO"
            and isinstance(c.get("confirmation_id"), str) and c.get("confirmation_id").strip() != ""):
        return "override_without_confirmation"
    if c.get("request_hash") != request_hash(req.get("request_id", "")):
        return "override_confirmation_not_for_this_request"
    at, current = _epoch(c.get("confirmed_at")), _epoch(now)
    if at is None or current is None:
        return "override_confirmation_expired"
    age = current - at
    if age < 0 or age > OVERRIDE_MAX_AGE_SECONDS:
        return "override_confirmation_expired"
    return None


def decide(request, policy_path=None, now=None):
    """Return the gate's answer. Never raises. allow is True only when every rule is met. `now` is only used to check an override's age."""
    try:
        policy = load_policy(policy_path)
    except PolicyError:
        return _answer(False, "policy_unreadable", request, "high")
    except Exception:
        return _answer(False, "policy_unreadable", request, "high")
    try:
        if not isinstance(request, dict):
            return _answer(False, "malformed_request", request, "high")
        dest = _norm(request.get("destination"), DESTINATIONS)
        if dest is None:
            return _answer(False, "malformed_request", request, "high")
        level = _norm(request.get("privacy"), LEVELS)
        used = level or "high"                      # missing, unknown or unsure means high (ADR-0003)
        if dest == "local":
            return _answer(True, "local_destination", request, used)
        # destination is cloud. Complexity and channel never loosen anything: privacy wins, and the Slack exemption
        # (privacy.yaml channels.slack) covers private data in private channels only, not cloud model calls.
        if used == "high":
            if request.get("override") is True:
                problem = _override_check(request, now)
                if problem is None:
                    notice = {"required": True, "kind": "privacy_override", "to": "CISO", "request_hash": request_hash(request.get("request_id", ""))}
                    return _answer(True, "override_confirmed_by_ceo", request, used, override_confirmed=True, ciso_notice=notice)
                return _answer(False, problem, request, used)
            reason = "privacy_high_cloud_denied" if level == "high" else "privacy_missing_or_unknown_treated_as_high"
            return _answer(False, reason, request, used)
        if used == "medium":
            if request.get("sensitivity") == "low":
                return _answer(True, "medium_low_sensitivity", request, used)
            return _answer(False, "medium_not_low_sensitivity", request, used)
        return _answer(True, "privacy_low", request, used, budget_gate=True)
    except Exception:
        return _answer(False, "internal_error_fail_closed", request, "high")
