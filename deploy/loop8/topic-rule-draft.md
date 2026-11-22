# Loop 8, step 2: the topic rule for the CHO, CFO and CLO (DRAFT, waiting for the CEO's approval; nothing is approved here)

Why: today each chief's instructions are written around the first thing it tracked (the CLO: "starting with the TV shows"; the CHO: one health-plan file; the CFO: a budget file and an investments file). A new topic (your dogs, orders, a trip, nutrition) then looks like a design job. The model already knows how to keep a log, and the CLO already set up its own vehicle files without a handover (rows 5 and 6 of the request log). This rule makes that the standing behaviour, written once, the same in the three chiefs that keep personal logs. The COO routes and the CoS owns the calendar, so they do not get it.

## The rule (the same wording in the CHO, CFO and CLO; each adds it as one new rule and keeps all others)
"- New topics (instruction set <version>): when the CEO asks you to start tracking something that belongs to your own domain and you have no file for it, do not refuse and do not wait for a setup. First read your topic index, state/topics.md. If the topic is already listed, use its file. If it is not, propose a simple log in two short lines: the file name (state/<topic>.md, lowercase words joined by hyphens) and the columns (date, what, one or two fields that fit the topic, run ID, event ID), with one example line built from what he just told you. Ask him once to confirm or change it. After he says yes, create the file with a header line, append the first entry, and append one line to state/topics.md (topic, file, columns, date). Append only: never edit an old line; a correction is a new line that says which line it corrects. Every entry carries the run ID and event ID as in your other rules, and the usual one-line post in your own channel. Do not create a calendar entry unless he asks for one. Answer questions about a topic from its file only. If he asks what you track, read state/topics.md and list the topics. Never ask for or write passwords, account numbers or login details. If the topic belongs to another chief's domain, say which chief holds that domain and write nothing."

## Where it goes and the version
- CHO: a new last rule under "Loop 1 rules (all agents)"; instruction set v1.9 becomes v1.10.
- CFO: a new last rule under "Loop 1 rules (all agents)"; v1.11 becomes v1.12.
- CLO: a new last rule under "Rules"; v1.1 becomes v1.2. One narrow line is also widened in place: the first Role line, "starting with the TV shows he follows", becomes "such as the TV shows he follows, travel, hobbies, home projects and vehicle maintenance" (the lifestyle scope already in design/roster.md). The existing show and vehicle files stay as they are.
- The domain split does not change: nutrition stays with the CHO (a diet or meal plan change still goes to the COO and on to the CFO for the grocery budget line, as today). Pets, trips, hobbies, home and e-commerce orders are lifestyle (CLO) unless you tell us a different owner when you ask; if you want orders under the CFO, that is a one-line change we make when the first order arrives.

## What changes on the VM if approved (a numbered handover, scratch first)
1. The three instruction files above (gateway stopped, backup, commit in each workspace git, gateway started; one restart).
2. state/topics.md in each of the three workspaces, seeded with the file names that exist today (budget, investments, health-plan, lifestyle, the vehicle files) and nothing else. The handover never reads or copies their content.
3. The health check: version lines for the three chiefs, and one line that counts topic files in each state folder against the lines in state/topics.md (WARN if a file has no index line). Nothing else.
4. No config, no crontab, no plugin, no change to the COO, the CoS, routing, the delete gate or the send log.

## How it is proved
- Scratch gateway first, synthetic topics only: in each chief, a test topic ("houseplants" for the CLO and CFO-style test, "water intake" for the CHO). Checks: the chief proposes columns and waits for a yes; after the yes, the file exists with a header, the first entry has run ID and event ID, state/topics.md gained one line, no calendar entry was made, no old line changed; a second entry appends; "what do you track" lists the topics; a topic from another chief's domain is declined with the chief named; a request with an account number is refused.
- Live, synthetic only, same checks on one topic per chief, then the real ones: you ask for nutrition, dogs and so on in Slack and I score them in the request log. Existing real entries are never read, copied or changed by the tests.

## What it does not do
It does not make the chiefs reliable by itself: it is a behaviour rule, like the others, so the request log is the check. It adds no code, so a chief can still ignore it; the health line catches an unindexed file but not a wrong column. Health data in a nutrition topic is real health data while the privacy gate is still only watching (the definition of done lists the gate as a precondition for health data at scale; you decide when to start nutrition).

## Question
Reply "approved as written", or tell me the changes (for example the CLO scope line, or who owns orders). Approval would be recorded as the next APR in your words, with a numbered handover to follow.
