"""Tests for deploy/loop1/loop1-v191-upgrade.sh (v1.9.1). Runs the script against fake workspaces in a temporary HOME.
A fake pgrep on PATH stands in for the gateway check, so no OpenClaw is needed."""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "deploy", "loop1", "loop1-v191-upgrade.sh")
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@localhost"]

V19 = "# Agent\n- Privacy mark (APR-0086, instruction set v1.9): rule.\n"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def make_workspace(path, text=V19):
    os.makedirs(os.path.join(path, "state"))
    with open(os.path.join(path, "AGENTS.md"), "w") as fh:
        fh.write(text)
    with open(os.path.join(path, "state", "seed.md"), "w") as fh:
        fh.write("seed\n")
    sh(["git", "init", "-q"], cwd=path)
    sh(GIT + ["add", "-A"], cwd=path)
    sh(GIT + ["commit", "-q", "-m", "seed"], cwd=path)


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "needs bash and git")
class V191Upgrade(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.w = os.path.join(self.home, "loop1", "workspaces")
        for a in ("cos", "cho"):
            make_workspace(os.path.join(self.w, a))
        self.bin = os.path.join(self.tmp, "bin")
        os.makedirs(self.bin)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_pgrep(self, running):
        p = os.path.join(self.bin, "pgrep")
        with open(p, "w") as fh:
            fh.write("#!/bin/sh\nexit %d\n" % (0 if running else 1))
        os.chmod(p, 0o755)

    def run_script(self, *args):
        env = dict(os.environ, HOME=self.home, PATH=self.bin + os.pathsep + os.environ["PATH"])
        return sh(["bash", SCRIPT, *args], env=env)

    def text(self, a):
        with open(os.path.join(self.w, a, "AGENTS.md")) as fh:
            return fh.read()

    def test_dry_run_changes_nothing(self):
        self.fake_pgrep(True)
        before = self.text("cos")
        r = self.run_script("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("would append", r.stdout)
        self.assertEqual(self.text("cos"), before)

    def test_applies_to_the_cos_only_and_commits_only_agents_md(self):
        self.fake_pgrep(False)
        cho_before = self.text("cho")
        with open(os.path.join(self.w, "cos", "state", "seed.md"), "w") as fh:
            fh.write("dirty\n")
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        t = self.text("cos")
        self.assertIn("instruction set v1.9.1", t)
        self.assertIn("instruction set v1.9)", t)  # the v1.9 rule stays
        self.assertIn("Never edit, replace or delete an existing journal line, including the header", t)
        self.assertIn("put privacy=high in the detail column of those new lines", t)
        self.assertEqual(self.text("cho"), cho_before)
        cwd = os.path.join(self.w, "cos")
        files = sh(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=cwd).stdout.split()
        self.assertEqual(files, ["AGENTS.md"])
        self.assertIn("state/seed.md", sh(["git", "status", "--porcelain"], cwd=cwd).stdout)

    def test_second_run_is_a_no_op(self):
        self.fake_pgrep(False)
        self.assertEqual(self.run_script().returncode, 0)
        once = self.text("cos")
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("already v1.9.1, skipped", r.stdout)
        self.assertEqual(self.text("cos"), once)

    def test_refuses_when_gateway_is_running(self):
        self.fake_pgrep(True)
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Gateway is running", r.stdout)
        self.assertNotIn("v1.9.1", self.text("cos"))

    def test_refuses_when_cos_is_not_on_v19(self):
        self.fake_pgrep(False)
        with open(os.path.join(self.w, "cos", "AGENTS.md"), "w") as fh:
            fh.write("# Agent\nold\n")
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("cos is not on v1.9", r.stdout)

    def test_refuses_when_the_file_is_missing(self):
        self.fake_pgrep(False)
        os.remove(os.path.join(self.w, "cos", "AGENTS.md"))
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("AGENTS.md missing", r.stdout)

    def test_bad_argument(self):
        self.fake_pgrep(False)
        r = self.run_script("--wat")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Usage", r.stdout)


if __name__ == "__main__":
    unittest.main()
