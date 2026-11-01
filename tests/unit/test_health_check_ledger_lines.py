"""Tests for the two health-check lines added by APR-0109 (plugin loaded and hook-only; calendar cron line carries both ledgers)
and for the gateway-process filter shared with daily-reset-report.py. health-check.py runs on import, so the functions are
extracted with ast and run alone."""
import ast
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HC = os.path.join(ROOT, "deploy", "loop1", "health-check.py")
RR = os.path.join(ROOT, "deploy", "loop2", "vm", "daily-reset-report.py")


def extract(path, names):
    tree = ast.parse(open(path).read())
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), path, "exec"), ns)
    return ns


HCF = extract(HC, {"cron_ledger_status", "plugin_inspect_status"})
RRF = extract(RR, {"gateway_count"})
GOOD = ("*/5 * * * * LIFEOS_SYNC_ARGS=\"--require-ceo-ledger $HOME/loop1/ceo-ledger/scenario-ledger.jsonl "
        "--require-ceo-ledger $HOME/loop1/ceo-ledger/slack-ledger.jsonl\" bash $HOME/lifeos-ro/scripts/gcal/gcal_sync_cron.sh")


class CronLine(unittest.TestCase):
    f = staticmethod(HCF["cron_ledger_status"])

    def test_both_ledgers_pass(self):
        self.assertEqual(self.f(["0 5 * * * x", GOOD])[0], "PASS")

    def test_one_ledger_fails(self):
        one = GOOD.replace("--require-ceo-ledger $HOME/loop1/ceo-ledger/slack-ledger.jsonl", "")
        self.assertEqual(self.f([one])[0], "FAIL")

    def test_no_flag_fails(self):
        self.assertEqual(self.f(["*/5 * * * * bash $HOME/lifeos-ro/scripts/gcal/gcal_sync_cron.sh"])[0], "FAIL")

    def test_paused_is_info(self):
        self.assertEqual(self.f(["#" + GOOD])[0], "INFO")

    def test_missing_fails(self):
        self.assertEqual(self.f(["0 5 * * * x"])[0], "FAIL")


class Plugin(unittest.TestCase):
    f = staticmethod(HCF["plugin_inspect_status"])

    def test_enabled_hook_only(self):
        self.assertEqual(self.f("Status: enabled\nShape: non-capability\nCapability mode: none")[0], "PASS")

    def test_disabled_fails(self):
        self.assertEqual(self.f("Status: disabled\nShape: non-capability\nCapability mode: none")[0], "FAIL")

    def test_missing_fails(self):
        self.assertEqual(self.f("plugin not found")[0], "FAIL")
        self.assertEqual(self.f("")[0], "FAIL")

    def test_shape_change_warns(self):
        self.assertEqual(self.f("Status: enabled\nShape: hybrid\nCapability mode: tools")[0], "WARN")


class GatewayFilter(unittest.TestCase):
    f = staticmethod(RRF["gateway_count"])

    def test_counts_only_real_gateway(self):
        out = ("101 openclaw-gateway\n"
               "202 bash -c pgrep -af 'openclaw.*gateway' | wc -l\n"
               "303 /bin/sh -c ps; pgrep -af openclaw.*gateway\n")
        self.assertEqual(self.f(out), 1)

    def test_gateway_run_form(self):
        self.assertEqual(self.f("55 node openclaw gateway run --port 1\n"), 1)

    def test_empty(self):
        self.assertEqual(self.f(""), 0)


if __name__ == "__main__":
    unittest.main()
