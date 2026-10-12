#!/usr/bin/env bash
# Runs the repo validator. Exit 1 on any blocking failure.
exec python3 "$(git rev-parse --show-toplevel)/scripts/verify/validate_repo.py"
