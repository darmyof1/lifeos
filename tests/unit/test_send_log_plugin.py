"""Send-log plugin (APR-0136): runs the node tests, and checks the shape files, the repo-side wiring and the health-check lines.
Skips the node run when node is not installed."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PL = os.path.join(ROOT, "deploy", "after-loop7", "send-log-plugin")


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class SendLogPlugin(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_node_tests_pass(self):
        r = subprocess.run(["node", "--test"], cwd=PL, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-500:])

    def test_manifest_shape(self):
        m = json.loads(read("deploy/after-loop7/send-log-plugin/openclaw.plugin.json"))
        self.assertEqual(m["id"], "send-log")
        self.assertEqual(m["configSchema"], {"type": "object", "additionalProperties": False})
        self.assertTrue(m["activation"]["onStartup"])

    def test_index_registers_only_two_hooks(self):
        code = "\n".join(l.split("//")[0] for l in read("deploy/after-loop7/send-log-plugin/index.js").splitlines())
        self.assertEqual(code.count("api.on("), 2)
        self.assertIn('api.on("after_tool_call"', code)
        self.assertIn('api.on("message_received"', code)
        self.assertNotIn("before_tool_call", code)
        for bad in ("registerTool", "registerService", "registerCommand", "registerHttpRoute"):
            self.assertNotIn(bad, code)

    def test_log_js_has_no_openclaw_import_and_no_text_field(self):
        src = read("deploy/after-loop7/send-log-plugin/log.js")
        self.assertNotIn("openclaw", src.replace("// ", "").lower().replace("no openclaw imports", ""))
        self.assertNotIn("event.result", "\n".join(l for l in src.splitlines() if not l.strip().startswith("//")))

    def test_health_check_has_send_log_lines(self):
        hc = read("deploy/loop1/health-check.py")
        for want in ('"plugin send-log enabled, hook-only"', '"send-log plugin files equal the repo copy"',
                     '"send-log plugin has no conversation access"', 'plugins.entries.send-log.hooks'):
            self.assertIn(want, hc)
        # APR-0137: the COO tool line is now read-only, own workspace
        self.assertIn('"coo read-only, own workspace"', hc)


if __name__ == "__main__":
    unittest.main()
