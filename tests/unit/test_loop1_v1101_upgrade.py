"""Tests for deploy/loop1/loop1-v1101-upgrade.sh (APR-0093). Runs the script against fake workspaces in a temporary HOME.
A fake pgrep on PATH stands in for the gateway check, so no OpenClaw is needed."""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "deploy", "loop1", "loop1-v1101-upgrade.sh")
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@localhost"]

COO = "# Agent\n- Confirmed reports (instruction set v1.10): x.\n"
COS = "# Agent\n- Deletes (instruction set v1.10): x.\n"
V0 = "# Agent\nplain\n"
AGENTS = ("coo", "cos")


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def make_workspace(path, text=V0):
    os.makedirs(os.path.join(path, "state"))
    with open(os.path.join(path, "AGENTS.md"), "w") as fh:
        fh.write(text)
    with open(os.path.join(path, "state", "seed.md"), "w") as fh:
        fh.write("seed\n")
    sh(["git", "init", "-q"], cwd=path)
    sh(GIT + ["add", "-A"], cwd=path)
    sh(GIT + ["commit", "-q", "-m", "seed"], cwd=path)


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "needs bash and git")
class V1101Upgrade(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        self.w = os.path.join(self.home, "loop1", "workspaces")
        make_workspace(os.path.join(self.w, "coo"), COO)
        make_workspace(os.path.join(self.w, "cos"), COS)
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
        before = {a: self.text(a) for a in AGENTS}
        r = self.run_script("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("would append", r.stdout)
        self.assertIn("Dry run only", r.stdout)
        for a in AGENTS:
            self.assertEqual(self.text(a), before[a])
            log = sh(["git", "log", "--oneline"], cwd=os.path.join(self.w, a)).stdout
            self.assertEqual(len(log.strip().splitlines()), 1)

    def test_applies_to_two_agents_and_commits_only_agents_md(self):
        self.fake_pgrep(False)
        with open(os.path.join(self.w, "cos", "state", "seed.md"), "w") as fh:
            fh.write("dirty\n")
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for a in AGENTS:
            self.assertIn(a + ": v1.10.1 added", r.stdout)
            cwd = os.path.join(self.w, a)
            files = sh(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=cwd).stdout.split()
            self.assertEqual(files, ["AGENTS.md"])
            self.assertEqual(sh(["git", "log", "-1", "--pretty=%s"], cwd=cwd).stdout.strip(), "Loop 1 instructions v1.10.1 (APR-0093)")
        cos = self.text("cos")
        self.assertIn("instruction set v1.10)", cos)
        self.assertIn("append the delete-pending-approval line first, even when the message says the CEO approved", cos)
        self.assertIn("A deleted line with no delete-pending-approval line before it for the same event ID is wrong", cos)
        self.assertIn("Never use the title and never make up an ID", cos)
        coo = self.text("coo")
        self.assertIn("quote the CEO's exact words and give the event ID from the journal entry", coo)
        self.assertIn("Never write approving or approved", coo)
        self.assertIn("put each item on its own line", coo)
        self.assertIn("state/seed.md", sh(["git", "status", "--porcelain"], cwd=os.path.join(self.w, "cos")).stdout)

    def test_second_run_is_a_no_op(self):
        self.fake_pgrep(False)
        self.assertEqual(self.run_script().returncode, 0)
        once = {a: self.text(a) for a in AGENTS}
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for a in AGENTS:
            self.assertIn(a + ": already v1.10.1, skipped", r.stdout)
            self.assertEqual(self.text(a), once[a])
            self.assertEqual(once[a].count("instruction set v1.10.1"), 1)

    def test_refuses_when_gateway_is_running(self):
        self.fake_pgrep(True)
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Gateway is running", r.stdout)
        for a in AGENTS:
            self.assertNotIn("v1.10.1", self.text(a))

    def test_refuses_when_not_on_v110_and_changes_nobody(self):
        self.fake_pgrep(False)
        with open(os.path.join(self.w, "cos", "AGENTS.md"), "w") as fh:
            fh.write(V0)
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("cos is not on v1.10", r.stdout)
        for a in AGENTS:
            self.assertNotIn("v1.10.1", self.text(a))

    def test_refuses_when_a_file_is_missing(self):
        self.fake_pgrep(False)
        os.remove(os.path.join(self.w, "coo", "AGENTS.md"))
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("coo/AGENTS.md missing", r.stdout)

    def test_bad_argument(self):
        self.fake_pgrep(False)
        r = self.run_script("--wat")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Usage", r.stdout)


if __name__ == "__main__":
    unittest.main()
