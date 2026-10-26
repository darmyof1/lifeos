# ADR-0011 — Append-only history, projected state

Status: accepted
Date: 2026-10-26
Approval basis: APR-0013 (state snapshots plus append-only logs); APR-0054, APR-0057, APR-0058 (the calendar journal); APR-0061 (dreaming off); APR-0072 (14-day active window); APR-0085 (memory for Loop 2).

## Context
Agents are models. A model that rewrites its own memory can lose or change facts without anyone seeing it. LifeOS needs a record that can be checked and replayed, and state that can be rebuilt from it.

## Decision
- History is written by appending lines to files. A line is never edited or deleted. A correction is a new line.
- Current state is a projection of the history: the latest line for a name decides. A snapshot may be kept, but the history wins if they differ.
- A move, a failure or a deletion is a new line with a status (moved, failed, deleted), not an edit of the old line.
- Agents keep their working memory in these state files (for example the calendar journal and the health plan), not in a model-managed memory. Memory search and dreaming stay off (APR-0061, APR-0085).
- Anything that changes Google or another outside system is done by code that reads the history (the push job, scripts/gcal/gcal_sync.py), not by the model.

## Working example (implemented and tested)
The CoS calendar journal (APR-0054): header `name | start | end | status | run ID | event ID | requested by [| detail]`. The push job takes the latest line per name, appends its own lines (pushed, failed with an attempt count, conflict) and never rewrites a line. Scenario runs check this with `git diff --numstat` on the journal: additions only, no deletions.

## Alternatives rejected
- Editable state files: a wrong edit leaves no trace.
- Model-managed memory (dreaming, nightly rewrites): conflicts with append-only history (APR-0061).

## Consequences
- Implementation status (2026-10-26): the calendar journal and push job follow this rule and are tested. A general snapshot and rebuild tool (scenario S-18) is not built.
- Files grow. The calendar journal has a 14-day active window with a monthly archive (APR-0072); the archive job is not built, and is needed when the journal reaches about 1,000 lines (P-40).
- Memory beyond state files (local embeddings, what the COO keeps versus asks for) is open in P-41.
