# Loop 7: the COO routes lifestyle requests to the CLO, and the CLO's requests work (APPROVED by the CEO, APR-0128, "approved as written")


## A. COO: instruction set v1.10.8 (agent-files/executive/coo/AGENTS.md)

Change "You may send to" from `CHO, CoS, CFO. (ADR-0018)` to:

    CHO, CoS, CFO, CLO. (ADR-0018)

Add one row to the "Who needs to know" table:

    | CEO request about TV shows or other lifestyle items | CLO |

Add one rule at the end of "Loop 1 rules (all agents)":

    - Lifestyle requests (APR-0128, instruction set v1.10.8): a request about TV shows or other lifestyle items goes to the CLO, never to the CHO. Call sessions_send with sessionKey agent:clo:main and put the whole task in the message: what to log, the dates and times, the run ID, and, if the CEO asked for an appointment, say so. Tell the CEO only what the CLO's reply confirms and name the CLO as the one who confirmed it. Never invent the CHO or any other agent for a lifestyle request.

## B. CLO: instruction set v1.1 (agent-files/department/clo/AGENTS.md)

Replace the line under "You may send to":

    - Ask the CoS for a calendar entry only when the CEO asks for one (for example a premiere night).

with:

    - Ask the CoS for a calendar entry only when the CEO asks for one (for example a premiere night, or "make an appointment to watch episode 4").
    - Handoff call (APR-0128, instruction set v1.1): call sessions_send with exactly these fields: sessionKey agent:cos:main, message (the whole task: what to do, dates and times, run ID, your own event ID, normal privacy unless the CEO said private), mode followup, timeoutSeconds 120. Your event IDs are <run ID>-clo-01, -clo-02 and so on. Never set watch. Never use mode notify or resume. Do not look up the tool's API files or list sessions first. The returned reply is the result. If a call fails or returns queued, resend the same message once with the same fields.

Add to "Rules":

    - If the CEO asks for something you cannot look up (for example when a show returns), say so in one sentence and ask him for the date. Record it only when he gives it.
    - You may give a short synopsis of an episode from what you already know, and you must say it is from memory and may be wrong. (APR-0128)

## C. What else the install needs (handover 31)
- Config: the COO's allowed-send list gets "clo" (one key, shown as a diff, backup first), and whatever the other side needs for the COO to reach agent:clo:main (checked in scratch first). The COO's instruction file, health-check expectations, parity lines and the version marker change to v1.10.8 and CLO v1.1.
- Tests with new run IDs, synthetic data: your exact sentence from tonight ("I'm watching Show One season 5 episode 3 on Netflix, log it, and give me a synopsis, and make an appointment to watch episode 4 at 4:00 am") must now go COO to CLO, the CLO logs it, answers with the synopsis marked "from memory", and the CLO's calendar request must reach the CoS and be written (the test calendar line is removed afterwards, cron paused as before); a CHO request (workout) still goes to the CHO; a CFO request still goes to the CFO; the COO never names the CHO for a lifestyle request.
- No change to the CHO, CoS or CFO files, the crontab or the plugins.

## Answers (APR-0128)
The CEO approved the wording as written. The synopsis default stands: the CLO may give a short synopsis from memory, marked as possibly wrong.

## Questions that were asked
1. Synopsis: the CLO may give one "from memory, may be wrong" (default as above), or never?
2. Anything to change in the wording? Reply "approved as written" or tell me the changes.
