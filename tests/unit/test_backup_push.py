"""Tests for scripts/ops/backup-push.sh and backup-run.sh (Loop 4, APR-0117): throwaway key, local bare repository as the remote."""
import os, shutil, tempfile, unittest


def read(p):
    with open(p) as fh:
        return fh.read()

from backup_fixture import HAVE, Keys, Home, sh, OPS


@unittest.skipUnless(HAVE, "needs gpg, git and sha256sum")
class PushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = Keys()

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bk-push-", dir="/tmp")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.h = Home(self.keys, self.tmp)

    def backup(self, date="20261105-0600"):
        rc, out = self.h.run("backup-weekly.sh", "--execute", date=date)
        self.assertEqual(rc, 0, out)
        return "lifeos-backup-%s.tar.gpg" % date

    def test_push_works_one_commit_with_only_the_archive_and_its_line(self):
        name = self.backup()
        rc, out = self.h.run("backup-push.sh", "--execute")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.h.remote_log(), ["backup " + name])
        self.assertEqual(self.h.remote_files(), sorted([name, name + ".sha256"]))

    def test_second_push_is_a_fast_forward_and_the_first_commit_is_untouched(self):
        n1 = self.backup("20261105-0600")
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 0)
        first = sh(["git", "-C", self.h.remote, "rev-parse", "main"]).stdout.strip()
        n2 = self.backup("20261105-0605")
        os.utime(os.path.join(self.h.backups, n2), None)
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 0)
        self.assertEqual(self.h.remote_log(), ["backup " + n2, "backup " + n1])
        self.assertEqual(sh(["git", "-C", self.h.remote, "merge-base", "--is-ancestor", first, "main"]).returncode, 0)

    def test_no_force_push_anywhere_in_the_scripts(self):
        for s in ("backup-push.sh", "backup-run.sh"):
            with open(os.path.join(OPS, s)) as fh:
                text = fh.read()
            self.assertNotIn("--force", text)
            self.assertNotIn("push -f", text)
            self.assertNotIn("+HEAD", text)

    def test_diverged_clone_is_refused_and_nothing_is_forced(self):
        self.backup("20261105-0600")
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 0)
        # someone else pushes to the remote
        other = os.path.join(self.tmp, "other")
        sh(["git", "clone", "-q", self.h.remote, other])
        sh(["git", "-C", other, "-c", "user.name=x", "-c", "user.email=x" + chr(64) + "localhost", "commit", "-q", "--allow-empty", "-m", "remote side"])
        sh(["git", "-C", other, "push", "-q", "origin", "HEAD:main"])
        # and the clone has its own unpushed commit
        sh(["git", "-C", self.h.clone, "-c", "user.name=x", "-c", "user.email=x" + chr(64) + "localhost", "commit", "-q", "--allow-empty", "-m", "local side"])
        remote_before = sh(["git", "-C", self.h.remote, "rev-parse", "main"]).stdout
        self.backup("20261105-0610")
        rc, out = self.h.run("backup-push.sh", "--execute")
        self.assertEqual(rc, 1)
        self.assertIn("diverged", out)
        self.assertEqual(sh(["git", "-C", self.h.remote, "rev-parse", "main"]).stdout, remote_before)

    def test_plaintext_archive_is_refused(self):
        name = self.backup()
        path = os.path.join(self.h.backups, name)
        with open(path, "wb") as fh:
            fh.write(b"this is plain text pretending to be a backup\n" * 20)
        os.system("cd '%s' && sha256sum '%s' > '%s.sha256'" % (self.h.backups, name, name))
        rc, out = self.h.run("backup-push.sh", "--execute")
        self.assertEqual(rc, 1)
        self.assertIn("not gpg-encrypted", out)
        self.assertEqual(self.h.remote_log(), [])

    def test_a_changed_archive_that_no_longer_matches_its_line_is_refused(self):
        name = self.backup()
        with open(os.path.join(self.h.backups, name), "ab") as fh:
            fh.write(b"x")
        rc, out = self.h.run("backup-push.sh", "--execute")
        self.assertEqual(rc, 1)
        self.assertEqual(self.h.remote_log(), [])

    def test_dirty_clone_is_refused(self):
        self.backup("20261105-0600")
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 0)
        with open(os.path.join(self.h.clone, "stray.txt"), "w") as fh:
            fh.write("x")
        self.backup("20261105-0610")
        rc, out = self.h.run("backup-push.sh", "--execute")
        self.assertEqual(rc, 1)
        self.assertIn("uncommitted", out)
        self.assertEqual(len(self.h.remote_log()), 1)

    def test_settings_file_must_be_mode_600_and_must_exist(self):
        self.backup()
        self.h.write_env(mode=0o644)
        rc, out = self.h.run("backup-push.sh", "--execute")
        self.assertEqual(rc, 1)
        self.assertIn("mode 600", out)
        os.remove(os.path.join(self.h.home, "loop1", "backup.env"))
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 1)

    def test_dry_run_changes_nothing_and_does_not_clone(self):
        self.backup()
        rc, out = self.h.run("backup-push.sh")
        self.assertEqual(rc, 0, out)
        self.assertIn("dry run", out)
        self.assertFalse(os.path.exists(self.h.clone))
        self.assertEqual(self.h.remote_log(), [])
        self.assertNotIn(self.h.remote, out)

    def test_same_day_second_backup_does_not_collide(self):
        n1 = self.backup("20261105-0600")
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 0)
        n2 = self.backup("20261105-1800")
        self.assertNotEqual(n1, n2)
        os.utime(os.path.join(self.h.backups, n2), None)
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 0)
        self.assertEqual(len(self.h.remote_files()), 4)

    def test_pushing_the_same_archive_twice_is_a_no_op(self):
        self.backup()
        self.assertEqual(self.h.run("backup-push.sh", "--execute")[0], 0)
        rc, out = self.h.run("backup-push.sh", "--execute")
        self.assertEqual(rc, 0)
        self.assertIn("already", out)
        self.assertEqual(len(self.h.remote_log()), 1)

    def test_repository_holds_no_plaintext_from_the_agent_files(self):
        self.backup()
        self.h.run("backup-push.sh", "--execute")
        out = sh(["git", "-C", self.h.remote, "grep", "-c", "-e", "synthetic heading", "-e", "tok-synthetic", "main"])
        self.assertEqual(out.stdout.strip(), "")


@unittest.skipUnless(HAVE, "needs gpg, git and sha256sum")
class RunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = Keys()

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bk-run-", dir="/tmp")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.h = Home(self.keys, self.tmp)
        self.log = os.path.join(self.h.backups, "run.log")

    def test_run_writes_one_log_line_with_no_secret_and_no_address(self):
        rc, out = self.h.run("backup-run.sh", "--execute")
        self.assertEqual(rc, 0, out)
        lines = read(self.log).splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("push=ok", lines[0])
        self.assertIn("archive=lifeos-backup-", lines[0])
        self.assertIn("bytes=", lines[0])
        self.assertNotIn(self.h.remote, lines[0])
        self.assertEqual(oct(os.stat(self.log).st_mode & 0o777), "0o600")
        self.assertEqual(len(self.h.remote_log()), 1)

    def test_a_failed_push_logs_a_failure_and_exits_non_zero(self):
        self.h.write_env(url=os.path.join(self.tmp, "does-not-exist.git"))
        rc, out = self.h.run("backup-run.sh", "--execute")
        self.assertNotEqual(rc, 0)
        line = read(self.log).strip()
        self.assertIn("push=FAILED", line)
        self.assertNotIn("does-not-exist", line)
        self.assertNotIn("does-not-exist", out)

    def test_a_failed_backup_logs_and_does_not_push(self):
        os.remove(os.path.join(self.h.home, "loop1", "backup-key-fingerprint"))
        rc, out = self.h.run("backup-run.sh", "--execute")
        self.assertNotEqual(rc, 0)
        self.assertIn("backup=FAILED", read(self.log))
        self.assertEqual(self.h.remote_log(), [])

    def test_dry_run_writes_no_log(self):
        rc, out = self.h.run("backup-run.sh")
        self.assertEqual(rc, 1)  # no archive yet: the push check stops
        self.assertFalse(os.path.exists(self.log))

    def test_two_runs_in_a_row_both_push(self):
        self.assertEqual(self.h.run("backup-run.sh", "--execute", date="20261105-0600")[0], 0)
        self.assertEqual(self.h.run("backup-run.sh", "--execute", date="20261105-0605")[0], 0)
        self.assertEqual(len(read(self.log).splitlines()), 2)
        self.assertEqual(len(self.h.remote_log()), 2)


if __name__ == "__main__":
    unittest.main()
