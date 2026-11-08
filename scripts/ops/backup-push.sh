#!/usr/bin/env bash
# backup-push.sh - put the newest encrypted backup archive into the private backup repository (Loop 4, APR-0117).
#   backup-push.sh              dry run: checks the newest archive and the settings, prints what --execute would do, changes nothing
#   backup-push.sh --execute    copies the newest archive and its .sha256 line into the clone, commits "backup <name>", pushes (never forced)
# Settings come from ~/loop1/backup.env (mode 600): BACKUP_REPO_URL=... and BACKUP_BRANCH=... (the address is never printed or logged).
# Optional there: BACKUP_SSH_KEY=path (default ~/loop1/backup-deploy-key, the deploy key for that one repository).
# Refuses: an archive that is not gpg-encrypted data, a clone with uncommitted changes, a clone that has diverged from the remote, a failed push.
set -uo pipefail
EXEC=0
case "${1:-}" in "") ;; --execute) EXEC=1 ;; -h|--help) sed -n 2,7p "$0"; exit 0 ;; *) echo "Usage: $0 [--execute]"; exit 2 ;; esac
L="$HOME/loop1"; ENVF="$L/backup.env"; OUT="$L/backups"; CLONE="$L/backup-repo"
say() { echo "$*"; }
die() { say "STOP: $*"; exit 1; }
command -v git >/dev/null || die "git is not installed."
command -v gpg >/dev/null || die "gpg is not installed."

[ -f "$ENVF" ] || die "no settings file ($ENVF). Nothing done."
PERM="$(stat -c %a "$ENVF" 2>/dev/null || stat -f %Lp "$ENVF" 2>/dev/null)"
[ "$PERM" = 600 ] || die "the settings file must have mode 600 (it has $PERM). Nothing done."
getv() { sed -n "s/^$1=//p" "$ENVF" | head -1 | tr -d "\"'\r"; }
URL="$(getv BACKUP_REPO_URL)"; BRANCH="$(getv BACKUP_BRANCH)"; KEY="$(getv BACKUP_SSH_KEY)"
[ -n "$URL" ] || die "BACKUP_REPO_URL is not set in the settings file. Nothing done."
BRANCH="${BRANCH:-main}"; KEY="${KEY:-$L/backup-deploy-key}"
case "$BRANCH" in *[!A-Za-z0-9._/-]*|"") die "BACKUP_BRANCH has odd characters. Nothing done." ;; esac
export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$L/backup-known-hosts"
export GIT_TERMINAL_PROMPT=0

NEWEST="$(ls -1t "$OUT"/lifeos-backup-*.tar.gpg 2>/dev/null | head -1)"
[ -n "$NEWEST" ] || die "no backup archive in $OUT. Run backup-weekly.sh --execute first. Nothing done."
NAME="$(basename "$NEWEST")"; SUMF="$NEWEST.sha256"
[ -f "$SUMF" ] || die "no .sha256 line for $NAME. Nothing done."
PK="$(gpg --batch --list-packets "$NEWEST" 2>&1 || true)"
echo "$PK" | grep -q "pubkey enc packet" || die "$NAME is not gpg-encrypted data. Nothing pushed."
( cd "$OUT" && { command -v sha256sum >/dev/null && sha256sum -c "$NAME.sha256" || shasum -a 256 -c "$NAME.sha256"; } ) >/dev/null 2>&1 || die "$NAME does not match its .sha256 line. Nothing pushed."

if [ "$EXEC" = 0 ]; then
  say "PUSH (dry run)"
  say "archive: $NAME ($(wc -c < "$NEWEST" | tr -d ' ') bytes), encrypted, checksum line matches"
  say "would: update the clone $CLONE (clone it if missing), copy the archive and its .sha256 line, commit 'backup $NAME', push branch $BRANCH (no force)"
  say "Run with --execute to act."
  exit 0
fi

g() { git -C "$CLONE" "$@"; }
if [ ! -d "$CLONE/.git" ]; then
  [ ! -e "$CLONE" ] || [ -z "$(ls -A "$CLONE" 2>/dev/null)" ] || die "$CLONE exists and is not a git clone. Nothing done."
  git clone -q "$URL" "$CLONE" >/dev/null 2>&1 || die "could not clone the backup repository (key, address or network). Nothing done."
fi
[ -z "$(g status --porcelain)" ] || die "the backup clone has uncommitted changes. Nothing pushed."
g remote set-url origin "$URL" >/dev/null 2>&1
g fetch -q origin >/dev/null 2>&1 || die "could not reach the backup repository (fetch failed). Nothing pushed."
if g rev-parse -q --verify "refs/remotes/origin/$BRANCH" >/dev/null; then
  g checkout -q "$BRANCH" >/dev/null 2>&1 || g checkout -q -B "$BRANCH" "origin/$BRANCH" >/dev/null 2>&1 || die "cannot check out branch $BRANCH. Nothing pushed."
  g merge -q --ff-only "origin/$BRANCH" >/dev/null 2>&1 || die "the clone and the remote have diverged. Nothing pushed (never forced)."
else
  g symbolic-ref HEAD "refs/heads/$BRANCH" >/dev/null 2>&1 || die "cannot start branch $BRANCH. Nothing pushed."
fi
if [ -f "$CLONE/$NAME" ]; then
  cmp -s "$NEWEST" "$CLONE/$NAME" && { say "PUSH: $NAME is already in the backup repository. Nothing to do."; exit 0; }
  die "$NAME exists in the backup repository with different content. Nothing pushed."
fi
cp "$NEWEST" "$CLONE/$NAME" && cp "$SUMF" "$CLONE/$NAME.sha256" || die "copy into the clone failed."
g add -- "$NAME" "$NAME.sha256"
AT=@
g -c user.name=lifeos-backup -c "user.email=lifeos-backup${AT}localhost" commit -q -m "backup $NAME" >/dev/null 2>&1 || die "commit failed."
if g push -q origin "HEAD:refs/heads/$BRANCH" >/dev/null 2>&1; then
  say "PUSH done: $NAME ($(wc -c < "$NEWEST" | tr -d ' ') bytes) to branch $BRANCH"
  exit 0
fi
g reset -q --hard "HEAD~1" >/dev/null 2>&1
die "the push failed (nothing was forced). The local commit was undone; the clone is clean."
