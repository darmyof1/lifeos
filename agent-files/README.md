# agent-files/ - the live instructions of the running agents

These are copies of the files the agents read on the VM (COO, CoS, CHO and CFO: AGENTS.md, SOUL.md, IDENTITY.md, USER.md). Other agents have empty placeholder files until they exist.

- SHA256SUMS lists the sha256 of the live files that were copied on 2026-10-27 (13 files; see the note below).
- The CoS, CHO and CFO AGENTS.md hold a placeholder instead of their Slack channel ID: {{COS_CHANNEL_ID}}, {{CHO_CHANNEL_ID}}, {{CFO_CHANNEL_ID}}. The real IDs live only on the VM, in ~/loop1/slack-channels.env (APR-0098). Their sha256 is therefore not in SHA256SUMS.
- The files are rebuilt from the scripts in deploy/loop1/ (loop1-agent-files.sh, then loop1-v13-upgrade.sh to loop1-v1105-upgrade.sh, in order). tests/unit/test_agent_files_rebuild.py does this in a temporary home with placeholder IDs and checks that every file here is byte for byte what the scripts produce.
- The VM health check compares each live file with its copy here (it fills the placeholders with the real IDs first). A difference is a FAIL: either the VM was changed without the repo, or the repo without the VM.
- Changing an agent's behaviour means a new upgrade script, a new approval entry and a new copy here. Nothing is edited by hand on the VM.
