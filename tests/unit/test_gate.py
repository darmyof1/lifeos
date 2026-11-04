"""Unit tests for the privacy gate (src/lifeos/router/gate.py, ADR-0003, APR-0112). Table of cases; no network, no model."""
import json, os, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lifeos.router import gate  # noqa: E402

POLICY = os.path.join(ROOT, "contracts", "policy", "privacy.yaml")
CONFIRM = {"confirmed": True, "confirmed_by": "CEO", "confirmation_id": "c-1"}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def build(fields):
    """A request from a case's fields; None means the privacy key is absent altogether."""
    r = req() if fields is None else req(**fields)
    if fields is None:
        del r["privacy"]
    return r


def req(**kw):
    r = {"request_id": "r-1", "privacy": "low", "complexity": "low", "destination": "cloud", "channel": "cli"}
    r.update(kw)
    return r


class TableTests(unittest.TestCase):
    CASES = [
        # name, request fields, allow, reason
        ("high privacy, cloud: denied", dict(privacy="high"), False, "privacy_high_cloud_denied"),
        ("high privacy, local: allowed", dict(privacy="high", destination="local"), True, "local_destination"),
        ("critical complexity with high privacy stays local", dict(privacy="high", complexity="critical"), False, "privacy_high_cloud_denied"),
        ("critical complexity with high privacy, local: allowed", dict(privacy="high", complexity="critical", destination="local"), True, "local_destination"),
        ("medium, low sensitivity, cloud: allowed", dict(privacy="medium", sensitivity="low"), True, "medium_low_sensitivity"),
        ("medium, no sensitivity, cloud: denied", dict(privacy="medium"), False, "medium_not_low_sensitivity"),
        ("medium, other sensitivity, cloud: denied", dict(privacy="medium", sensitivity="high"), False, "medium_not_low_sensitivity"),
        ("low privacy, cloud: allowed", dict(privacy="low"), True, "privacy_low"),
        ("missing level is high", dict(privacy=None), False, "privacy_missing_or_unknown_treated_as_high"),
        ("level key absent is high", None, False, "privacy_missing_or_unknown_treated_as_high"),
        ("unknown level is high", dict(privacy="secret"), False, "privacy_missing_or_unknown_treated_as_high"),
        ("unsure level is high", dict(privacy="unsure"), False, "privacy_missing_or_unknown_treated_as_high"),
        ("level of the wrong type is high", dict(privacy=3), False, "privacy_missing_or_unknown_treated_as_high"),
        ("level in capitals still reads as high", dict(privacy=" HIGH "), False, "privacy_high_cloud_denied"),
        ("Slack channel does not reach cloud model calls (high)", dict(privacy="high", channel="slack"), False, "privacy_high_cloud_denied"),
        ("Slack channel does not reach cloud model calls (missing level)", dict(privacy=None, channel="slack"), False, "privacy_missing_or_unknown_treated_as_high"),
        ("Slack channel does not loosen medium", dict(privacy="medium", channel="slack"), False, "medium_not_low_sensitivity"),
        ("override flag without confirmation: denied", dict(privacy="high", override=True), False, "override_without_confirmation"),
        ("override with an empty confirmation: denied", dict(privacy="high", override=True, confirmation={}), False, "override_without_confirmation"),
        ("override confirmed by someone else: denied", dict(privacy="high", override=True, confirmation=dict(CONFIRM, confirmed_by="COO")), False, "override_without_confirmation"),
        ("override with confirmed as a string: denied", dict(privacy="high", override=True, confirmation=dict(CONFIRM, confirmed="true")), False, "override_without_confirmation"),
        ("override with no confirmation ID: denied", dict(privacy="high", override=True, confirmation={"confirmed": True, "confirmed_by": "CEO"}), False, "override_without_confirmation"),
        ("override with a truthy non-True flag: denied", dict(privacy="high", override="yes", confirmation=CONFIRM), False, "privacy_high_cloud_denied"),
        ("confirmation without the override flag: denied", dict(privacy="high", confirmation=CONFIRM), False, "privacy_high_cloud_denied"),
        ("override with CEO confirmation: allowed", dict(privacy="high", override=True, confirmation=CONFIRM), True, "override_confirmed_by_ceo"),
        ("override cannot unlock medium without low sensitivity", dict(privacy="medium", override=True, confirmation=CONFIRM), False, "medium_not_low_sensitivity"),
        ("destination missing: malformed", dict(destination=None), False, "malformed_request"),
        ("destination unknown: malformed", dict(destination="mars"), False, "malformed_request"),
        ("complexity unknown does not loosen high", dict(privacy="high", complexity="trivial"), False, "privacy_high_cloud_denied"),
    ]

    def test_table(self):
        for name, fields, allow, reason in self.CASES:
            a = gate.decide(build(fields), POLICY)
            self.assertEqual((a["allow"], a["reason"]), (allow, reason), name)

    def test_not_a_dict_is_denied(self):
        for bad in (None, "cloud", 5, [], [req()], ("x",)):
            a = gate.decide(bad, POLICY)
            self.assertFalse(a["allow"], repr(bad))
            self.assertEqual(a["reason"], "malformed_request")

    def test_allow_is_a_real_bool_and_only_set_by_a_rule(self):
        for _, fields, allow, _ in self.CASES:
            self.assertIs(gate.decide(build(fields), POLICY)["allow"], allow)


class OverrideAndLogTests(unittest.TestCase):
    def test_override_logs_and_notifies_the_ciso(self):
        a = gate.decide(req(privacy="high", override=True, confirmation=CONFIRM), POLICY)
        self.assertTrue(a["allow"])
        self.assertEqual(a["ciso_notice"]["kind"], "privacy_override")
        self.assertEqual(a["ciso_notice"]["to"], "CISO")
        self.assertTrue(a["log"]["override_requested"])
        self.assertTrue(a["log"]["override_confirmed"])
        self.assertEqual(a["log"]["reason"], "override_confirmed_by_ceo")

    def test_no_notice_when_nothing_was_overridden(self):
        for f in (dict(privacy="low"), dict(privacy="high"), dict(privacy="high", override=True)):
            self.assertIsNone(gate.decide(req(**f), POLICY)["ciso_notice"])

    def test_a_denied_override_is_still_logged_as_requested(self):
        a = gate.decide(req(privacy="high", override=True), POLICY)
        self.assertFalse(a["allow"])
        self.assertTrue(a["log"]["override_requested"])
        self.assertFalse(a["log"]["override_confirmed"])

    def test_log_has_hashes_and_labels_only(self):
        secret = "my-private-request-text-1234"
        a = gate.decide(req(request_id=secret, privacy="high", text=secret, prompt=secret, content=secret), POLICY)
        blob = json.dumps(a)
        self.assertNotIn(secret, blob)
        self.assertEqual(sorted(a["log"]), sorted(["event", "request_hash", "privacy_in", "privacy_used", "complexity", "destination",
                                                   "channel", "decision", "reason", "override_requested", "override_confirmed"]))
        self.assertEqual(len(a["log"]["request_hash"]), 16)

    def test_odd_labels_are_not_copied_into_the_log(self):
        a = gate.decide(req(privacy="SOME FREE TEXT", channel="some-private-channel", complexity="x y z"), POLICY)
        blob = json.dumps(a["log"])
        for s in ("FREE TEXT", "private-channel", "x y z"):
            self.assertNotIn(s, blob)
        self.assertEqual((a["log"]["privacy_in"], a["log"]["channel"], a["log"]["complexity"]), ("invalid", "other", "unknown"))

    def test_low_privacy_cloud_asks_for_the_budget_gate(self):
        self.assertTrue(gate.decide(req(privacy="low"), POLICY)["budget_gate"])
        self.assertFalse(gate.decide(req(privacy="high"), POLICY)["budget_gate"])

    def test_the_same_request_gives_the_same_answer(self):
        r = req(privacy="medium", sensitivity="low")
        self.assertEqual(gate.decide(r, POLICY), gate.decide(dict(r), POLICY))

    def test_the_request_is_not_changed(self):
        r = req(privacy="high", override=True, confirmation=dict(CONFIRM))
        before = json.dumps(r, sort_keys=True)
        gate.decide(r, POLICY)
        self.assertEqual(before, json.dumps(r, sort_keys=True))


class PolicyTests(unittest.TestCase):
    def policy_file(self, text):
        fh = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
        fh.write(text)
        fh.close()
        self.addCleanup(os.unlink, fh.name)
        return fh.name

    def denied(self, path):
        for f in (dict(privacy="low"), dict(privacy="high", destination="local"), dict(privacy="high")):
            a = gate.decide(req(**f), path)
            self.assertFalse(a["allow"], f)
            self.assertEqual(a["reason"], "policy_unreadable")

    def test_the_real_policy_loads(self):
        p = gate.load_policy(POLICY)
        self.assertEqual(p["precedence"], "privacy_wins")
        self.assertEqual(p["gate"]["high"]["cloud"], "denied")

    def test_missing_file_denies_everything(self):
        self.denied(os.path.join(tempfile.gettempdir(), "no-such-privacy-policy.yaml"))

    def test_a_directory_instead_of_a_file_denies(self):
        self.denied(tempfile.gettempdir())

    def test_empty_and_garbage_files_deny(self):
        for text in ("", "not yaml at all", "a: b\n  c\n", "\x00\x01\x02", "gate:\n\thigh:\n"):
            self.denied(self.policy_file(text))

    def test_a_weakened_policy_denies(self):
        good = read(POLICY)
        for old, new in (("cloud: denied", "cloud: allowed"), ("precedence: privacy_wins", "precedence: complexity_wins"),
                         ("low_sensitivity_only", "anything"), ("model_calls: gate_applies", "model_calls: exempt"),
                         ("runs_before_gate: true", "runs_before_gate: false")):
            self.assertIn(old, good)
            self.denied(self.policy_file(good.replace(old, new, 1)))

    def test_a_missing_section_denies(self):
        good = read(POLICY)
        self.denied(self.policy_file(good.replace("channels:", "chans:", 1)))

    def test_a_duplicate_key_denies(self):
        good = read(POLICY)
        self.denied(self.policy_file(good + "\nprecedence: privacy_wins\n"))

    def test_the_minimal_reader_agrees_with_pyyaml_on_the_real_file(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is not installed")
        text = read(POLICY)
        mine, theirs = gate.parse_policy_text(text), yaml.safe_load(text)

        def norm(x):
            if isinstance(x, dict):
                return {str(k): norm(v) for k, v in x.items()}
            return str(x).lower() if isinstance(x, bool) else str(x)
        self.assertEqual(norm(mine), norm(theirs))

    def test_the_gate_does_not_import_a_network_or_model_library(self):
        src = read(os.path.join(ROOT, "src", "lifeos", "router", "gate.py"))
        for word in ("import socket", "import requests", "import urllib", "import http", "subprocess", "openai", "anthropic"):
            self.assertNotIn(word, src)


if __name__ == "__main__":
    unittest.main()
