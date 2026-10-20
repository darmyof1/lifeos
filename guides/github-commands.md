Here’s the sequence we’ve been using. Run these in Terminal on your Mac.
cd ~/Desktop/"Command & Control"/ArchitectureOS/LifeOS2.0/lifeos
git pull --ff-only
bash ~/Downloads/fix-NN.sh
git push origin main

1. Go to the repo and confirm you’re on main with a clean tree

cd ~/Desktop/"Command & Control"/ArchitectureOS/LifeOS2.0/lifeos
git branch --show-current
git status

Expected: main, and nothing to commit, working tree clean. If there are changes, stop and paste the output here.

2. Pull the latest main

git pull --ff-only
git log -1 --oneline

Expected: the top commit is b2a8fc9 research: SPK-03 partial ..., the fix-36 commit. If you see a newer commit, paste the line here before going on.

3. Run fix-37

Replace the path with where you saved the file (for example ~/Downloads/fix-37.sh):

bash ~/Downloads/fix-37.sh

The script runs the validator and commits only if it passes. Expected end lines: 0 blocking failure(s), then committed: <hash> research: SPK-04 Part A done ..., then Done. Nothing was pushed. If the validator reports a blocking failure, the script stops before committing. Paste the output here.

4. Check the commit before pushing

git show --stat HEAD

Expected six files: contracts/registry/artifacts.yaml, decisions/PENDING.md, guides/README.md, guides/slack-multi-identity.md, ops/install-log.md, research/spikes/SPK-04-slack-multi-identity.md.

5. Push to GitHub

git push origin main

Then check the repo on GitHub: the commit should appear on main, and guides/slack-multi-identity.md should be in the file list.