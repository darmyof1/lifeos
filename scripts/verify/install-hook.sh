#!/usr/bin/env bash
# Installs a pre-commit hook that blocks commits when the validator fails. Run once per clone.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cat > "$ROOT/.git/hooks/pre-commit" <<'HOOK'
#!/usr/bin/env bash
ROOT="$(git rev-parse --show-toplevel)"
python3 "$ROOT/scripts/verify/validate_repo.py" || { echo "pre-commit: validator failed. Commit blocked."; exit 1; }
HOOK
chmod +x "$ROOT/.git/hooks/pre-commit"
echo "pre-commit hook installed."
