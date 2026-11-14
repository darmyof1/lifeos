#!/usr/bin/env bash
cd ~/handover/h31; A=scripts/ask.sh
crontab -l | sed 's|^\*/5 .*gcal_sync_cron.sh|#&|' | crontab -
trap "crontab -l | sed 's|^#\(\*/5 .*gcal_sync_cron.sh\)|\1|' | crontab -; echo restored > cron1.restored" EXIT
$A coo loop31-coo-001 "I am watching Show One, season 5 episode 3, log it and give me a synopsis, and make an appointment to watch episode 4 at 4:00 am" coo >/dev/null
cp ~/loop1/workspaces/cos/state/calendar-journal.md cos-journal-after-001.txt
cp ~/loop1/workspaces/clo/state/lifestyle.md clo/lifestyle-after-001.txt
$A coo loop31-coo-002 "I finished Show Two season 1, please log where I stopped." coo >/dev/null
cp ~/loop1/workspaces/cos/state/calendar-journal.md cos-journal-after-002.txt
$A clo loop31-clo-003 "When does Show Two season 2 come back?" clo >/dev/null
$A coo loop31-coo-004 "Add a new show to my list: Show Three, planned." coo >/dev/null
$A coo loop31-coo-005 "Note that I dropped Show Two." coo >/dev/null
$A coo loop31-coo-006 "What shows am I following right now?" coo >/dev/null
$A coo loop31-coo-007 "What is my workout plan this week? Just tell me, do not change anything." coo >/dev/null
$A coo loop31-coo-008 "What is my weekly grocery budget right now? Just tell me, do not change anything." coo >/dev/null
echo done > batch1.done
