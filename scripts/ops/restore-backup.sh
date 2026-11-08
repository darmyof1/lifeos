#!/usr/bin/env bash
# restore-backup.sh - restore a LifeOS backup archive into a NEW folder and check every file (Loop 4, APR-0117).
#   restore-backup.sh ARCHIVE.tar.gpg TARGET_DIR
#   restore-backup.sh --latest BACKUP_REPO_CLONE_DIR TARGET_DIR     (newest lifeos-backup-*.tar.gpg in that folder)
# Needs the PRIVATE backup key in your local gpg keyring; gpg asks for the passphrase itself (it is never taken from the command line).
# TARGET_DIR must not exist or must be empty, and must not be inside ~/loop1/workspaces or ~/loop1/state (never a live folder).
# Checks every file against FILES.sha256 inside the archive and prints: files, mismatches, elapsed seconds.
# Exit status is 0 only with at least one file and 0 mismatches. Works on macOS and Linux (bash 3.2, sha256sum or shasum).
set -uo pipefail
LATEST=0
case "${1:-}" in --latest) LATEST=1; shift ;; -h|--help) sed -n 2,8p "$0"; exit 0 ;; esac
[ $# -eq 2 ] || { echo "Usage: $0 [--latest] ARCHIVE_OR_REPO_DIR TARGET_DIR"; exit 2; }
SRC="$1"; TARGET="$2"
die() { echo "STOP: $*"; exit 1; }
command -v gpg >/dev/null || die "gpg is not installed (macOS: brew install gnupg)."
if command -v sha256sum >/dev/null; then hash_of() { sha256sum < "$1" | awk '{print $1}'; }; else hash_of() { shasum -a 256 < "$1" | awk '{print $1}'; }; fi

if [ "$LATEST" = 1 ]; then
  [ -d "$SRC" ] || die "$SRC is not a folder."
  ARCH="$(ls -1 "$SRC" | grep -E '^lifeos-backup-.*\.tar\.gpg$' | sort | tail -1)"
  [ -n "$ARCH" ] || die "no lifeos-backup-*.tar.gpg in $SRC."
  ARCH="$SRC/$ARCH"
else
  [ -f "$SRC" ] || die "$SRC is not a file (for a repository folder use --latest)."
  ARCH="$SRC"
fi

# absolute path of the target without needing it to exist
case "$TARGET" in /*) ABS="$TARGET" ;; *) ABS="$(pwd -P)/$TARGET" ;; esac
PARENT="$(cd "$(dirname "$ABS")" 2>/dev/null && pwd -P)" || die "the parent folder of $TARGET does not exist."
ABS="$PARENT/$(basename "$ABS")"
for LIVE in "$HOME/loop1/workspaces" "$HOME/loop1/state"; do
  LP="$(cd "$LIVE" 2>/dev/null && pwd -P || echo "$LIVE")"
  case "$ABS/" in "$LP"/*|"$LIVE"/*) die "$TARGET is inside a live folder ($LIVE). Choose a new folder." ;; esac
done
if [ -e "$ABS" ]; then
  [ -d "$ABS" ] || die "$TARGET exists and is not a folder."
  [ -z "$(ls -A "$ABS")" ] || die "$TARGET is not empty. Choose a new or empty folder."
fi

# the .sha256 line next to the archive, if present, must match
SUM="$ARCH.sha256"
if [ -f "$SUM" ]; then
  WANT="$(awk '{print $1}' "$SUM" | head -1)"; GOT="$(hash_of "$ARCH")"
  [ "$WANT" = "$GOT" ] || die "the archive does not match its .sha256 line. Nothing restored."
  echo "archive checksum line: OK"
fi

START="$(date +%s)"
mkdir -p "$ABS" || die "cannot create $TARGET."
gpg --decrypt "$ARCH" 2>/dev/null | tar xf - -C "$ABS"
RC=("${PIPESTATUS[@]}")
if [ "${RC[0]}" != 0 ] || [ "${RC[1]}" != 0 ]; then
  echo "STOP: decryption or extraction failed (wrong key or passphrase, or damaged archive). The folder $TARGET may hold partial files; delete it."
  exit 1
fi
[ -f "$ABS/FILES.sha256" ] || die "the archive has no FILES.sha256 manifest. Restored files are NOT verified."

FILES=0; BAD=0
while IFS= read -r line; do
  [ -n "$line" ] || continue
  h="${line%%  *}"; p="${line#*  }"
  FILES=$((FILES+1))
  if [ ! -f "$ABS/$p" ]; then BAD=$((BAD+1)); echo "MISSING $p"; continue; fi
  [ "$(hash_of "$ABS/$p")" = "$h" ] || { BAD=$((BAD+1)); echo "DIFFERENT $p"; }
done < "$ABS/FILES.sha256"
# files that are not in the manifest also count
MT="$(mktemp)"; sed 's/^[^ ]*  //' "$ABS/FILES.sha256" | sort > "$MT"
EXTRA="$( cd "$ABS" && find . -type f ! -name FILES.sha256 | sort | comm -13 "$MT" - | wc -l | tr -d ' ' )"
rm -f "$MT"
BAD=$((BAD+EXTRA)); [ "$EXTRA" = 0 ] || echo "files not in the manifest: $EXTRA"
END="$(date +%s)"
echo "files: $FILES"
echo "mismatches: $BAD"
echo "elapsed seconds: $((END-START))"
[ "$FILES" -gt 0 ] && [ "$BAD" = 0 ]
