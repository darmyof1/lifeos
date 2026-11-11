#!/usr/bin/env bash
cd ~/handover/h30
A=scripts/ask.sh; O=clo
$A clo loop30-clo-001 "I started watching Show One, season 1, episode 3." $O >/dev/null
$A clo loop30-clo-002 "I am now at Show One, season 1, episode 5." $O >/dev/null
$A clo loop30-clo-003 "Add Show Two to my list as planned." $O >/dev/null
$A clo loop30-clo-004 "I finished Show One." $O >/dev/null
$A clo loop30-clo-005 "What am I watching and what is next?" $O >/dev/null
$A clo loop30-clo-006 "Look up when Show One returns" $O >/dev/null
echo batch-done > clo/batch1.done
