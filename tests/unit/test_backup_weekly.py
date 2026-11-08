"""Tests for scripts/ops/backup-weekly.sh (APR-0113) with throwaway keys in temp GnuPG homes. No real key, no real data."""
import hashlib, json, os, shutil, stat, subprocess, tarfile, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "scripts", "ops", "backup-weekly.sh")
SECRET = "tok-test-secret-value-98765"


def sh(cmd, env, **kw):
    return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=180, **kw)


@unittest.skipUnless(shutil.which("gpg") and shutil.which("sha256sum"), "needs gpg and sha256sum (the backup runs on the Linux VM)")
class BackupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = tempfile.mkdtemp(prefix="bk-keys-", dir="/tmp")
        cls.ceo = os.path.join(cls.keys, "ceo")
        os.mkdir(cls.ceo, 0o700)
        spec = os.path.join(cls.keys, "spec")
        with open(spec, "w") as fh:
            fh.write("%no-protection\nKey-Type: RSA\nKey-Length: 2048\nSubkey-Type: RSA\nSubkey-Length: 2048\nName-Real: Test CEO\nName-Email: test" + chr(64) + "example.invalid\nExpire-Date: 0\n%commit\n")
        env = dict(os.environ, GNUPGHOME=cls.ceo)
        r = sh(["gpg", "--batch", "--gen-key", spec], env)
        assert r.returncode == 0, r.stderr
        out = sh(["gpg", "--batch", "--with-colons", "--list-keys"], env).stdout
        cls.fpr = [l.split(":")[9] for l in out.splitlines() if l.startswith("fpr:")][0]
        cls.pub = sh(["gpg", "--batch", "--armor", "--export", cls.fpr], env).stdout

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.keys, ignore_errors=True)

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bk-home-", dir="/tmp")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home = os.path.join(self.tmp, "home")
        self.gnupg = os.path.join(self.tmp, "gnupg")
        os.mkdir(self.gnupg, 0o700)
        os.makedirs(os.path.join(self.home, "loop1", "state"))
        for a in ("coo", "cho", "cos", "cfo"):
            d = os.path.join(self.home, "loop1", "workspaces", a, "state")
            os.makedirs(d)
            with open(os.path.join(d, "note.md"), "w") as fh:
                fh.write("synthetic note for " + a + "\n")
            with open(os.path.join(self.home, "loop1", "workspaces", a, "AGENTS.md"), "w") as fh:
                fh.write("# " + a + "\n")
        cfg = {"gateway": {"auth": {"token": SECRET}}, "channels": {"slack": {"accounts": {"default": {"botToken": SECRET + "-bot", "enabled": True}}}},
               "agents": {"list": ["coo"]}}
        with open(os.path.join(self.home, "loop1", "state", "openclaw.json"), "w") as fh:
            json.dump(cfg, fh)
        self.env = {"HOME": self.home, "PATH": os.environ["PATH"], "GNUPGHOME": self.gnupg, "BK_DATE": "20261101"}

    def put_key(self, with_fpr=True):
        r = sh(["gpg", "--batch", "--import"], self.env, input=self.pub)
        self.assertEqual(r.returncode, 0, r.stderr)
        if with_fpr:
            with open(os.path.join(self.home, "loop1", "backup-key-fingerprint"), "w") as fh:
                fh.write(self.fpr + "\n")

    def run_bk(self, *args, date=None):
        env = dict(self.env)
        if date:
            env["BK_DATE"] = date
        r = sh(["bash", SCRIPT, *args], env)
        return r.returncode, r.stdout + r.stderr

    backups = property(lambda self: os.path.join(self.home, "loop1", "backups"))

    def decrypt(self, name):
        out = os.path.join(self.tmp, "plain.tar")
        r = sh(["gpg", "--batch", "--yes", "-d", "-o", out, os.path.join(self.backups, name)], dict(self.env, GNUPGHOME=self.ceo))
        self.assertEqual(r.returncode, 0, r.stderr)
        dest = os.path.join(self.tmp, "restored")
        shutil.rmtree(dest, ignore_errors=True)
        os.mkdir(dest)
        with tarfile.open(out) as t:
            t.extractall(dest)
        return dest

    def test_missing_key_file_refuses(self):
        rc, out = self.run_bk("--execute")
        self.assertEqual(rc, 1)
        self.assertIn("no public key fingerprint file", out)
        self.assertFalse(os.path.exists(self.backups))

    def test_fingerprint_not_in_keyring_refuses(self):
        with open(os.path.join(self.home, "loop1", "backup-key-fingerprint"), "w") as fh:
            fh.write(self.fpr + "\n")
        rc, out = self.run_bk("--execute")
        self.assertEqual(rc, 1)
        self.assertIn("not in the keyring", out)
        self.assertEqual(os.listdir(self.backups), [])

    def test_bad_fingerprint_text_refuses(self):
        with open(os.path.join(self.home, "loop1", "backup-key-fingerprint"), "w") as fh:
            fh.write("not-a-fingerprint\n")
        rc, out = self.run_bk("--execute")
        self.assertEqual(rc, 1)

    def test_a_secret_key_on_this_machine_refuses(self):
        r = sh(["gpg", "--batch", "--import"], dict(self.env, GNUPGHOME=self.gnupg), input=sh(["gpg", "--batch", "--armor", "--export-secret-keys", self.fpr], dict(self.env, GNUPGHOME=self.ceo)).stdout)
        self.put_key()
        rc, out = self.run_bk("--execute")
        self.assertEqual(rc, 1)
        self.assertIn("SECRET key is on this machine", out)

    def test_dry_run_changes_nothing(self):
        self.put_key()
        before = sorted(os.walk(self.home))
        rc, out = self.run_bk()
        self.assertEqual(rc, 0)
        self.assertIn("dry run", out)
        self.assertFalse(os.path.exists(self.backups))
        self.assertEqual(sorted(os.walk(self.home)), before)

    def test_archive_decrypts_every_file_matches_and_tokens_are_absent(self):
        self.put_key()
        rc, out = self.run_bk("--execute")
        self.assertEqual(rc, 0, out)
        name = "lifeos-backup-20261101.tar.gpg"
        self.assertTrue(os.path.exists(os.path.join(self.backups, name)))
        dest = self.decrypt(name)
        for a in ("coo", "cho", "cos", "cfo"):
            src = os.path.join(self.home, "loop1", "workspaces", a)
            for root, _, files in os.walk(src):
                for f in files:
                    p = os.path.join(root, f)
                    q = os.path.join(dest, a, os.path.relpath(p, src))
                    with open(p, "rb") as x, open(q, "rb") as y:
                        self.assertEqual(hashlib.sha256(x.read()).hexdigest(), hashlib.sha256(y.read()).hexdigest(), p)
        with open(os.path.join(dest, "openclaw.json")) as fh:
            text = fh.read()
        self.assertNotIn(SECRET, text)
        self.assertIn("<redacted>", text)
        self.assertEqual(json.loads(text)["channels"]["slack"]["accounts"]["default"]["enabled"], True)
        # the encrypted file itself holds no plain token either
        with open(os.path.join(self.backups, name), "rb") as fh:
            self.assertNotIn(SECRET.encode(), fh.read())
        self.assertNotIn(SECRET, out)

    def test_modes_and_sha_line(self):
        self.put_key()
        self.run_bk("--execute")
        self.assertEqual(stat.S_IMODE(os.stat(self.backups).st_mode), 0o700)
        for f in os.listdir(self.backups):
            self.assertEqual(stat.S_IMODE(os.stat(os.path.join(self.backups, f)).st_mode), 0o600, f)
        name = "lifeos-backup-20261101.tar.gpg"
        with open(os.path.join(self.backups, name + ".sha256")) as fh:
            line = fh.read().split()
        with open(os.path.join(self.backups, name), "rb") as fh:
            self.assertEqual(line[0], hashlib.sha256(fh.read()).hexdigest())
        self.assertEqual(line[1], name)

    def test_keep_the_last_four(self):
        self.put_key()
        for d in ("20261001", "20261008", "20261015", "20261022", "20261029", "20261105"):
            rc, out = self.run_bk("--execute", date=d)
            self.assertEqual(rc, 0, out)
        names = sorted(f for f in os.listdir(self.backups) if f.endswith(".tar.gpg"))
        self.assertEqual(names, ["lifeos-backup-%s.tar.gpg" % d for d in ("20261015", "20261022", "20261029", "20261105")])
        self.assertEqual(len([f for f in os.listdir(self.backups) if f.endswith(".sha256")]), 4)

    def test_other_files_in_the_folder_are_never_deleted(self):
        self.put_key()
        os.makedirs(self.backups, mode=0o700)
        keep = os.path.join(self.backups, "my-own-notes.txt")
        with open(keep, "w") as fh:
            fh.write("x")
        for d in ("20261001", "20261002", "20261003", "20261004", "20261005"):
            self.run_bk("--execute", date=d)
        self.assertTrue(os.path.exists(keep))

    def test_temp_folder_is_deleted(self):
        self.put_key()
        self.run_bk("--execute")
        self.assertEqual([f for f in os.listdir(self.backups) if f.startswith(".tmp")], [])

    def test_a_missing_workspace_stops_before_anything_is_written(self):
        self.put_key()
        shutil.rmtree(os.path.join(self.home, "loop1", "workspaces", "cfo"))
        rc, out = self.run_bk("--execute")
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.backups))

    def test_public_key_file_is_imported_when_present(self):
        with open(os.path.join(self.home, "loop1", "backup-public-key.asc"), "w") as fh:
            fh.write(self.pub)
        with open(os.path.join(self.home, "loop1", "backup-key-fingerprint"), "w") as fh:
            fh.write(self.fpr + "\n")
        rc, out = self.run_bk("--execute")
        self.assertEqual(rc, 0, out)
        self.decrypt("lifeos-backup-20261101.tar.gpg")

    def test_default_name_has_date_and_time(self):
        import re
        self.put_key()
        env = {k: v for k, v in self.env.items() if k != "BK_DATE"}
        r = sh(["bash", SCRIPT, "--execute"], env)
        self.assertEqual(r.returncode, 0, r.stderr)
        names = [f for f in os.listdir(self.backups) if f.endswith(".tar.gpg")]
        self.assertEqual(len(names), 1)
        self.assertTrue(re.match(r"^lifeos-backup-\d{8}-\d{4}\.tar\.gpg$", names[0]), names)

    def test_two_runs_in_the_same_minute_do_not_collide(self):
        self.put_key()
        self.assertEqual(self.run_bk("--execute", date="20261105-0600")[0], 0)
        first = os.path.join(self.backups, "lifeos-backup-20261105-0600.tar.gpg")
        with open(first, "rb") as fh:
            before = fh.read()
        self.assertEqual(self.run_bk("--execute", date="20261105-0600")[0], 0)
        names = sorted(f for f in os.listdir(self.backups) if f.endswith(".tar.gpg"))
        self.assertEqual(len(names), 2, names)
        with open(first, "rb") as fh:
            self.assertEqual(fh.read(), before)

    def test_old_date_only_names_still_count_for_keep_four(self):
        self.put_key()
        for d in ("20261001", "20261008", "20261015", "20261022", "20261029-0600", "20261105-0600"):
            self.assertEqual(self.run_bk("--execute", date=d)[0], 0)
        names = sorted(f for f in os.listdir(self.backups) if f.endswith(".tar.gpg"))
        self.assertEqual(len(names), 4, names)
        self.assertEqual(names[-1], "lifeos-backup-20261105-0600.tar.gpg")

    def test_manifest_inside_the_archive_lists_every_file_but_itself(self):
        self.put_key()
        self.run_bk("--execute")
        dest = self.decrypt("lifeos-backup-20261101.tar.gpg")
        listed = set()
        with open(os.path.join(dest, "FILES.sha256")) as fh:
            for line in fh:
                listed.add(line.rstrip("\n").split("  ", 1)[1])
        real = set()
        for base, _d, files in os.walk(dest):
            for n in files:
                p = "./" + os.path.relpath(os.path.join(base, n), dest)
                if p != "./FILES.sha256":
                    real.add(p)
        self.assertEqual(listed, real)

    def test_unknown_option_is_refused(self):
        rc, out = self.run_bk("--force")
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
