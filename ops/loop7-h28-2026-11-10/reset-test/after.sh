#!/usr/bin/env bash
cd ~/scratch28
while [ "$(TZ=America/Puerto_Rico date +%H%M)" -lt 0301 ]; do sleep 5; done
TZ=America/Puerto_Rico date +%H:%M:%S > out/after-start.txt
for g in g1 g2; do
 ./ask.sh $g p agent:p:main loop7-rst-$g-p-after out/$g-p-after.txt &
 ./ask.sh $g q agent:q:slack:channel:test28$g loop7-rst-$g-q-after out/$g-q-after.txt &
done; wait
echo done > out/after-done.txt
