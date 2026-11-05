"""Regenerates tests/data/gate_cases.json from the Python gate. Run only when the gate's rules change on purpose:
   python3 tests/data/make_gate_cases.py
The table is shared by the Python gate tests, the JS gate tests and the parity test (tests/unit/test_gate_parity.py)."""
import json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lifeos.router import gate  # noqa: E402

NOW = 1_800_000_000
POLICY_TEXT = open(os.path.join(ROOT, "contracts", "policy", "privacy.yaml"), encoding="utf-8").read()


def confirm(rid="r-1", at=NOW - 60, **kw):
    c = {"confirmed": True, "confirmed_by": "CEO", "confirmation_id": "c-1", "request_hash": gate.request_hash(rid), "confirmed_at": at}
    c.update(kw)
    return c


def req(**kw):
    r = {"request_id": "r-1", "privacy": "low", "complexity": "low", "destination": "cloud", "channel": "cli"}
    r.update(kw)
    return r


def drop(r, k):
    r = dict(r)
    r.pop(k, None)
    return r


cases = []


def add(name, request, policy="real", now=NOW):
    cases.append({"name": name, "request": request, "now": now, "policy": policy})


add("high cloud", req(privacy="high"))
add("high local", req(privacy="high", destination="local"))
add("critical complexity high privacy cloud", req(privacy="high", complexity="critical"))
add("medium low sensitivity", req(privacy="medium", sensitivity="low"))
add("medium no sensitivity", req(privacy="medium"))
add("medium high sensitivity", req(privacy="medium", sensitivity="high"))
add("low cloud", req(privacy="low"))
add("low local", req(privacy="low", destination="local"))
add("privacy null", req(privacy=None))
add("privacy absent", drop(req(), "privacy"))
add("privacy unknown", req(privacy="secret"))
add("privacy unsure", req(privacy="unsure"))
add("privacy number", req(privacy=3))
add("privacy capitals and spaces", req(privacy=" HIGH "))
add("slack high", req(privacy="high", channel="slack"))
add("slack missing level", req(privacy=None, channel="slack"))
add("slack medium", req(privacy="medium", channel="slack"))
add("odd channel", req(privacy="low", channel="some-private-channel"))
add("channel absent", drop(req(), "channel"))
add("complexity unknown", req(privacy="high", complexity="trivial"))
add("complexity absent", drop(req(privacy="high"), "complexity"))
add("override no confirmation", req(privacy="high", override=True))
add("override empty confirmation", req(privacy="high", override=True, confirmation={}))
add("override by COO", req(privacy="high", override=True, confirmation=confirm(confirmed_by="COO")))
add("override confirmed string", req(privacy="high", override=True, confirmation=confirm(confirmed="true")))
add("override confirmed 1", req(privacy="high", override=True, confirmation=confirm(confirmed=1)))
add("override no id", req(privacy="high", override=True, confirmation=confirm(confirmation_id="")))
add("override id blank", req(privacy="high", override=True, confirmation=confirm(confirmation_id="   ")))
add("override flag string", req(privacy="high", override="yes", confirmation=confirm()))
add("confirmation without flag", req(privacy="high", confirmation=confirm()))
add("override valid", req(privacy="high", override=True, confirmation=confirm()))
add("override valid missing level", req(privacy=None, override=True, confirmation=confirm()))
add("override on medium", req(privacy="medium", override=True, confirmation=confirm()))
add("override other request", req(privacy="high", override=True, confirmation=confirm(rid="other")))
add("override no request hash", req(privacy="high", override=True, confirmation={k: v for k, v in confirm().items() if k != "request_hash"}))
add("override second request", req(request_id="r-2", privacy="high", override=True, confirmation=confirm()))
for age in (0, 599, 600, 601, 3600, -1, -600):
    add("override age %d" % age, req(privacy="high", override=True, confirmation=confirm(at=NOW - age)))
add("override now null", req(privacy="high", override=True, confirmation=confirm()), now=None)
add("override no time", req(privacy="high", override=True, confirmation={k: v for k, v in confirm().items() if k != "confirmed_at"}))
for bad in ("yesterday", "2026-11-04 08:00:00", "", None, True, [], {}):
    add("override bad time %r" % (bad,), req(privacy="high", override=True, confirmation=confirm(at=bad)))
add("override now string bad", req(privacy="high", override=True, confirmation=confirm()), now="soon")
add("override iso ok", req(privacy="high", override=True, confirmation=confirm(at="2027-01-15T07:55:00Z")), now="2027-01-15T08:00:00Z")
add("override iso too old", req(privacy="high", override=True, confirmation=confirm(at="2027-01-15T07:55:00Z")), now="2027-01-15T08:10:01Z")
add("override iso bad date", req(privacy="high", override=True, confirmation=confirm(at="2027-02-30T07:55:00Z")), now="2027-02-28T08:00:00Z")
add("destination missing", req(destination=None))
add("destination unknown", req(destination="mars"))
add("destination absent", drop(req(), "destination"))
add("request id absent", drop(req(privacy="low"), "request_id"))
add("request id number", req(request_id=7, privacy="low"))
add("request id bool", req(request_id=True, privacy="low"))
add("request id null", req(request_id=None, privacy="low"))
add("request id object", req(request_id={"a": 1}, privacy="low"))
for bad in (None, "cloud", 5, [], [req()]):
    add("not a dict %r" % (bad if not isinstance(bad, list) else "list"), bad)
add("extra text fields are ignored", req(privacy="high", text="private text", prompt="private prompt"))
add("policy missing file", req(privacy="low"), policy="missing")
add("policy empty", req(privacy="low"), policy={"text": ""})
add("policy garbage", req(privacy="low"), policy={"text": "not yaml at all"})
add("policy no colon line", req(privacy="low"), policy={"text": "a: b\n  c\n"})
add("policy tab", req(privacy="low"), policy={"text": "gate:\n\thigh:\n"})
for old, new in (("cloud: denied", "cloud: allowed"), ("precedence: privacy_wins", "precedence: complexity_wins"), ("low_sensitivity_only", "anything"),
                 ("model_calls: gate_applies", "model_calls: exempt"), ("runs_before_gate: true", "runs_before_gate: false")):
    assert old in POLICY_TEXT
    add("policy weakened: %s" % old, req(privacy="low"), policy={"replace": [old, new]})
add("policy missing section", req(privacy="low"), policy={"replace": ["channels:", "chans:"]})
add("policy duplicate key", req(privacy="low"), policy={"text": POLICY_TEXT + "\nprecedence: privacy_wins\n"})
add("policy quoted values", req(privacy="high"), policy={"replace": ["precedence: privacy_wins", "precedence: \"privacy_wins\""]})


def policy_file(spec, d):
    if spec == "real":
        return os.path.join(ROOT, "contracts", "policy", "privacy.yaml")
    if spec == "missing":
        return os.path.join(d, "no-such-file.yaml")
    p = os.path.join(d, "policy.yaml")
    text = spec["text"] if "text" in spec else POLICY_TEXT.replace(spec["replace"][0], spec["replace"][1], 1)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


if __name__ == "__main__":
    out = []
    with tempfile.TemporaryDirectory() as d:
        for c in cases:
            out.append(dict(c, expect=gate.decide(c["request"], policy_file(c["policy"], d), now=c["now"])))
    path = os.path.join(ROOT, "tests", "data", "gate_cases.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(len(out), "cases written")
