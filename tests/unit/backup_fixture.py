"""Shared fixture for the Loop 4 backup tests: throwaway RSA key (no passphrase), a fake home with four synthetic workspaces, a local bare git repository as the remote. No real key, no real data."""
import json, os, shutil, subprocess, tarfile, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "scripts", "ops")
HAVE = bool(shutil.which("gpg") and shutil.which("git") and shutil.which("sha256sum"))


def sh(cmd, env=None, **kw):
    return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=180, **kw)


class Keys:
    """One throwaway key pair; ceo = keyring with the private key, pub = armored public block, fpr = fingerprint."""
    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="bk-keys-", dir="/tmp")
        self.ceo = os.path.join(self.dir, "ceo")
        os.mkdir(self.ceo, 0o700)
        spec = os.path.join(self.dir, "spec")
        with open(spec, "w") as fh:
            fh.write("%no-protection\nKey-Type: RSA\nKey-Length: 2048\nSubkey-Type: RSA\nSubkey-Length: 2048\nName-Real: Test CEO\nExpire-Date: 0\n%commit\n")
        env = dict(os.environ, GNUPGHOME=self.ceo)
        r = sh(["gpg", "--batch", "--gen-key", spec], env)
        assert r.returncode == 0, r.stderr
        out = sh(["gpg", "--batch", "--with-colons", "--list-keys"], env).stdout
        self.fpr = [l.split(":")[9] for l in out.splitlines() if l.startswith("fpr:")][0]
        self.pub = sh(["gpg", "--batch", "--armor", "--export", self.fpr], env).stdout

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class Home:
    """A fake VM home: workspaces, config, public key in its own keyring, a bare remote, backup.env."""
    def __init__(self, keys, tmp):
        self.keys, self.tmp = keys, tmp
        self.home = os.path.join(tmp, "home")
        self.gnupg = os.path.join(tmp, "gnupg")
        os.mkdir(self.gnupg, 0o700)
        for a in ("coo", "cho", "cos", "cfo", "clo"):
            d = os.path.join(self.home, "loop1", "workspaces", a, "state")
            os.makedirs(d)
            with open(os.path.join(d, "note.md"), "w") as fh:
                fh.write("synthetic note for " + a + "\n")
            with open(os.path.join(self.home, "loop1", "workspaces", a, "AGENTS.md"), "w") as fh:
                fh.write("# Agent " + a + " synthetic heading\n")
        os.makedirs(os.path.join(self.home, "loop1", "state"))
        with open(os.path.join(self.home, "loop1", "state", "openclaw.json"), "w") as fh:
            json.dump({"gateway": {"auth": {"token": "tok-synthetic-123456"}}, "agents": {"list": ["coo"]}}, fh)
        self.env = {"HOME": self.home, "PATH": os.environ["PATH"], "GNUPGHOME": self.gnupg}
        r = sh(["gpg", "--batch", "--import"], self.env, input=keys.pub)
        assert r.returncode == 0, r.stderr
        with open(os.path.join(self.home, "loop1", "backup-key-fingerprint"), "w") as fh:
            fh.write(keys.fpr + "\n")
        self.remote = os.path.join(tmp, "remote.git")
        sh(["git", "init", "-q", "--bare", "-b", "main", self.remote])
        self.write_env()

    @property
    def backups(self):
        return os.path.join(self.home, "loop1", "backups")

    @property
    def clone(self):
        return os.path.join(self.home, "loop1", "backup-repo")

    def write_env(self, url=None, mode=0o600):
        p = os.path.join(self.home, "loop1", "backup.env")
        with open(p, "w") as fh:
            fh.write("BACKUP_REPO_URL=%s\nBACKUP_BRANCH=main\n" % (url or self.remote))
        os.chmod(p, mode)

    def run(self, script, *args, date=None):
        env = dict(self.env)
        if date:
            env["BK_DATE"] = date
        r = sh(["bash", os.path.join(OPS, script), *args], env)
        return r.returncode, r.stdout + r.stderr

    def remote_log(self):
        r = sh(["git", "-C", self.remote, "log", "--format=%s", "main"])
        return r.stdout.split("\n")[:-1] if r.returncode == 0 else []

    def remote_files(self, rev="main"):
        r = sh(["git", "-C", self.remote, "ls-tree", "-r", "--name-only", rev])
        return sorted(r.stdout.split()) if r.returncode == 0 else []

    def ceo_env(self):
        return dict(self.env, GNUPGHOME=self.keys.ceo)
