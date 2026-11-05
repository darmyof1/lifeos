"""Tests for scripts/verify/history_scan.sh (APR-0113, APR-0114) on throwaway git repos. Token-shaped test strings are built at run time,
so this file itself holds none. The scan must print counts and file names, never the matches."""
import os, shutil, subprocess, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "scripts", "verify", "history_scan.sh")
AT = chr(64)
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t" + AT + "example.invalid", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t" + AT + "example.invalid")

CASES = {
    "slack token": "xo" + "xb-" + "1234567890-abcdefghijkl",
    "slack app token": "xa" + "pp-" + "1-A0123456789-abcdefghijkl",
    "google key": "AI" + "za" + "A" * 35,
    "google client secret": "GOC" + "SPX-" + "abcdefghij0123456789ab",
    "openai key": "s" + "k-" + "abcdefghijklmnopqrstuvwx",
    "aws key": "AK" + "IA" + "ABCDEFGHIJKLMNOP",
    "github token": "gh" + "p_" + "a" * 36,
    "private key": "-----BEGIN " + "RSA PRIVATE KEY-----",
    "ipv4": "host 10." + "20.30.40 here",
    "slack id": "owner " + "U07ABC" + "12345",
    "email": "write to " + "someone" + "@" + "company.test",
}


def git(d, *a):
    return subprocess.run(["git", "-C", d, *a], env=ENV, capture_output=True, text=True)


class HistoryScanTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="hs-", dir="/tmp")
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        git(self.d, "init", "-q", "-b", "main")

    def commit(self, name, text, msg="c"):
        with open(os.path.join(self.d, name), "w") as fh:
            fh.write(text)
        git(self.d, "add", "-A")
        git(self.d, "commit", "-q", "-m", msg)

    def scan(self):
        r = subprocess.run(["bash", SCRIPT, self.d], capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def test_a_clean_repo_passes(self):
        self.commit("a.md", "plain text, 127.0.0.1 and 0.0.0.0 are fine, version 2026.10.5, test" + AT + "example.com\n")
        rc, out = self.scan()
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULT: clean", out)

    def test_known_fake_ids_pass(self):
        self.commit("a.md", "UFAKECEO01 CFAKECHAN01 C0123456789 U0ANYONE\n")
        self.assertEqual(self.scan()[0], 0)

    def test_every_category_is_found_and_the_match_is_never_printed(self):
        for label, text in CASES.items():
            with self.subTest(label):
                d = tempfile.mkdtemp(prefix="hs-", dir="/tmp")
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                git(d, "init", "-q", "-b", "main")
                fname = "notes-%s.txt" % label.replace(" ", "-")
                with open(os.path.join(d, fname), "w") as fh:
                    fh.write(text + "\n")
                git(d, "add", "-A")
                git(d, "commit", "-q", "-m", "c")
                r = subprocess.run(["bash", SCRIPT, d], capture_output=True, text=True, timeout=120)
                out = r.stdout + r.stderr
                self.assertEqual(r.returncode, 1, out)
                self.assertIn("HIT", out)
                self.assertIn(fname, out)
                core = text.split()[-1] if label in ("ipv4", "slack id", "email") else text
                self.assertNotIn(core, out)
                self.assertNotIn(text, out)

    def test_a_secret_removed_in_a_later_commit_is_still_found(self):
        self.commit("k.txt", CASES["slack token"] + "\n")
        self.commit("k.txt", "removed\n")
        rc, out = self.scan()
        self.assertEqual(rc, 1)
        self.assertIn("k.txt", out)

    def test_a_secret_on_another_branch_is_found(self):
        self.commit("a.md", "clean\n")
        git(self.d, "checkout", "-q", "-b", "side")
        self.commit("side.txt", CASES["aws key"] + "\n")
        git(self.d, "checkout", "-q", "main")
        self.assertEqual(self.scan()[0], 1)

    def test_a_secret_in_a_commit_message_is_found(self):
        self.commit("a.md", "clean\n", msg="token " + CASES["github token"])
        rc, out = self.scan()
        self.assertEqual(rc, 1)
        self.assertIn("(commit messages)", out)
        self.assertNotIn(CASES["github token"], out)

    def test_author_email_is_info_only_and_not_printed(self):
        self.commit("a.md", "clean\n")
        rc, out = self.scan()
        self.assertEqual(rc, 0)
        self.assertIn("INFO author/committer email addresses", out)
        self.assertNotIn("t" + AT + "example.invalid", out)

    def test_not_a_repo_is_an_error(self):
        d = tempfile.mkdtemp(prefix="hs-", dir="/tmp")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = subprocess.run(["bash", SCRIPT, d], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
