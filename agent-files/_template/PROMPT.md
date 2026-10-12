---
spec_name: [specialist-name]
spec_type: transient-specialist
version: 1.0
last_updated: YYYY-MM-DD
parent_agent: [CHO|CFO|CCO|CFA|CLO|CSO|CSP|CDO]
invocation_trigger: [when parent invokes this specialist]
est_tokens: [approximate token cost per invocation]
status: active
---

# Specialist: [Human-Readable Name]

## Purpose
[One sentence describing what this specialist does and why it exists.]

## Invocation Trigger
[When does the parent agent invoke this specialist? Be specific.]

Example:
- Parent receives a request containing keywords [X, Y, Z]
- Parent needs to [specific task]
- Parent cannot handle the request directly because [reason]

## Input Contract
[What the specialist needs to receive from the parent.]

| Input | Type | Source | Required? |
|-------|------|--------|-----------|
| [input 1] | [string/md/json] | [source] | Yes/No |
| [input 2] | ... | ... | ... |

## Output Contract
[What the specialist returns to the parent.]

| Output | Type | Destination | Format |
|--------|------|-------------|--------|
| [output 1] | [markdown/json] | [parent/domain file] | [schema ref] |

## Execution Steps
[Numbered steps the specialist follows. Deterministic where possible.]

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Prompt Template
[The actual prompt the parent sends. Use {placeholders} for variables.]
