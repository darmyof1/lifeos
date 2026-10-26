"""Tests for deploy/loop1/loop1-v17-upgrade.sh (APR-0075). Runs the script against fake workspaces in a temporary HOME.
A fake pgrep on PATH stands in for the gateway check, so no OpenClaw is needed."""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "deploy", "loop1", "loop1-v17-upgrade.sh")
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@localhost"]

V14 = "# Agent\n- Waiting (APR-0065, instruction set v1.4): wait.\n"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def make_workspace(path, text=V14):
    os.makedirs(os.path.join(path, "state"))
    with open(os.path.join(path, "AGENTS.md"), "w") as fh:
        fh.write(text)
    with open(os.path.join(path, "state", "seed.md"), "w") as fh:
        fh.write("seed\n")
    sh(["git", "init", "-q"], cwd=path)
    sh(GIT + ["add", "-A"], cwd=path)
    sh(GIT + ["commit", "-q", "-m", "seed"], cwd=path)


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "needs bash and git")
class V17Upgrade(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.w = os.path.join(self.home, "loop1", "workspaces")
        for a in ("cho", "cos"):
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
        self.fake_pgrep(True)  # a running gateway does not block a dry run
        before = {a: self.text(a) for a in ("cho", "cos")}
        r = self.run_script("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("would append", r.stdout)
        self.assertIn("Dry run only", r.stdout)
        for a in before:
            self.assertEqual(self.text(a), before[a])
            log = sh(["git", "log", "--oneline"], cwd=os.path.join(self.w, a)).stdout
            self.assertEqual(len(log.strip().splitlines()), 1)

    def test_applies_and_commits_only_agents_md(self):
        self.fake_pgrep(False)
        # state/ is dirty: the commit must not take it along (the v1.3 lesson, fix-51)
        with open(os.path.join(self.w, "cho", "state", "seed.md"), "w") as fh:
            fh.write("dirty\n")
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("cho: v1.7 added", r.stdout)
        self.assertIn("cos: v1.7 added", r.stdout)
        self.assertIn("sessionKey agent:cos:main", self.text("cho"))
        self.assertIn("mode followup, timeoutSeconds 120", self.text("cho"))
        self.assertIn("Never set watch", self.text("cho"))
        self.assertIn("Never call sessions_send to the CHO", self.text("cos"))
        self.assertIn("sentBeforeError true", self.text("cos"))
        self.assertNotIn("Never call sessions_send to the CHO", self.text("cho"))
        self.assertNotIn("sessionKey agent:cos:main", self.text("cos"))
        for a in ("cho", "cos"):
            cwd = os.path.join(self.w, a)
            files = sh(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=cwd).stdout.split()
            self.assertEqual(files, ["AGENTS.md"])
            self.assertEqual(sh(["git", "log", "-1", "--pretty=%s"], cwd=cwd).stdout.strip(), "Loop 1 instructions v1.7 (APR-0075)")
        status = sh(["git", "status", "--porcelain"], cwd=os.path.join(self.w, "cho")).stdout
        self.assertIn("state/seed.md", status)  # still dirty, not committed

    def test_second_run_is_a_no_op(self):
        self.fake_pgrep(False)
        self.assertEqual(self.run_script().returncode, 0)
        once = {a: self.text(a) for a in ("cho", "cos")}
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("cho: already v1.7, skipped", r.stdout)
        self.assertIn("cos: already v1.7, skipped", r.stdout)
        for a in once:
            self.assertEqual(self.text(a), once[a])

    def test_refuses_when_gateway_is_running(self):
        self.fake_pgrep(True)
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Gateway is running", r.stdout)
        self.assertNotIn("v1.7", self.text("cho"))

    def test_refuses_when_an_agent_is_not_on_v14_and_changes_neither(self):
        self.fake_pgrep(False)
        with open(os.path.join(self.w, "cos", "AGENTS.md"), "w") as fh:
            fh.write("# Agent\nold\n")
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("cos is not on v1.4", r.stdout)
        self.assertNotIn("v1.7", self.text("cho"))  # all or nothing

    def test_refuses_when_a_file_is_missing(self):
        self.fake_pgrep(False)
        os.remove(os.path.join(self.w, "cho", "AGENTS.md"))
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
