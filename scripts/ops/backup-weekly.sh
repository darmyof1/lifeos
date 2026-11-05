#!/usr/bin/env bash
# backup-weekly.sh - weekly encrypted backup of the four agent workspaces and a token-free copy of the OpenClaw config (APR-0113).
#   backup-weekly.sh              dry run: prints what --execute would do, changes nothing
#   backup-weekly.sh --execute    makes ~/loop1/backups/lifeos-backup-YYYYMMDD.tar.gpg and a .sha256 line, keeps the last 4
# Encrypts to a PUBLIC key only (fingerprint in ~/loop1/backup-key-fingerprint). The private key and any passphrase never live on this VM:
# the script refuses to run if the matching secret key is in this keyring. Prints no secrets. Deletes nothing but its own old backups
# (lifeos-backup-*.tar.gpg and their .sha256) and its own temp folder. No cron line is installed by this script.
set -uo pipefail
EXEC=0
case "${1:-}" in "") ;; --execute) EXEC=1 ;; -h|--help) sed -n 2,7p "$0"; exit 0 ;; *) echo "Usage: $0 [--execute]"; exit 2 ;; esac
L="$HOME/loop1"
WS="$L/workspaces"; CFG="$L/state/openclaw.json"; FPR_FILE="$L/backup-key-fingerprint"; KEYFILE="$L/backup-public-key.asc"
OUT="$L/backups"; KEEP=4
AGENTS="coo cho cos cfo"
DATE="${BK_DATE:-$(date +%Y%m%d)}"
say() { echo "$*"; }
die() { say "STOP: $*"; exit 1; }

[ -r "$FPR_FILE" ] || die "no public key fingerprint file ($FPR_FILE). Nothing done."
FPR="$(tr -d ' \t\r\n' < "$FPR_FILE")"
case "$FPR" in *[!0-9A-Fa-f]*|"") die "the fingerprint file does not hold a hex fingerprint. Nothing done." ;; esac
[ "${#FPR}" -ge 16 ] || die "the fingerprint is too short. Nothing done."
for a in $AGENTS; do [ -d "$WS/$a" ] || die "workspace $a is missing. Nothing done."; done
[ -r "$CFG" ] || die "the OpenClaw config is not readable. Nothing done."
command -v gpg >/dev/null || die "gpg is not installed."
if [ -r "$KEYFILE" ]; then say "public key file present: it will be imported (public part only)"; fi

if [ "$EXEC" = 0 ]; then
  say "BACKUP (dry run)"
  say "would copy: workspaces $AGENTS and the config with token-like fields replaced by <redacted>"
  say "would write: $OUT/lifeos-backup-$DATE.tar.gpg and a .sha256 line; keep the last $KEEP; encrypt to fingerprint ending ...${FPR: -8}"
  say "Run with --execute to act."
  exit 0
fi

( umask 077; mkdir -p "$OUT" ) || die "cannot create $OUT"
chmod 700 "$OUT"
if [ -r "$KEYFILE" ]; then gpg --batch --import "$KEYFILE" >/dev/null 2>&1; fi
gpg --batch --list-keys "$FPR" >/dev/null 2>&1 || die "the public key $FPR is not in the keyring. Nothing done."
if gpg --batch --list-secret-keys "$FPR" >/dev/null 2>&1; then die "the matching SECRET key is on this machine. The backup key must be public only. Nothing done."; fi

TMP="$(mktemp -d "$OUT/.tmp.XXXXXX")" || die "cannot make a temp folder"
case "$TMP" in "$OUT"/.tmp.*) ;; *) die "unexpected temp folder" ;; esac
cleanup() { case "$TMP" in "$OUT"/.tmp.*) rm -rf "$TMP" ;; esac; }
trap cleanup EXIT
chmod 700 "$TMP"
mkdir "$TMP/src" || die "temp"
for a in $AGENTS; do cp -a "$WS/$a" "$TMP/src/$a" || die "copy of $a failed"; done
python3 - "$CFG" "$TMP/src/openclaw.json" <<'PY' || die "could not make the token-free config"
import json, re, sys
c = json.load(open(sys.argv[1]))
def scrub(o):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if re.search(r"token|secret|password|apikey", k, re.I) and isinstance(v, str):
                o[k] = "<redacted>"
            else:
                scrub(v)
    elif isinstance(o, list):
        for x in o:
            scrub(x)
scrub(c)
json.dump(c, open(sys.argv[2], "w"), indent=1, sort_keys=True)
PY
( cd "$TMP/src" && find . -type f -print0 | sort -z | xargs -0 sha256sum > "$TMP/files.sha256" ) || die "file list failed"
( cd "$TMP/src" && cp "$TMP/files.sha256" ./FILES.sha256 && tar cf "$TMP/backup.tar" . ) || die "tar failed"
NAME="lifeos-backup-$DATE.tar.gpg"
( umask 077; gpg --batch --yes --trust-model always --recipient "$FPR" --encrypt -o "$OUT/$NAME" "$TMP/backup.tar" ) >/dev/null 2>&1 || die "encryption failed"
chmod 600 "$OUT/$NAME"
( cd "$OUT" && sha256sum "$NAME" > "$NAME.sha256" ) && chmod 600 "$OUT/$NAME.sha256"
FILES="$(wc -l < "$TMP/files.sha256")"
# keep the last $KEEP (names sort by date)
N=0
for f in $(ls -1 "$OUT"/lifeos-backup-*.tar.gpg 2>/dev/null | sort -r); do
  N=$((N+1))
  if [ "$N" -gt "$KEEP" ]; then rm -f "$f" "$f.sha256"; say "removed old backup $(basename "$f")"; fi
done
say "BACKUP done: $NAME, $(stat -c %s "$OUT/$NAME") bytes, $FILES files, mode $(stat -c %a "$OUT/$NAME")"
say "kept: $(ls -1 "$OUT"/lifeos-backup-*.tar.gpg | wc -l) of at most $KEEP"
exit 0
