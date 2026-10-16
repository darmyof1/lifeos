# Design

Hand-written design documents live directly in design/ (for example roster.md). A person writes and approves them.

design/generated/ is for files a script produces from a source. Nobody edits a generated file by hand. A generated file names its source and its script in its first lines. Generators are not all built yet; placeholders there are 0 bytes until their generator exists.

Agent roster: design/roster.md is the source. contracts/agents.yaml is generated from it by scripts/verify/roster_to_agents.py (APR-0038, P-16).
