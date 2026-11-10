#!/usr/bin/env bash
# coo-compact.sh - the COO's morning compaction (Loop 6, APR-0121). Since Loop 7 (APR-0126) a thin wrapper around agent-compact.sh with the agent "coo".
# Same options (--execute), same log file (~/loop1/state/coo-compact.log), same exit codes, same COO_COMPACT_* test hooks. See agent-compact.sh.
exec bash "$(dirname "$(readlink -f "$0")")/agent-compact.sh" coo "$@"
