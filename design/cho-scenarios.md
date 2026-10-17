# CHO scenarios: how requests move between agents (approved design, APR-0051)

Status: approved for design (APR-0051). Nothing is built yet.
Purpose: show, step by step, who does what and when, for requests that touch health, sleep, gym, supplements, meals and the calendar.
Basis: approved rules APR-0007 (privacy), APR-0008 (direct CISO line), APR-0009 (COO dispatches), APR-0030 (CoS only writes calendar), APR-0032 (titles only in Google), APR-0044 (calendar adds from a chief go straight to CoS; deletes need CEO), APR-0045 (Slack exemption for private channels), APR-0046 (CSTO drafts instructions), APR-0048 (one channel per agent), APR-0050 (CEO sees real changes and failures).

## Rules every scenario follows
1. Every request from the CEO enters through the COO channel, or through the CHO channel when it is health-only. Both are posted in Slack.
2. The COO dispatches (APR-0009). The CHO may send calendar adds straight to CoS (APR-0044).
3. Any delete goes to the CEO for approval first (APR-0044). The step waits until the CEO answers.
4. Every real change and every failure is posted (APR-0050). Routine checks stay in the call log (APR-0047).
5. Health data is high privacy under the gate. A cloud model never sees it. Slack may hold it (APR-0045), but the gate still decides what each model call may see.
6. Retries: calendar writes retry every 5 minutes; after 5 failed attempts the COO is told and the CEO checks (S-06, APR-0043).

## Time terms used below
- "Now": within the same request.
- "Every 5 min": calendar retries (S-06).
- "Weekly": CMO dashboard and CISO leak scan (APR-0049).
- "Not defined": the sources do not say when this happens yet. Marked as a gap.

---

## C-01 - CEO asks to wake up earlier tomorrow
Request, in the COO channel: "I want to wake up earlier tomorrow because I have an important task. Align my calendar. Alarms should go off earlier. Some things may need to change."

Steps:
1. Now. COO reads the request and dispatches it to three places: CHO (sleep, gym, supplements), CoS (calendar), CIO (alarm device). It posts the dispatch in the COO channel, so the CEO sees it (APR-0050).
2. Now. CHO asks its Sleep Bot for a sleep window that fits the earlier wake time. The Sleep Bot returns a bedtime proposal. CHO posts the proposal in the CHO channel.
3. Now. CHO works out the knock-on changes. Example from the CEO: gym moves from 1pm to 2pm, and magnesium moves from 8pm to 9pm. CHO posts the list in the CHO channel.
4. Now. CHO sends the calendar changes straight to CoS (APR-0044). A move is two calendar actions: a delete of the 1pm gym entry and an add of the 2pm entry.
5. Now. CoS writes the add of the 2pm gym entry (titles only). CoS checks for a clash first; if there is one, it resolves it or asks the COO. CoS posts "gym entry added for 2pm" in the CHO channel and in its own channel.
6. Now. The delete of the 1pm gym entry waits. CoS posts the request for CEO approval in the COO channel (APR-0044). Nothing is deleted until the CEO answers.
7. Now. COO posts a notice to the CEO in the COO channel: the add is written; the delete waits for approval.
8. Now. CHO updates the supplement schedule: magnesium moves to 9pm. CHO records this in its own health log. A reminder entry, if wanted, goes to CoS as a calendar add.
9. Now. CIO owns alarm changes (APR-0051). It sets the alarm through a calendar-bot alarm, because that is the only alarm path configured today. Device alarms need the CIO's alarm skill, which does not exist yet. If the device alarm is wanted before then, CIO posts "device alarm not possible yet" in the CIO channel, and COO tells the CEO.
10. Every 5 min, if a calendar write fails, the retry rule applies (S-06). After 5 failures the COO is told and the CEO checks.

Pass criteria:
- The COO channel shows the dispatch, the add notice and the waiting delete, in that order.
- No delete runs before the CEO's yes.
- The 2pm gym entry exists, is titles only, and the 1pm entry is removed after the CEO's yes.
- The alarm gap is reported, not silently skipped.

Gaps:
- Alarm: the CIO needs a skill to set device alarms. Until it exists, only calendar-bot alarms can be set (APR-0051).
- Clash check: the rule for a clash is not written (S-08 is still in the catalogue as a design item).

---

## C-02 - CEO logs a therapy session (aromatherapy, sound, grounding, meditation)
Request, in the CHO channel: "Aromatherapy: lavender, 8:10am, 3 drops." Or later: "Sound therapy, 9pm, 20 min."

Steps:
1. Now. CHO parses the entry: type, product or method, time, duration or amount. If a field is missing, CHO asks once, in the CHO channel.
2. Now. CHO writes one record to the health log. Only CHO writes to this log (a single writer, the same pattern as APR-0030 for the calendar). Gap: where the log lives and its format are not defined.
3. Now. CHO posts "logged" in the CHO channel with the record it wrote. The CEO can correct it there.
4. Weekly. CMO reads the health log and includes the therapy totals in the dashboard, under Health (see C-05).
5. If a reminder is wanted, CHO sends a titles-only calendar add to CoS (APR-0044). The title shows the therapy name (APR-0051).

Pass criteria:
- Each log entry appears once, with the time given.
- A missing field is asked for, not guessed.
- The dashboard totals equal the sum of the log.

Gaps:
- Health log location, format and retention: not defined (APR-0013 approves append-only logs, but the format is not written).
- Owner: CHO owns the record. CSP proposes the practices that serve mental clarity (APR-0051).

---

## C-03 - CEO asks for next week's meal plan, anxiety aware
Request, in the CHO channel: "Full diet plan for next week. Anxiety aware. For example, breakfast: scrambled eggs, avocado, sardines, kefir."

Steps:
1. Now. CHO asks the questions it needs before drafting: foods to avoid, foods that trigger anxiety, caffeine limits, meal times, and whether a shopping list is wanted. It asks once, in one message.
2. Now. CHO spawns the Nutritionist (roster: CHO spawns Nutritionist; the template exists in agent-files/transient/nutritionist, still empty).
3. Now. Nutritionist drafts the week: breakfast, lunch, dinner, snacks, with the CEO's examples included. It runs on the local model, because the plan contains health detail and the gate blocks cloud for high privacy (APR-0007). Local model for now; changeable later (APR-0051).
4. Now. CHO checks the draft against the stated limits and posts it in the CHO channel, with a note of which limit each item respects.
5. The CEO replies with changes or "approved". Only then is the plan final.
6. After approval. If a grocery list is wanted, CHO asks CLO's Grocery Bot to build it from the plan. The list is not sent to any cloud model.
7. Not defined. Whether meal times become calendar entries. If yes, CHO sends titles-only adds to CoS (APR-0044).

Pass criteria:
- Nothing in the plan breaks a limit the CEO gave.
- The draft is produced by the local model (check the call log, APR-0047).
- No meal is marked final before the CEO's approval.

Gaps:
- Nutrition data: no food database or nutrient source is defined. The plan relies on the local model's knowledge until one exists.
- Clinical limits: CHO does not give medical advice. Any supplement dose change is shown to the CEO with a line that a doctor or pharmacist should confirm it (APR-0051).
- Local model quality: the local model is smaller than cloud models, so the draft may need more review rounds. Not measured yet.

---

## C-04 - Supplement timing change (magnesium 8pm to 9pm)
Trigger: C-01 step 8, or a direct request in the CHO channel.

Steps:
1. Now. CHO updates the supplement schedule in its health log. Timing only; the dose is not changed.
2. Now. CHO posts the change in the CHO channel.
3. If a reminder entry exists, CHO sends the calendar change to CoS (an add of the new time; the delete of the old entry needs the CEO's yes, APR-0044).
4. Dose change: CHO does not change a dose on its own. A dose change is shown to the CEO with a note that a doctor or pharmacist should confirm it first (APR-0051).

Pass criteria:
- The schedule shows 9pm; the dose is unchanged; the change is in the CHO channel.

---

## C-05 - Dashboard: Nutrition section under Health
Trigger: weekly dashboard (the CMO produces it, per the roster).

Steps:
1. Weekly. CMO collects the health log (therapies, C-02), the supplement schedule (C-04) and the meal plan (C-03).
2. Weekly. CMO builds the Nutrition section: planned meals, what was logged, supplement timing, and the therapy totals under Health.
3. Weekly. CMO posts the dashboard summary in its own channel. The CEO can open the full page later (P-17, dashboard access, is still open).
4. Weekly. CISO runs the leak scan over the dashboard data too (APR-0049).

Pass criteria:
- The Nutrition section shows only data CHO wrote; nothing is typed in by hand.
- The totals match the logs.

Gaps:
- Dashboard access and hosting: P-17, deferred.
- Dashboard design: deferred until the loop is proven (P-17).

---

## C-06 - Conflict: earlier wake-up and a late gym or late dinner
Trigger: C-01, when the Sleep Bot's bedtime clashes with a late gym session or a late dinner in the plan.

Steps:
1. Now. CHO sees the clash in its own proposal and does not hide it.
2. Now. CHO sends the clash to CoS, which resolves inter-department conflicts (roster: CoS).
3. If CoS cannot resolve it, the COO is told, and the COO gives the CEO the two options in the COO channel.
4. The CEO chooses. The choice is recorded and posted in the COO channel.

Pass criteria:
- No silent resolution: both options are shown.
- The CEO's choice is what gets written to the calendar.

---

## Decided (APR-0051)
1. Therapy owner: CHO. CSP proposes the practices.
2. Therapy reminders: the title shows the therapy name.
3. Alarms: CIO owns them; the CIO needs an alarm skill for device alarms.
4. Supplements: timing changes are free; dose changes need a doctor or pharmacist check.
5. Meal plans: local model for now.

## Not expanded yet
Lab results and blood work (Lab Analyst); sleep scoring; gym programming. Add these as C-07 onwards after P-25 is answered.
