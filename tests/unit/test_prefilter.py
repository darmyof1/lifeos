"""Unit tests for the rules-based privacy prefilter (src/lifeos/router/prefilter.py, APR-0113). Synthetic sentences only."""
import json, os, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lifeos.router import prefilter as pf  # noqa: E402

with open(os.path.join(ROOT, "tests", "data", "prefilter_cases.json"), encoding="utf-8") as fh:
    CASES = json.load(fh)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


class TableTests(unittest.TestCase):
    def test_at_least_forty_sentences(self):
        self.assertGreaterEqual(len(CASES), 40)
        self.assertEqual({c["truth"] for c in CASES}, {"high", "medium", "low"})

    def test_every_case_gets_the_label_the_table_expects(self):
        for c in CASES:
            r = pf.classify(c["channel"], c["agent"], c["text"])
            self.assertEqual(r["label"], c["expect"], c["text"])

    def test_no_leak_a_truly_high_sentence_is_never_below_high(self):
        for c in CASES:
            if c["truth"] == "high":
                self.assertEqual(pf.classify(c["channel"], c["agent"], c["text"])["label"], "high", c["text"])

    def test_false_blocks_are_the_four_named_near_misses_only(self):
        wrong = [c for c in CASES if c["truth"] != "high" and c["expect"] == "high"]
        self.assertEqual(len(wrong), 4, [c["text"] for c in wrong])
        self.assertTrue(all("near miss" in c["note"] for c in wrong))
        other = [c for c in CASES if c["truth"] != "high"]
        self.assertEqual(len(other), 17)          # the false-block rate in the report: 4 of 17

    def test_a_looser_label_than_the_truth_never_happens(self):
        rank = {"low": 0, "medium": 1, "high": 2}
        for c in CASES:
            self.assertGreaterEqual(rank[c["expect"]], rank[c["truth"]], c["text"])

    def test_each_category_is_covered(self):
        reasons = {pf.classify(c["channel"], c["agent"], c["text"])["reason"] for c in CASES}
        for r in ("category_health", "category_finance", "category_family", "category_journal", "agent_cho", "agent_cfo", "medium_topic", "low_topic",
                  "no_rule_matched_treated_as_high", "invalid_input_treated_as_high"):
            self.assertIn(r, reasons)


class RuleBehaviourTests(unittest.TestCase):
    def label(self, text, agent="coo", channel="slack"):
        return pf.classify(channel, agent, text)["label"]

    def test_case_plural_hyphen_and_curly_apostrophes(self):
        self.assertEqual(self.label("DOCTORS appointment"), "high")
        self.assertEqual(self.label("check-up tomorrow"), "high")
        self.assertEqual(self.label("check up tomorrow"), "high")
        self.assertEqual(self.label("It\u2019s my wife\u2019s day"), "high")

    def test_whole_words_only(self):
        self.assertEqual(self.label("What is the capital of France"), "low")
        self.assertEqual(self.label("Translate the word spouseless"), "low")        # not the word spouse

    def test_amounts_and_doses_are_high(self):
        for t in ("It costs $5", "send 20 dollars", "take 500 mg", "weighs 80 kg", "about 120 bpm"):
            self.assertEqual(self.label(t), "high", t)

    def test_high_wins_over_medium_and_low(self):
        self.assertEqual(self.label("Schedule my doctor meeting"), "high")
        self.assertEqual(self.label("Weather for my trip"), "medium")
        self.assertEqual(self.label("Weather and my wife"), "high")

    def test_cho_and_cfo_are_always_high(self):
        for agent in ("cho", "cfo", "CHO", " cfo "):
            self.assertEqual(self.label("What is the capital of France", agent=agent), "high")
        self.assertEqual(self.label("What is the capital of France", agent="cos"), "low")

    def test_unknown_agent_and_missing_agent(self):
        self.assertEqual(pf.classify("slack", "solo", "What is the capital of France")["reason"], "unknown_agent_treated_as_high")
        self.assertEqual(self.label("What is the capital of France", agent=None), "low")

    def test_invalid_input_is_high(self):
        for bad in (None, 5, [], {}, "", "   ", "x" * 200001):
            r = pf.classify("slack", "coo", bad)
            self.assertEqual(r["label"], "high", repr(bad)[:30])
            self.assertEqual(r["reason"], "invalid_input_treated_as_high")


class LogAndRulesFileTests(unittest.TestCase):
    def test_log_has_labels_and_a_hash_only(self):
        secret = "my private diary entry zx81"
        r = pf.classify("slack", "coo", secret)
        blob = json.dumps(r)
        self.assertNotIn(secret, blob)
        self.assertNotIn("diary", blob.replace("category_journal", ""))
        self.assertEqual(sorted(r["log"]), sorted(["event", "label", "reason", "channel", "agent", "text_hash"]))
        self.assertEqual(len(r["log"]["text_hash"]), 16)

    def test_odd_channel_and_agent_names_are_not_copied(self):
        r = pf.classify("some-private-channel", "secret-agent-name", "What is the capital of France")
        self.assertNotIn("private", json.dumps(r["log"]))
        self.assertEqual(r["log"]["channel"], "other")
        self.assertEqual(r["log"]["agent"], "other")

    def test_the_same_input_gives_the_same_answer(self):
        self.assertEqual(pf.classify("slack", "coo", "Plan the doctor visit"), pf.classify("slack", "coo", "Plan the doctor visit"))

    def test_missing_or_broken_rules_file_makes_everything_high(self):
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        for name, text in (("none.json", None), ("empty.json", ""), ("junk.json", "{not json"), ("short.json", "{\"high\": {}}"),
                           ("nolists.json", json.dumps({"high_agents": [], "high": {"health": [], "finance": [], "family": [], "journal": []},
                                                        "high_patterns": [], "medium": [], "low": []}))):
            path = os.path.join(d, name)
            if text is not None:
                with open(path, "w") as fh:
                    fh.write(text)
            r = pf.classify("slack", "coo", "What is the capital of France", rules_path=path)
            self.assertEqual(r["label"], "high", name)
            self.assertEqual(r["reason"], "rules_unreadable_treated_as_high", name)

    def test_rules_file_shape_and_readability(self):
        d = json.loads(read("src/lifeos/router/prefilter_rules.json"))
        self.assertEqual(set(d["high"]), {"health", "finance", "family", "journal"})
        self.assertEqual(sorted(d["high_agents"]), ["cfo", "cho"])
        for k in ("health", "finance", "family", "journal"):
            self.assertGreaterEqual(len(d["high"][k]), 4)
            self.assertTrue(all(isinstance(x, str) and x == x.lower() for x in d["high"][k]), k)

    def test_the_module_has_no_network_or_model_imports(self):
        src = read("src/lifeos/router/prefilter.py")
        for word in ("import socket", "import requests", "import urllib", "import http", "subprocess", "openai", "anthropic"):
            self.assertNotIn(word, src)
        self.assertNotIn("print(", src)


if __name__ == "__main__":
    unittest.main()
