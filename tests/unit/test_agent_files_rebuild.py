"""Rebuild the four agents' instruction files from the repo scripts in a temporary HOME (placeholder channel IDs, a stub pgrep)
and check that every file under agent-files/ is byte for byte what the scripts produce (APR-0097, APR-0098)."""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEPLOY = os.path.join(ROOT, "deploy", "loop1")
SCRIPTS = ["loop1-agent-files.sh", "loop1-v13-upgrade.sh", "loop1-v14-upgrade.sh", "loop1-v15-upgrade.sh",
           "loop1-v16-upgrade.sh", "loop1-v17-upgrade.sh", "loop1-v18-upgrade.sh", "loop1-v19-upgrade.sh",
           "loop1-v191-upgrade.sh", "loop1-v110-upgrade.sh", "loop1-v1101-upgrade.sh", "loop1-v1102-upgrade.sh",
           "loop1-v1103-upgrade.sh", "loop1-v1104-upgrade.sh"]
PATHS = {"coo": "executive/coo", "cos": "executive/cos", "cho": "department/cho", "cfo": "department/cfo"}
FILES = ("AGENTS.md", "SOUL.md", "IDENTITY.md", "USER.md")
ENV = "staff-cos={{COS_CHANNEL_ID}}\noperations-coo={{COO_CHANNEL_ID}}\nhealth-cho={{CHO_CHANNEL_ID}}\nfinance-cfo={{CFO_CHANNEL_ID}}\n"


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "needs bash and git")
class AgentFilesRebuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.home = os.path.join(cls.tmp, "home")
        cls.w = os.path.join(cls.home, "loop1", "workspaces")
        cls.bin = os.path.join(cls.tmp, "bin")
        os.makedirs(cls.bin)
        with open(os.path.join(cls.bin, "pgrep"), "w") as fh:
            fh.write("#!/bin/sh\nexit 1\n")
        os.chmod(os.path.join(cls.bin, "pgrep"), 0o755)
        for a in PATHS:
            os.makedirs(os.path.join(cls.w, a))
            subprocess.run(["git", "init", "-q"], cwd=os.path.join(cls.w, a), check=True)
        with open(os.path.join(cls.home, "loop1", "slack-channels.env"), "w") as fh:
            fh.write(ENV)
        env = dict(os.environ, HOME=cls.home, PATH=cls.bin + os.pathsep + os.environ["PATH"])
        cls.failed = []
        for s in SCRIPTS:
            r = subprocess.run(["bash", os.path.join(DEPLOY, s)], env=env, capture_output=True, text=True)
            if r.returncode != 0:
                cls.failed.append((s, (r.stdout + r.stderr)[-300:]))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_script_runs(self):
        self.assertEqual(self.failed, [])

    def test_repo_copies_match_the_rebuild(self):
        for a, d in PATHS.items():
            for f in FILES:
                with self.subTest(file="%s/%s" % (d, f)):
                    with open(os.path.join(ROOT, "agent-files", d, f), "rb") as fh:
                        repo = fh.read()
                    with open(os.path.join(self.w, a, f), "rb") as fh:
                        built = fh.read()
                    self.assertTrue(repo, "repo copy is empty")
                    self.assertEqual(repo, built)

    def test_no_real_channel_id_in_the_repo_copies(self):
        for a, d in PATHS.items():
            with open(os.path.join(ROOT, "agent-files", d, "AGENTS.md"), "rb") as fh:
                data = fh.read()
            for tag in (b"{{COS_CHANNEL_ID}}", b"{{CHO_CHANNEL_ID}}", b"{{CFO_CHANNEL_ID}}"):
                self.assertLessEqual(data.count(tag), 1)
            self.assertNotRegex(data.decode(), r"\b[CG][0-9A-Z]{9,}\b")


if __name__ == "__main__":
    unittest.main()
