# VM spike runbook (SPK-07, SPK-02, SPK-01, SPK-03, SPK-04)

Purpose: prove the runtime pieces work on the Oracle VM before Genesis. Each spike has a pass criterion written before it runs, a method, and a result to send back.
Run them in this order. SPK-07 needs no OpenClaw, so it can run first.

## Rules for every spike
1. Use a test identity only. Test agents already running on the VM keep their data: do not change their directories, config or Slack channels.
2. Never paste a token, API key, password, hostname or IP into chat or into a result file. Redact before sending results back.
3. Slack tests run only in a test workspace you create for this (see SPK-04 setup). Never your real workspace.
4. Before SPK-02 or SPK-03, copy the OpenClaw directory: cp -a ~/.openclaw ~/.openclaw.bak-$(date +%Y%m%d) (skip if the directory does not exist yet).
5. Record exit codes with the method in guides/measure-a-cli-call.md: read $? straight after the command. In zsh, PIPESTATUS is empty.

## What you need
- SSH access to the VM (user ubuntu).
- Ollama with llama3.1:8b installed (SPK-06 already ran this).
- A free Slack workspace for testing, created at slack.com.
- No Anthropic or OpenAI key is needed for any spike here. The local model does the text work.

---

## Step 1 - SPK-07: GPG restore drill (no OpenClaw needed)

Question: can an encrypted archive be restored from its key and passphrase alone, and can the VM encrypt without ever holding the restore secret?

Pass criteria (written before running):
- Part A: the restored file's SHA-256 matches the reference hash saved before the original was deleted. A wrong passphrase fails with a nonzero exit code and writes no output.
- Part B: the VM encrypts with a public key with no prompt. The VM cannot decrypt. The CEO key restores the file with a matching SHA-256.

Rules: type passphrases only at the prompt. Never write a passphrase into a file or into chat.

### Part A - symmetric (passphrase)

    mkdir -p ~/spk07 && cd ~/spk07
    rm -f original.bin archive.gpg restored.bin wrong.bin
    head -c 5000000 /dev/urandom > original.bin
    sha256sum original.bin | cut -d' ' -f1 > original.sha256     # reference hash, saved BEFORE the original is deleted
    gpg --symmetric --cipher-algo AES256 --output archive.gpg original.bin     # type the passphrase
    rm original.bin
    gpgconf --kill gpg-agent                                     # clears the cached passphrase, so the next command prompts
    rm -f restored.bin
    gpg --decrypt --output restored.bin archive.gpg; echo "exit=$?"     # type the correct passphrase
    [ "$(cat original.sha256)" = "$(sha256sum restored.bin | cut -d' ' -f1)" ] && echo MATCH || echo NOMATCH
    gpgconf --kill gpg-agent
    rm -f wrong.bin
    gpg --decrypt --output wrong.bin archive.gpg; echo "exit=$?"     # type a WRONG passphrase
    ls

Expected: MATCH. The wrong passphrase gives "Bad session key" with a nonzero exit code, and wrong.bin is not listed.

### Part B - asymmetric (VM holds only the public key; CEO restores)

    mkdir -p -m 700 ~/spk07/b && cd ~/spk07/b
    export GNUPGHOME=$HOME/spk07/b/ceo && mkdir -p -m 700 "$GNUPGHOME"
    gpg --quick-gen-key "spk07 ceo test" ed25519 default never     # type a passphrase for the CEO key
    FPR=$(gpg --list-keys --with-colons "spk07 ceo test" | awk -F: '/^fpr:/ {print $10; exit}')
    gpg --quick-add-key "$FPR" cv25519 encr never                 # adds the encryption subkey; type the CEO passphrase
    gpg --list-keys "spk07 ceo test"                              # must show a sub line with [E]
    gpg --armor --export "spk07 ceo test" > ceo-public.asc
    head -c 5000000 /dev/urandom > data.bin
    sha256sum data.bin | cut -d' ' -f1 > data.sha256
    rm -rf ~/spk07/b/agent && export GNUPGHOME=$HOME/spk07/b/agent && mkdir -p -m 700 "$GNUPGHOME"
    gpg --import ~/spk07/b/ceo-public.asc
    gpg --list-secret-keys; echo "(none should be listed)"
    gpg --batch --yes --trust-model always --encrypt --recipient "spk07 ceo test" --output ~/spk07/b/archive-pub.gpg ~/spk07/b/data.bin; echo "encrypt exit=$?"
    rm ~/spk07/b/data.bin
    gpg --batch --decrypt --output ~/spk07/b/should-fail.bin ~/spk07/b/archive-pub.gpg; echo "agent decrypt exit=$?"
    export GNUPGHOME=$HOME/spk07/b/ceo && gpgconf --kill gpg-agent && rm -f ~/spk07/b/restored-pub.bin
    gpg --decrypt --output ~/spk07/b/restored-pub.bin ~/spk07/b/archive-pub.gpg; echo "ceo exit=$?"     # type the CEO passphrase
    [ "$(cat ~/spk07/b/data.sha256)" = "$(sha256sum ~/spk07/b/restored-pub.bin | cut -d' ' -f1)" ] && echo MATCH || echo NOMATCH
    export GNUPGHOME=$HOME/.gnupg

Expected: a sub line with [E] after the add; encrypt exit 0 with no prompt; the agent's decrypt exit 2 with "No secret key" (not "No such file"); CEO exit 0 after the passphrase prompt, then MATCH.

Send back: the exit codes and MATCH/NOMATCH lines for both parts. Never the passphrases.

---

## Step 2 - SPK-01: can the host block outbound calls per process?

Question: can the VM block outbound network access for one agent's user, while the local model on loopback still answers?

Pass criterion: the test user cannot reach the internet (exit code nonzero, no HTTP response), and the same user can reach the local model at 127.0.0.1:11434.

Method:
    sudo iptables -S OUTPUT | head -20      # save this output; check for existing rules first
    sudo useradd --system --no-create-home --shell /usr/sbin/nologin oc-spk01
    sudo iptables -I OUTPUT 1 -m owner --uid-owner oc-spk01 ! -o lo -j REJECT
    sudo -u oc-spk01 curl -sS -m 10 https://example.com -o /dev/null; echo "internet exit=$?"
    sudo -u oc-spk01 curl -sS -m 10 http://127.0.0.1:11434/api/tags -o /dev/null; echo "local exit=$?"
    curl -sS -m 10 https://example.com -o /dev/null; echo "normal user exit=$?"
    # cleanup (always run this)
    sudo iptables -D OUTPUT -m owner --uid-owner oc-spk01 ! -o lo -j REJECT
    sudo userdel oc-spk01

Expected: internet exit nonzero; local exit 0; normal user exit 0.
Safety: the rule only matches the test user. It does not touch SSH or your user. If the rule blocks anything else, run the cleanup line.
Send back: the three exit codes and the iptables -S output before the change (redacted).

---

## Step 3 - SPK-02: does OpenClaw honour a state-directory override?

Question: can OpenClaw keep its state somewhere other than ~/.openclaw?

Background (from OpenClaw's agent documentation): the state directory is ~/.openclaw, the config is ~/.openclaw/openclaw.json, and the docs do not name an environment variable or setting that moves the state directory. So this spike tests it directly.

Pass criterion: a setup run with HOME pointed at a test folder creates all state under that folder and nothing under the real ~/.openclaw. A named override, if one exists, must also work.

Step 3a - find out what the CLI offers (paste the output to me before step 3b):
    openclaw --version
    openclaw --help
    openclaw setup --help
    env | grep -i openclaw        # empty is fine; do not paste secrets

Step 3b - HOME test (the CLI may need a moment to create files):
    mkdir -p ~/spk02/home
    HOME=~/spk02/home openclaw setup
    echo "exit=$?"
    find ~/spk02/home -maxdepth 3 | sort | head -50
    ls -la ~/.openclaw 2>/dev/null | head -5; echo "real state untouched check done"

Pass: exit 0, and the find output shows ~/spk02/home/.openclaw with openclaw.json and state/openclaw.sqlite. Nothing new under the real ~/.openclaw (compare with the backup from rule 4).

Step 3c - if 3a shows an override option, test it the same way and record its exact name.

Send back: the help output from 3a (redacted), the exit code and the find output from 3b.
Note: do not run openclaw setup against the real ~/.openclaw during this spike unless the test agents are stopped first.

---

## Step 4 - SPK-03: are agent workspaces isolated from each other?

Question: can one agent read another agent's workspace files?

Pass criterion: an agent in workspace B cannot read a canary file in workspace A, with the isolation setting turned on. Record the setting that was on and whether it is needed.

Step 4a - paste to me the help output for agents and sandbox (commands below) before creating any agent:
    openclaw agents --help
    openclaw config --help
    # if the sub-commands differ, paste the closest help output

From the OpenClaw docs, the workspace is set by agents.defaults.workspace or agents.entries.<id>.workspace, and sandbox sessions use agents.defaults.sandbox.workspaceRoot. The exact syntax comes from 4a, so I will write the config from your output.

Step 4b - create two test agents (spk03-a, spk03-b) with separate workspaces under ~/spk03/. Put a canary file only in A:
    mkdir -p ~/spk03/ws-a ~/spk03/ws-b
    echo "CANARY-A-$(date +%s)" > ~/spk03/ws-a/canary.txt

Step 4c - ask agent spk03-b, through its normal session, to read ~/spk03/ws-a/canary.txt and to list ~/spk03/ws-a. Run once with the isolation setting off, once with it on (I will tell you the key from 4a).

Send back: the setting used in each run, and what B answered (did it read the canary?).

---

## Step 5 - SPK-04: can several bots post to one channel, without context leaking?

Question: can separate agents post to one Slack channel under their own display names, and does one agent see another's messages unless they are routed to it?

Pass criteria:
- Part A (identity): two posts from one bot token, each shown with its own display name in the channel.
- Part B (local model): the local model writes the text, and a post with that text appears in the channel. No cloud model call happens.
- Part C (leakage): agent B cannot quote a canary that agent A posted, unless the channel message was routed to B.

Setup (test workspace only):
1. Create a free Slack workspace for testing.
2. Create a channel: spk04-test. Note its channel ID (channel details, bottom).
3. Create a Slack app from scratch. Add these bot token scopes: chat:write, chat:write.customize, channels:history, channels:read.
4. Install the app to the test workspace. Copy the Bot User OAuth Token (starts with xoxb-).
5. Put it in a file only you can read:
       mkdir -p ~/spk04 && chmod 700 ~/spk04
       printf 'SLACK_BOT_TOKEN=%s\n' 'PASTE_TOKEN_HERE' > ~/spk04/slack.env
       chmod 600 ~/spk04/slack.env
   Replace PASTE_TOKEN_HERE in your own terminal. Never paste it in chat.
6. In the Slack channel, type /invite @your-app-name.

Part A - identity (plain curl, no model):
    source ~/spk04/slack.env
    CH="PASTE_CHANNEL_ID"
    for name in agent-one agent-two; do
      curl -s -X POST https://slack.com/api/chat.postMessage \
        -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
        -H "Content-type: application/json; charset=utf-8" \
        -d "{\"channel\":\"$CH\",\"text\":\"test from $name\",\"username\":\"$name\"}" | head -c 200; echo
    done
Pass: both messages show in the channel under agent-one and agent-two. If Slack shows only the app name, the display-name option did not work and that is a finding to record.

Part B - local model writes, Slack posts (no cloud):
    cat > ~/spk04/local_post.sh <<'SH'
    #!/usr/bin/env bash
    set -euo pipefail
    source ~/spk04/slack.env
    CH="$1"
    TEXT=$(curl -s http://127.0.0.1:11434/api/generate \
      -d '{"model":"llama3.1:8b","prompt":"Write one friendly sentence, under 20 words, greeting a test channel.","stream":false}' \
      | python3 -c 'import sys,json; print(json.load(sys.stdin)["response"].strip())')
    echo "model said: $TEXT"
    BODY=$(python3 -c 'import json,sys; print(json.dumps({"channel":sys.argv[1],"text":sys.argv[2],"username":"local-model"}))' "$CH" "$TEXT")
    curl -s -X POST https://slack.com/api/chat.postMessage \
      -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
      -H "Content-type: application/json; charset=utf-8" -d "$BODY" \
      | python3 -c 'import sys,json; r=json.load(sys.stdin); print("posted" if r.get("ok") else r)'
    SH
    chmod +x ~/spk04/local_post.sh
    ~/spk04/local_post.sh PASTE_CHANNEL_ID
Pass: "model said" shows a sentence, and the message appears in Slack under local-model. The model call went only to 127.0.0.1.

Part C - leakage (needs OpenClaw; I will write the setup after you paste the help output):
    openclaw agents --help
    openclaw channels --help
Plan: agent A posts CANARY-A-<number> in spk04-test. Agent B is asked, in its own session and without that message routed to it, to repeat the canary. Pass: B does not repeat it. Then route the message to B and ask again: B should now repeat it. Both results matter.

Send back: the Part A and Part B results (the posts shown in Slack, and the python "posted" line), and the help output for Part C. Never the token.

---

## After each step
Fill in the matching file from research/spikes/_TEMPLATE.md: Status, Date run, Method, Result (with units and pass or fail), Evidence (redacted), Conclusion, Redaction log. Send it back to me with the command output.
