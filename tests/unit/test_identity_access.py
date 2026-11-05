"""Contract test for contracts/identity-access.yaml (APR-0112): the contract must not drift from the live-facts files in the repo."""
import ast, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AGENTS = ("coo", "cho", "cos", "cfo")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def split_flow(body):
    out, depth, cur, quote = [], 0, "", None
    for ch in body:
        if quote:
            cur += ch
            quote = None if ch == quote else quote
        elif ch in "\"'":
            quote = ch
            cur += ch
        elif ch in "[{":
            depth += 1
            cur += ch
        elif ch in "]}":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def value(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [value(x) for x in split_flow(v[1:-1])]
    if v.startswith("{") and v.endswith("}"):
        d = {}
        for item in split_flow(v[1:-1]):
            k, _, x = item.partition(":")
            d[scalar(k)] = value(x)
        return d
    return scalar(v)


def parse(text):
    """The small YAML subset the contract uses: nested maps by indentation, 'key: value', flow lists and flow maps, # comments."""
    root, stack = {}, [(-1, None)]
    stack = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, _, val = raw.strip().partition(":")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if key in parent:
            raise ValueError("duplicate key " + key)
        if val.strip() == "":
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = value(val)
    return root


class IdentityAccessContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read("contracts/identity-access.yaml")
        cls.c = parse(cls.text)

    def test_shape(self):
        self.assertEqual(self.c["status"], "accepted")
        want = {"ceo", "coo", "cho", "cos", "cfo", "sync_job", "ceo_ledger_plugin", "claude_code_vm", "repo_owner"}
        self.assertEqual(set(self.c["identities"]), want)
        for name, ident in self.c["identities"].items():
            for k in ("kind", "authenticates_with", "may_read", "may_write", "may_send", "may_approve", "must_never"):
                self.assertIn(k, ident, name + " lacks " + k)
            self.assertTrue(ident["authenticates_with"], name)
            self.assertTrue(ident["must_never"], name)

    def test_send_lists_equal_the_health_check_and_the_upgrade_diff(self):
        hc = read("deploy/loop1/health-check.py")
        send = ast.literal_eval(re.search(r"^SEND = (\{.*\})$", hc, re.M).group(1))
        for a in AGENTS:
            self.assertEqual(sorted(self.c["identities"][a]["may_send"]), sorted(send[a]), a)
        diff = read("ops/cfo-send-list-diff-2026-10-26.txt")
        after = ast.literal_eval(re.search(r"^after:\s*(\[.*\])$", diff, re.M).group(1))
        self.assertEqual(sorted(self.c["identities"]["cfo"]["may_send"]), sorted(after))

    def test_agent_instruction_text_never_lists_more_than_the_contract(self):
        par = {"coo": "executive/coo", "cos": "executive/cos", "cho": "department/cho", "cfo": "department/cfo"}
        for a, d in par.items():
            m = re.search(r"## You may send to\n([^\n]+)", read("agent-files/%s/AGENTS.md" % d))
            self.assertIsNotNone(m, a)
            names = [x.strip().lower() for x in re.sub(r"\(.*?\)", "", m.group(1)).replace(".", "").split(",") if x.strip()]
            self.assertTrue(set(names) <= set(self.c["identities"][a]["may_send"]), "%s text %s" % (a, names))

    def test_only_the_cos_writes_the_journal_and_only_the_job_writes_google(self):
        for name, ident in self.c["identities"].items():
            self.assertEqual("calendar_journal" in ident["may_write"], name == "cos", name)
            self.assertEqual("google_test_calendar" in ident["may_write"], name == "sync_job", name)
        self.assertEqual(self.c["rules"]["calendar_writes"]["google"], "sync_job_only")
        self.assertEqual(self.c["rules"]["calendar_writes"]["journal"], "cos_only")

    def test_only_the_ceo_approves_a_delete(self):
        for name, ident in self.c["identities"].items():
            self.assertEqual("delete" in ident["may_approve"], name == "ceo", name)
        self.assertEqual(self.c["rules"]["delete"]["approver"], "ceo")
        self.assertEqual(self.c["rules"]["delete"]["evidence"], "ceo_ledger")

    def test_delete_rule_matches_the_job_and_the_health_check(self):
        job = read("scripts/gcal/gcal_sync.py")
        hours = int(re.search(r"LEDGER_MAX_AGE_SECONDS = (\d+) \* 3600", job).group(1))
        self.assertEqual(int(self.c["rules"]["delete"]["approval_max_age_hours"]), hours)
        self.assertIn("--require-ceo-ledger", job)
        hc = read("deploy/loop1/health-check.py")
        self.assertIn('l.count("--require-ceo-ledger") == 2', hc)
        self.assertEqual(self.c["rules"]["delete"]["cron_option"], "require_ceo_ledger_for_both_ledgers")

    def test_file_modes_match_the_plugin_and_the_vm_facts(self):
        js = read("deploy/loop3/ceo-plugin/ledger.js")
        self.assertIn("mode: 0o700", js)
        self.assertIn("0o600", js)
        f = self.c["files"]
        self.assertEqual(f["ceo_ledger_dir"]["mode"], "700")
        for k in ("slack_ledger", "scenario_ledger", "ceo_slack_id", "gateway_token", "openclaw_config", "gcal_sync_env"):
            self.assertEqual(f[k]["mode"], "600", k)
        self.assertTrue(f["ceo_slack_id"]["path"].endswith("/ceo-slack-id"))

    def test_the_plugin_stays_observe_only(self):
        self.assertIn("store_message_text", self.c["identities"]["ceo_ledger_plugin"]["must_never"])
        idx = read("deploy/loop3/ceo-plugin/index.js")
        self.assertEqual(re.findall(r'api\.on\("([a-z_]+)"', idx), ["message_received"])
        self.assertEqual(self.c["identities"]["ceo_ledger_plugin"]["may_send"], [])

    def test_channels_are_placeholders_and_no_secret_or_id_shapes_appear(self):
        for k, v in self.c["channels"].items():
            self.assertRegex(v, r"^\{\{[A-Z_]+_CHANNEL_ID\}\}$", k)
        for pat in (r"xox[bpa]-", r"xapp-", r"\bU[0-9A-Z]{8,}\b", r"\bC[0-9A-Z]{9,}\b", r"\b\d{1,3}(\.\d{1,3}){3}\b", r"@[A-Za-z0-9.-]+\.[a-z]{2,}", r"sk-[A-Za-z0-9]{10,}"):
            self.assertIsNone(re.search(pat, self.text), pat)

    def test_every_approval_cited_exists(self):
        ledger = read("decisions/APPROVALS.md")
        for apr in self.c["approvals"]:
            self.assertRegex(ledger, r"(?m)^## %s\b" % re.escape(apr))

    def test_the_privacy_gate_is_declared_unwired_and_the_code_exists(self):
        self.assertEqual(self.c["rules"]["privacy"]["wired"], "false")
        self.assertTrue(os.path.getsize(os.path.join(ROOT, self.c["rules"]["privacy"]["gate"])) > 0)

    def test_the_known_cfo_difference_is_recorded_and_still_true(self):
        self.assertIn("cfo_send_text_vs_config", self.c["known_differences"])
        m = re.search(r"## You may send to\n([^\n]+)", read("agent-files/department/cfo/AGENTS.md"))
        text = {x.strip().lower() for x in re.sub(r"\(.*?\)", "", m.group(1)).replace(".", "").split(",") if x.strip()}
        config = set(self.c["identities"]["cfo"]["may_send"])
        self.assertTrue(text < config, "if the text and the config now agree, remove the known difference")

    def test_the_parser_rejects_a_duplicate_key(self):
        with self.assertRaises(ValueError):
            parse("a: 1\na: 2\n")


if __name__ == "__main__":
    unittest.main()
