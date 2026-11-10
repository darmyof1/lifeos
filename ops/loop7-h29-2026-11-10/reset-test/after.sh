#!/usr/bin/env bash
cd ~/scratch29
while [ "$(TZ=America/Puerto_Rico date +%H%M)" -lt 1501 ]; do sleep 5; done
TZ=America/Puerto_Rico date +%H:%M:%S > out/after-start.txt
for r in direct-p1 direct-q1 send-p2 send-q2; do ./ask.sh $r loop29-rst-$r-after out/$r-after.txt & done
./chat.sh loop29-rst-chat-q3-after out/chat-q3-after.txt &
wait; sleep 20
. ./snap.sh; snap > out/sessions-after.txt
echo done > out/after-done.txt
