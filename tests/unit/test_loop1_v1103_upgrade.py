"""Tests for deploy/loop1/loop1-v1103-upgrade.sh (APR-0095). Fake COO workspace in a temporary HOME; a fake pgrep stands in for the gateway check."""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "deploy", "loop1", "loop1-v1103-upgrade.sh")
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@localhost"]
COO = "# Agent\n- Delete requests (instruction set v1.10.1): x.\n"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "needs bash and git")
class V1103Upgrade(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.ws = os.path.join(self.home, "loop1", "workspaces", "coo")
        os.makedirs(os.path.join(self.ws, "state"))
        self.write(COO)
        with open(os.path.join(self.ws, "state", "seed.md"), "w") as fh:
            fh.write("seed\n")
        sh(["git", "init", "-q"], cwd=self.ws)
        sh(GIT + ["add", "-A"], cwd=self.ws)
        sh(GIT + ["commit", "-q", "-m", "seed"], cwd=self.ws)
        self.bin = os.path.join(self.tmp, "bin")
        os.makedirs(self.bin)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, text):
        with open(os.path.join(self.ws, "AGENTS.md"), "w") as fh:
            fh.write(text)

    def text(self):
        with open(os.path.join(self.ws, "AGENTS.md")) as fh:
            return fh.read()

    def fake_pgrep(self, running):
        p = os.path.join(self.bin, "pgrep")
        with open(p, "w") as fh:
            fh.write("#!/bin/sh\nexit %d\n" % (0 if running else 1))
        os.chmod(p, 0o755)

    def run_script(self, *args):
        env = dict(os.environ, HOME=self.home, PATH=self.bin + os.pathsep + os.environ["PATH"])
        return sh(["bash", SCRIPT, *args], env=env)

    def test_dry_run_changes_nothing(self):
        self.fake_pgrep(True)
        r = self.run_script("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("would append", r.stdout)
        self.assertEqual(self.text(), COO)

    def test_applies_and_commits_only_agents_md(self):
        self.fake_pgrep(False)
        with open(os.path.join(self.ws, "state", "seed.md"), "w") as fh:
            fh.write("dirty\n")
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("coo: v1.10.3 added", r.stdout)
        t = self.text()
        self.assertIn("instruction set v1.10.3", t)
        self.assertIn("always post the seven items, each on its own line", t)
        self.assertIn("What, Used for, Why now, Risk if approved, Risk if not, Recommendation, Reply", t)
        self.assertIn("A plain sentence is not enough", t)
        files = sh(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=self.ws).stdout.split()
        self.assertEqual(files, ["AGENTS.md"])
        self.assertEqual(sh(["git", "log", "-1", "--pretty=%s"], cwd=self.ws).stdout.strip(), "Loop 1 instructions v1.10.3 (APR-0095)")
        self.assertIn("state/seed.md", sh(["git", "status", "--porcelain"], cwd=self.ws).stdout)

    def test_second_run_is_a_no_op(self):
        self.fake_pgrep(False)
        self.assertEqual(self.run_script().returncode, 0)
        once = self.text()
        r = self.run_script()
        self.assertEqual(r.returncode, 0)
        self.assertIn("already v1.10.3, skipped", r.stdout)
        self.assertEqual(self.text(), once)
        self.assertEqual(once.count("instruction set v1.10.3"), 1)

    def test_refuses_when_gateway_is_running(self):
        self.fake_pgrep(True)
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Gateway is running", r.stdout)
        self.assertEqual(self.text(), COO)

    def test_refuses_when_not_on_v1101(self):
        self.fake_pgrep(False)
        self.write("# Agent\nplain\n")
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("coo is not on v1.10.1", r.stdout)

    def test_bad_argument(self):
        self.fake_pgrep(False)
        r = self.run_script("--wat")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Usage", r.stdout)


if __name__ == "__main__":
    unittest.main()
