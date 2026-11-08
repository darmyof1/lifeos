"""Tests for scripts/ops/restore-backup.sh (Loop 4, APR-0117): throwaway key, local bare repository. No real key, no real data."""
import os, shutil, tarfile, tempfile, unittest
from backup_fixture import HAVE, Keys, Home, sh, OPS


def read(p):
    with open(p) as fh:
        return fh.read()


@unittest.skipUnless(HAVE, "needs gpg, git and sha256sum")
class RestoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = Keys()

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bk-rest-", dir="/tmp")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.h = Home(self.keys, self.tmp)
        rc, out = self.h.run("backup-weekly.sh", "--execute", date="20261105-0600")
        self.assertEqual(rc, 0, out)
        self.archive = os.path.join(self.h.backups, "lifeos-backup-20261105-0600.tar.gpg")
        # the restoring machine is "another machine": its own HOME and the keyring that holds the PRIVATE key
        self.mac = os.path.join(self.tmp, "mac")
        os.mkdir(self.mac)
        self.env = dict(self.h.ceo_env(), HOME=self.mac)

    def restore(self, *args):
        r = sh(["bash", os.path.join(OPS, "restore-backup.sh"), *args], self.env)
        return r.returncode, r.stdout + r.stderr

    def test_restore_matches_every_file(self):
        target = os.path.join(self.tmp, "out")
        rc, out = self.restore(self.archive, target)
        self.assertEqual(rc, 0, out)
        self.assertIn("mismatches: 0", out)
        self.assertIn("files: 9", out)  # 4 x AGENTS.md + 4 x note.md + openclaw.json
        self.assertIn("elapsed seconds:", out)
        self.assertEqual(read(os.path.join(target, "cho", "state", "note.md")), "synthetic note for cho\n")

    def test_the_restored_config_has_no_token(self):
        target = os.path.join(self.tmp, "out")
        self.assertEqual(self.restore(self.archive, target)[0], 0)
        self.assertNotIn("tok-synthetic-123456", read(os.path.join(target, "openclaw.json")))

    def test_a_changed_byte_is_detected_and_exit_is_non_zero(self):
        plain = os.path.join(self.tmp, "plain.tar")
        r = sh(["gpg", "--batch", "--yes", "-d", "-o", plain, self.archive], self.h.ceo_env())
        self.assertEqual(r.returncode, 0, r.stderr)
        x = os.path.join(self.tmp, "x")
        os.mkdir(x)
        with tarfile.open(plain) as t:
            t.extractall(x)
        with open(os.path.join(x, "coo", "AGENTS.md"), "a") as fh:
            fh.write("X")
        bad = os.path.join(self.tmp, "bad.tar")
        with tarfile.open(bad, "w") as t:
            t.add(x, arcname=".")
        evil = os.path.join(self.tmp, "lifeos-backup-20261106-0600.tar.gpg")
        r = sh(["gpg", "--batch", "--yes", "--trust-model", "always", "--recipient", self.keys.fpr, "--encrypt", "-o", evil, bad], self.h.ceo_env())
        self.assertEqual(r.returncode, 0, r.stderr)
        rc, out = self.restore(evil, os.path.join(self.tmp, "out"))
        self.assertNotEqual(rc, 0)
        self.assertIn("DIFFERENT ./coo/AGENTS.md", out)
        self.assertIn("mismatches: 1", out)

    def test_a_file_that_is_not_in_the_manifest_counts_as_a_mismatch(self):
        plain = os.path.join(self.tmp, "plain.tar")
        sh(["gpg", "--batch", "--yes", "-d", "-o", plain, self.archive], self.h.ceo_env())
        x = os.path.join(self.tmp, "x")
        os.mkdir(x)
        with tarfile.open(plain) as t:
            t.extractall(x)
        with open(os.path.join(x, "extra.txt"), "w") as fh:
            fh.write("not in the manifest")
        bad = os.path.join(self.tmp, "bad.tar")
        with tarfile.open(bad, "w") as t:
            t.add(x, arcname=".")
        evil = os.path.join(self.tmp, "lifeos-backup-20261106-0601.tar.gpg")
        sh(["gpg", "--batch", "--yes", "--trust-model", "always", "--recipient", self.keys.fpr, "--encrypt", "-o", evil, bad], self.h.ceo_env())
        rc, out = self.restore(evil, os.path.join(self.tmp, "out"))
        self.assertNotEqual(rc, 0)
        self.assertIn("mismatches: 1", out)

    def test_refuses_a_live_folder(self):
        for sub in ("workspaces", "state"):
            live = os.path.join(self.mac, "loop1", sub)
            os.makedirs(live)
            rc, out = self.restore(self.archive, os.path.join(live, "new"))
            self.assertNotEqual(rc, 0)
            self.assertIn("live folder", out)
            self.assertFalse(os.path.exists(os.path.join(live, "new")))

    def test_refuses_a_target_that_is_not_empty(self):
        target = os.path.join(self.tmp, "full")
        os.mkdir(target)
        with open(os.path.join(target, "mine.txt"), "w") as fh:
            fh.write("keep")
        rc, out = self.restore(self.archive, target)
        self.assertNotEqual(rc, 0)
        self.assertIn("not empty", out)
        self.assertEqual(os.listdir(target), ["mine.txt"])

    def test_an_empty_existing_target_is_fine(self):
        target = os.path.join(self.tmp, "empty")
        os.mkdir(target)
        self.assertEqual(self.restore(self.archive, target)[0], 0)

    def test_latest_picks_the_newest_archive_in_a_repo_folder(self):
        repo = os.path.join(self.tmp, "repo")
        os.mkdir(repo)
        old = os.path.join(repo, "lifeos-backup-20261101-0600.tar.gpg")
        shutil.copy(self.archive, old)
        shutil.copy(self.archive, os.path.join(repo, "lifeos-backup-20261105-0600.tar.gpg"))
        shutil.copy(self.archive + ".sha256", os.path.join(repo, "lifeos-backup-20261105-0600.tar.gpg.sha256"))
        with open(old, "ab") as fh:
            fh.write(b"damaged old one")  # if --latest wrongly took this one, it would fail
        rc, out = self.restore("--latest", repo, os.path.join(self.tmp, "out"))
        self.assertEqual(rc, 0, out)
        self.assertIn("mismatches: 0", out)

    def test_a_repo_folder_without_latest_is_refused(self):
        rc, out = self.restore(self.tmp, os.path.join(self.tmp, "out"))
        self.assertNotEqual(rc, 0)
        self.assertIn("--latest", out)

    def test_wrong_checksum_line_refuses_before_decrypting(self):
        repo = os.path.join(self.tmp, "repo")
        os.mkdir(repo)
        a = os.path.join(repo, "lifeos-backup-20261105-0600.tar.gpg")
        shutil.copy(self.archive, a)
        with open(a + ".sha256", "w") as fh:
            fh.write("0" * 64 + "  lifeos-backup-20261105-0600.tar.gpg\n")
        rc, out = self.restore(a, os.path.join(self.tmp, "out"))
        self.assertNotEqual(rc, 0)
        self.assertIn(".sha256 line", out)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "out")))

    def test_without_the_private_key_it_fails(self):
        env = dict(self.env, GNUPGHOME=self.h.gnupg)  # the VM keyring: public key only
        r = sh(["bash", os.path.join(OPS, "restore-backup.sh"), self.archive, os.path.join(self.tmp, "out")], env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("decryption or extraction failed", r.stdout + r.stderr)

    def test_the_script_uses_no_gnu_only_commands_and_takes_no_passphrase(self):
        text = read(os.path.join(OPS, "restore-backup.sh"))
        for bad in ("stat -c", "date -d", "readlink -f", "--passphrase", "--batch", "realpath"):
            self.assertNotIn(bad, text, bad)


if __name__ == "__main__":
    unittest.main()
