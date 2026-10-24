# Approvals ledger

Only entries with `Status: approved` are binding. Quotes are the CEO's own answers from the
decision review (2026-10-10). Open items are in `decisions/PENDING.md`.
Each ADR cites these IDs. A change to an approved decision needs a new entry, not an edit.

## APR-0001 — Triage runs locally
Status: approved
Decided by: CEO
Your words: "triage is local, it has always been"
Applies to: ADR-0004; contracts/models/aliases.yaml (triage)

## APR-0002 — Cloud code model is GPT-6 Luna
Status: approved
Decided by: CEO
Your answer: "change to GPT-6 Luna"
Applies to: contracts/models/aliases.yaml (cloud-code)

## APR-0003 — Genesis model is Opus 5.5
Status: approved
Decided by: CEO
Your answer: "b" (move to claude-opus-5-5)
Applies to: contracts/models/aliases.yaml (genesis-brain, cloud-reasoning-high). Model ID still needs a probe (PENDING P-06).

## APR-0004 — Local model is a smaller model, about 12–14B
Status: approved
Decided by: CEO
Your answer: "a" (smaller local model, about 12–14B)
Applies to: contracts/models/aliases.yaml (local-primary). The exact model is not yet chosen (PENDING P-05).

## APR-0005 — Genesis inputs are a sanitized seed set you approve
Status: approved
Decided by: CEO
Your answer: "b"
Applies to: bootstrap/genesis-primer.md (when written); ADR-0017

## APR-0006 — Genesis Slack posts use a bounded, Genesis-only token
Status: approved
Decided by: CEO
Your answer: "b" (bounded Genesis-only scope)
Applies to: bootstrap/genesis-runbook.md (when written). The token is revoked when Genesis ends.

## APR-0007 — Privacy wins over critical complexity
Status: approved
Decided by: CEO
Your answer: "a" (privacy always wins; the CEO can override with explicit confirmation)
Applies to: contracts/policy/privacy.yaml; ADR-0003

## APR-0008 — CISO escalates P1 directly to the CEO
Status: approved
Decided by: CEO
Your answer: "a" (direct CISO to CEO)
Applies to: contracts/policy/escalation.yaml (when written); ADR-0007

## APR-0009 — The COO is the event dispatcher
Status: approved
Decided by: CEO
Your answer: "b" (COO)
Applies to: design/event-bus.md (when written); ADR-0008

## APR-0010 — Archive is local and encrypted until Phase 2; no AWS in the pilot
Status: approved
Decided by: CEO
Your answer: "b" (local encrypted archive until Phase 2)
Applies to: contracts/policy/archive.yaml (when written); ADR-0012

## APR-0011 — Archive uses S3 Object Lock (Compliance) with lifecycle to Glacier
Status: approved
Decided by: CEO
Your answer: "Object Lock Compliance with lifecycle to Glacier"
Applies to: contracts/policy/archive.yaml (when written); ADR-0012. Phase 2 only (see APR-0010).

## APR-0012 — One ADR per core decision
Status: approved
Decided by: CEO
Your answer: "one per core decision"
Applies to: decisions/adr/ (the ADR set)

## APR-0013 — Append-only logs plus state snapshots
Status: approved
Decided by: CEO
Your answer: "b" (state snapshots plus append-only logs)
Applies to: design/memory-and-data.md (when written); ADR-0011

## APR-0014 — Heartbeat files are renamed without spaces
Status: approved
Decided by: CEO
Your answer: "yes"
Applies to: agent-files/**/HEARTBEAT-*.md

## APR-0015 — Quiet hours use AST
Status: approved
Decided by: CEO
Your answer: "ast"
Applies to: ops/notification-strategy.md (when written)

## APR-0016 — Transient specialists are prompt templates
Status: approved
Decided by: CEO
Your answer: "prompt template"
Applies to: agent-files/transient/*/PROMPT.md; ADR-0010

## APR-0017 — CKO heartbeat is part of Phase 1
Status: approved
Decided by: CEO
Your answer: "yes from phase 1"
Applies to: agent-files/executive/cko/ (HEARTBEAT); design/agent-lifecycle.md

## APR-0018 — Cloud cheap model is gemini-3.8-flash-medium
Status: approved
Decided by: CEO
Your answer: "gemini-3.8-flash-medium" (the Claude Haiku 5.5 toggle is NOT approved; see PENDING P-01)
Applies to: contracts/models/aliases.yaml (cloud-cheap)

## APR-0019 — Local primary model is llama3.1:8b
Status: approved
Decided by: CEO
Your answer: "approve llama3.1:8b to be the local"
Evidence: research/spikes/SPK-06-local-model-on-vm.md (model ran on the VM, about 5.3 GB resident)
Supersedes: the size part of APR-0004 (12–14B). The new primary is 8B. APR-0004 is not edited.
Applies to: contracts/models/aliases.yaml (local-primary, triage)

## APR-0020 — Local backup model is Qwen 2.5 14B
Status: approved
Decided by: CEO
Your answer: "qwen2 as backup to it"
Applies to: contracts/models/aliases.yaml (local-backup)
Open: the exact tag must be confirmed (PENDING P-08).

## APR-0021 — Cloud-cheap can be switched by a provider field (Haiku 5.5 toggle)
Status: approved
Decided by: CEO
Your answer: "CEO: yes" to the proposal in P-01
Applies to: contracts/models/aliases.yaml (cloud-cheap, options list). Default stays gemini-3.8-flash-medium (APR-0018).

## APR-0022 — Minimum Genesis seed set
Status: approved
Decided by: CEO
Your answer: "CEO: yes" to the proposal in P-02: ceo-soul, ceo-identity, 2026-vision, constitution, genesis-interview-answers, health-baseline. Everything else is generated.
Applies to: bootstrap/genesis-primer.md, bootstrap/genesis-runbook.md (when written); APR-0005

## APR-0023 — ADRs required before Genesis
Status: approved
Decided by: CEO
Your answer: "CEO: yes" to the proposal in P-04: ADR-0003 (privacy), ADR-0004 (triage), ADR-0007 (CISO escalation), ADR-0016 (per-domain access). The rest follow after Genesis.
Applies to: decisions/adr/
## APR-0024 — Model IDs for Opus, GPT, and Gemini are correct
Status: approved
Decided by: CEO
Your answer: "CEO: yes, all correct" (P-06)
Applies to: aliases.yaml (genesis-brain, cloud-reasoning-high: claude-opus-5-5; cloud-code: GPT-6-Luna; cloud-cheap: gemini-3.8-flash-medium)
Note: no provider probe is recorded in research/spikes/ for these three yet. Only SPK-06 (local) has evidence.

## APR-0025 — Local backup model is qwen3.5:latest (digest 6488c96fa5fa)
Status: approved
Decided by: CEO
Your answer: installed models, "llama3.1:8b is ok", "these are my current local models i might change them later"
Evidence: `ollama list` output recorded in contracts/models/aliases.yaml
Supersedes: APR-0020 (the qwen2.5 14B tag). APR-0020 is not edited.
Applies to: contracts/models/aliases.yaml (local-backup)

## APR-0026 — gemma4:latest (digest c6eb396dbd59) is installed, not assigned to a route
Status: approved
Decided by: CEO
Your answer: installed; no role assigned yet
Applies to: nothing routed. It may be evaluated later under a new spike, and assigned only by a new APR entry.

## APR-0027 — Local model tags are pinned by digest in the aliases file
Status: approved
Decided by: CEO
Your answer: "i might change them later as I do upgrades"
Rule: a model change is a new APR entry plus an edit to aliases.yaml. Tags such as :latest move, so the digest is what the record uses.

## APR-0028 — CoS owns the combined calendar view
Status: approved
Decided by: CEO
Your answer: "the answer is CoS" (P-03, option a)
Meaning: CoS builds and holds the single combined calendar. It reads family events from CFA and personal events from CLO. It is the one place where conflicts across domains are checked.
Not decided here: which agent may WRITE a calendar entry (see P-10).
Applies to: design/ (calendar section, when written); agent-files/executive/cos/

## APR-0029 — The three draft ADRs are approved as decisions
Status: approved
Decided by: CEO
Your answer: "approve" (P-07)
Decisions:
  1. Per-domain access instead of universal symlinks (ADR-0016)
  2. OpenClaw is the initial runtime (ADR-0014)
  3. Repo, runtime, and seed are separate (ADR-0015)
Applies to: decisions/adr/ADR-0014, ADR-0015, ADR-0016 (the text is still to be written)

## APR-0030 — CoS is the only agent that writes calendar entries
Status: approved
Decided by: CEO
Your answer: "ok cos handles my calendar, approve" (P-10, option a)
Meaning: only CoS creates, changes, or deletes calendar entries. Other agents send CoS a request.
The COO is the front door: it receives your request, routes it, and relays the result. It does not write calendar entries.
Reason for the split: the COO holds conversation context and is already the single point of failure (see design/). Scheduling conflicts need the full picture, which belongs to CoS.
Applies to: decisions/adr/ (none directly); agent-files/executive/cos/ and agent-files/executive/coo/ (when written)

## APR-0031 — Google Calendar is the calendar store
Status: approved
Decided by: CEO
Your answer: "google calendar" (P-11)
Open consequence: calendar entries are personal data stored with a cloud provider. What may be stored there is a separate decision (PENDING P-12).
Applies to: design/ (calendar section, when written); contracts/channels.yaml or a calendar contract (when written)

## APR-0032 - Calendar content in Google: titles only for now
Status: approved
Decided by: CEO
Your answer: "P-12 should be titles only for now, i should be able to change this later ... i approve"
Meaning: Google Calendar stores event titles, start, and end. Details, locations, attendees, and health or family notes stay local. High-privacy events appear in Google as "busy" (option a of P-12).
Changeable: yes. A change is a new APR entry plus an edit to contracts/policy/calendar.yaml.
Applies to: contracts/policy/calendar.yaml; guides/calendar-gcalcli.md

## APR-0033 - ADR-0003 accepted (privacy gate enforced in code)
Status: approved
Decided by: CEO
Your answer: "I approve ADR-003 that you decided"
Applies to: decisions/adr/ADR-0003-privacy-gate-in-code.md (status changed to accepted)

## APR-0034 - Calendar event naming standard (mandate)
Status: approved
Decided by: CEO
Your words: "every calendar event has a prefix name and id ... CHO - Doctor Appointment - 10202026-0001 ... this is a mandate"
Format: <DOMAIN> - <Title> - <MMDDYYYY>-<NNNN>
Example: CHO - Doctor Appointment - 10202026-0001
Who assigns: CoS, the only writer of calendar entries (APR-0030). No other agent creates an event name.
Interpretation still to confirm: see P-15 (date order, ID scope, domain codes for non-domain events).
Changeable: yes. A change is a new APR entry plus an edit to contracts/policy/calendar.yaml.
Applies to: contracts/policy/calendar.yaml; guides/calendar-gcalcli.md

## APR-0035 - Calendar naming details (P-15)
Status: approved
Decided by: CEO
Your answer: "yes to your suggestions, so CSO and CFA for domain, approved" and "p-15 is a yes"
Meaning:
  1. Date order: MMDDYYYY (10202026 = October 20, 2026).
  2. ID scope: the four-digit counter restarts at 0001 for each date.
  3. Domain codes: CHO, CSP, CDO, CFO, CFA, CLO, CSO, CCO. Non-domain codes: COO and COS.
     The meaning of each domain code is in APR-0037.
Closes: P-15
Changeable: yes. A change is a new APR entry plus an edit to contracts/policy/calendar.yaml.
Applies to: contracts/policy/calendar.yaml; guides/calendar-gcalcli.md

## APR-0036 - Triage latency accepted for now (P-14, option a)
Status: approved
Decided by: CEO
Your answer: "for p-14 is a, let's accept the 20 seconds for now, as i dont have the machine available to test. so proceed as if this test is completed we will adjust later."
Meaning: triage may take about 20 seconds on the VM (SPK-06: 3.68 tokens per second). SPK-08 (smaller models) is not run for now.
Closes: P-14
Changeable: yes, when the machine is available to test. A change is a new APR entry.
Applies to: research/spikes/SPK-06-local-model-on-vm.md; contracts/models/aliases.yaml

## APR-0037 - Meaning of the domain codes (corrects how APR-0035 was read)
Status: approved
Decided by: CEO
Your words: "CFA is family domain, CFO is finance, csoc should not exists anywhere, CSO is social, I think i had it reverse when i answer before."
Meaning:
  CHO = Health, CSP = Spirituality, CDO = Development, CFO = Finance, CFA = Family,
  CLO = Lifestyle, CSO = Social, CCO = Career.
  COO = Operations and COS = Staff, for events that belong to no domain.
  Social is CSO. Family is CFA.
Changeable: yes. A change is a new APR entry plus an edit to contracts/policy/calendar.yaml.
Applies to: contracts/policy/calendar.yaml; guides/calendar-gcalcli.md

## APR-0038 - Agent roster approved (design/roster.md)
Status: approved
Decided by: CEO
Your answer: "i approved sovereign_life_os_roster.md yes."
Meaning: the approved roster is design/roster.md, a hand-written source. Roster codes: CFA is Family, CSO is Social (APR-0037).
Applies to: design/roster.md; design/README.md; contracts/agents.yaml (generated from the roster)
Note: how agents.yaml is produced is approved in APR-0039.
Changeable: yes. A change is a new APR entry plus an edit to design/roster.md.

## APR-0039 - agents.yaml is generated from the roster (P-16)
Status: approved
Decided by: CEO
Your answer: "approve for p-16"
Meaning: design/roster.md is the only hand-written roster. contracts/agents.yaml is generated from it by scripts/verify/roster_to_agents.py. Nobody edits agents.yaml by hand. The validator (BLOCKING 13) fails if agents.yaml does not match the roster.
To add an agent: add its row to design/roster.md, run the script, add its folder under agent-files/, and record an APR entry.
Closes: P-16
Changeable: yes. A change is a new APR entry plus an edit to this rule.
Applies to: design/roster.md; contracts/agents.yaml; scripts/verify/roster_to_agents.py; scripts/verify/validate_repo.py

## APR-0040 - Model ID claude-haiku-5-5 confirmed (P-08)
Status: approved
Decided by: CEO
Your answer: "P-08 > yes" (after SPK-09: HTTP 200 from the API, and the CLI works with the model)
Meaning: the model ID claude-haiku-5-5 is confirmed as usable. Switching the active model is still APR-0021.
Closes: P-08
Changeable: yes. A change is a new APR entry.
Applies to: research/spikes/SPK-09-haiku-model-probe.md; contracts/models/aliases.yaml

## APR-0041 - Calendar token location confirmed (P-13)
Status: approved
Decided by: CEO
Your answer: "yes"
Meaning: the Google Calendar OAuth token lives on the VM only, at ~/.local/share/gcalcli/oauth, owner ubuntu, mode 600. It is never in the repo or in chat. Copying it to another machine needs a new APR entry.
Evidence: VM check on 2026-10-16. Mode was 664 and was changed to 600 (chmod), confirmed by stat.
Closes: P-13
Changeable: yes. A change is a new APR entry.
Applies to: guides/calendar-gcalcli.md ("Where the token lives"); ops/install-log.md

## APR-0042 - ADR-0002 approved: dual authority (P-18)
Status: approved
Decided by: CEO
Your answer: "Approved"
Meaning: ADR-0002 is accepted as written, including the tie-break. Operational authority is the COO; constitutional authority is the CSTO; neither outranks the other. When the CSTO vetoes a COO plan, nothing runs until the CEO decides.
Closes: P-18
Changeable: yes. A change is a new APR entry.
Applies to: decisions/adr/ADR-0002-dual-authority-model.md

## APR-0043 - Scenario catalogue approved, with changes to S-06 and S-07 (P-19)
Status: approved
Decided by: CEO
Your answer: "yes" to the proposed defaults, with changes to S-06 and S-07
Meaning: design/scenarios.md is approved.
- S-06 (calendar unreachable): the event is kept local and not written to Google. It is retried every 5 minutes until it completes. After 5 failed attempts the problem goes to the COO, who has the CEO check it. Retries continue after that until it completes.
- S-07 (Google token revoked): this is an alert that must be fixed. The CIO reports it in its Slack channel.
- The CIO's Slack channel is also the notice channel for S-01, S-14 and S-20. This was applied from the S-07 answer and is recorded here for CEO confirmation or change.
Closes: P-19
Changeable: yes. A change is a new APR entry.
Applies to: design/scenarios.md

## APR-0044 - Calendar adds and deletes: routing (refines APR-0030)
Status: approved
Decided by: CEO
Your answer: "CHO decides, goes straight to CoS to execute. No approval from me except for deletes. COO notifies me on each add."
Meaning: a chief's calendar add goes directly to the CoS for execution. The CoS stays the only writer (APR-0030). The COO notifies the CEO when an add is written. Every delete needs the CEO's approval first.
Closes: none
Changeable: yes. A change is a new APR entry.
Applies to: decisions/APPROVALS.md APR-0030 (unchanged); design/routing-and-privacy.md (when written); P-20

## APR-0045 - Slack exemption from the privacy rule until an in-house app exists
Status: approved
Decided by: CEO
Your answer: "We are going to need an exemption for Slack until we develop our own in-house app. Slack is the communication channel, so it is OK to have private data there. The Slack channels are fully private, even though the service is cloud."
Meaning: private data may be posted in private Slack channels until the in-house app exists. This covers posting to Slack only. It does not allow sending that data to a cloud model: the privacy gate still applies (APR-0007).
Closes: none
Changeable: yes. A change is a new APR entry.
Applies to: contracts/policy/privacy.yaml (channels block); P-22

## APR-0046 - Agent instructions are written by the CSTO from approved rules (P-20)
Status: approved
Decided by: CEO
Your answer: "P-20 yes"
Meaning: Aurelius (CSTO) turns approved rules into one instruction draft per chief. Limits: it writes only from approved APR entries and adds no new rules; each rule cites its APR number; each draft is approved by the CEO before use; the CISO checks the tool permissions in each draft. A script generates the rules index from APPROVALS.md first.
Closes: P-20
Changeable: yes. A change is a new APR entry.
Applies to: design/agent-lifecycle.md (when written); agent-files/ (drafts after approval)

## APR-0047 - LLM call log approved, with a CISO leak check added (P-21)
Status: approved
Decided by: CEO
Your answer: "P-21 yes, but also need to flag where the CISO looks for possible sensitive data leaks and reports"
Meaning: the LLM call log design in P-21 is approved for building later (exact request and response per call, local and cloud, outside git). Added requirement: the CISO checks the log for possible sensitive-data leaks and reports them. What is scanned, how often, and who receives the report is set out in P-24.
Closes: P-21 (design approved; build later)
Changeable: yes. A change is a new APR entry.
Applies to: design/observability-and-cost.md (when written); P-24

## APR-0048 - Slack model: one app, display name per message, one channel per agent (P-22)
Status: approved
Decided by: CEO
Your answer: "P-22 yes. Slack shows display name. Each agent will have its own Slack channel."
Meaning: one Slack app, with each message shown under the agent's display name. Each agent has its own channel. The COO channel holds only the CEO and the COO. The privacy exemption in APR-0045 applies to these channels.
Closes: P-22
Changeable: yes. A change is a new APR entry.
Applies to: contracts/policy/privacy.yaml (channels block); P-23

## APR-0049 - CISO sensitive-data leak check: scope, schedule, recipient (P-24)
Status: approved
Decided by: CEO
Your answer: "1. scan all. 2. schedule weekly. 3. yes, report to me directly."
Meaning:
- Scope: the CISO scans all sources: the LLM call log (P-21), Slack posts, and calendar entries.
- Schedule: once a week.
- Recipient: the CISO reports possible sensitive-data leaks directly to the CEO.
Closes: P-24
Changeable: yes. A change is a new APR entry.
Applies to: design/security-and-network.md (when written); P-21 (APR-0047); APR-0008 (direct CISO line)

## APR-0050 - What the CEO sees of agent-to-agent communication (P-23)
Status: approved
Decided by: CEO
Your answer: "p23 yes"
Meaning: the CEO sees every cross-agent message that changes something real (calendar add, budget change, delete), posted in the sender's and the receiver's channel. Replies go back to the requester's channel. Every failure, escalation and retry limit goes to the COO channel. Routine reads, status checks and retries under the limit are not posted; they stay in the LLM call log (APR-0047), which the CEO can open at any time.
Closes: P-23
Changeable: yes. A change is a new APR entry.
Applies to: APR-0044 (calendar announcements), APR-0048 (Slack channels), APR-0047 (call log)

## APR-0051 - CHO communication scenarios: P-25 answers (therapy owner, alarms, supplements, meal model)
Status: approved
Decided by: CEO
Your answer: "CSP proposes, CHO owns. 1: CHO. 2: CHO. 3: therapy name is ok. 4: CIO, he will need the skill to set up alarms; we only configure calendar bot alarms. 5: yes. 6: local model for now, we can change this later."
Meaning:
- Therapy owner: CSP proposes the practices that serve mental clarity. CHO owns them: the therapy log, the records, and any health-related safety.
- Therapy calendar entries show the therapy name in the title (titles only, APR-0032).
- Alarms: the CIO owns alarm changes. The CIO needs a skill that sets device alarms. Until that skill exists, the only alarms that can be set are calendar-bot alarms.
- Supplements: CHO may change timing freely. A dose change needs a doctor or pharmacist check first (C-04).
- Meal plans: the local model drafts them for now. This can be changed later by a new APR entry.
Closes: P-25
Changeable: yes. A change is a new APR entry.
Applies to: design/cho-scenarios.md (C-01 to C-06); roster (CIO alarm role); P-25 closed

## APR-0052 - Loop 1 runs cloud-only on synthetic data (time-boxed exception)
Status: approved
Decided by: CEO
Your answer: "1. yes" (to the Loop 1 exception record proposed on 2026-10-22)
Meaning:
- Scope: Loop 1 only. Four agents: COO, CHO, CoS, CFO.
- Model: every agent uses openai/gpt-6-luna through OpenClaw's OpenAI provider, as both the default and the utility model.
- Data: synthetic only. No file from lifeos-seed/ is copied, mounted or rendered onto the Loop 1 host. No real personal data is typed into Loop 1 Slack channels.
- Suspended for Loop 1 only: APR-0018 and APR-0021 (cheap cloud model), APR-0051 (meal drafts on the local model), APR-0031 (Google Calendar, see APR-0054), APR-0047 and APR-0049 (CISO leak scan; the CEO checks by hand instead), and the router path of ADR-0003 and ADR-0004 (router, privacy gate and CLI adapters are not used).
- Not changed: contracts/models/aliases.yaml. The triage alias stays local (APR-0001).
- Expiry: when Loop 1 closes or on 2026-11-15, whichever comes first. After expiry the suspended entries apply again, unless a new APR entry changes them.
Changeable: yes. A change is a new APR entry.
Applies to: decisions/adr/ADR-0018-loop-1-cloud-only-exception.md; the Loop 1 OpenClaw config

## APR-0053 - Loop 1 Slack: one app, each agent posts under its own name (must be proven)
Status: approved
Decided by: CEO
Your answer: "you are recommending 1 app on slack and each agent post with their identity? we need to prove that can be achieved otherwise we will need different apps in slack."
Meaning:
- Loop 1 aims at APR-0048: one Slack app; each agent posts under its own display name and icon, in its own channel. Only the COO accepts requests from the CEO.
- This is proven by a test before Loop 1 (SPK-10, P-27). OpenClaw's Slack docs say the chat:write.customize scope lets outgoing messages use the active agent's name and icon.
- If the test fails, each Loop 1 agent gets its own Slack app (the shape SPK-04 proved), and APR-0048 is changed by a new APR entry.
Changeable: yes. A change is a new APR entry.
Applies to: research/spikes/SPK-10-slack-one-app-display-names.md; Slack app setup for Loop 1

## APR-0054 - Loop 1 calendar is a local journal kept by the CoS
Status: approved
Decided by: CEO
Your answer: "3. yes to your recommendation"
Meaning:
- Loop 1 makes no Google Calendar writes. The CoS keeps a calendar journal file in its own runtime workspace (never in the repo) and is its only writer (APR-0030).
- Each entry is named per APR-0034 and APR-0035 and carries a status.
- Google Calendar (APR-0031) is added in Loop 2. How the journal works with Google (retries, holds, duplicate checks) is open as P-28.
Changeable: yes. A change is a new APR entry.
Applies to: Loop 1 CoS instructions; tests/scenario/bad-sleep-reschedule.md

## APR-0055 - Loop 1 agent instructions: drafted by the AI in the CSTO role, approved as one set
Status: approved
Decided by: CEO
Your answer: "4. yes"
Meaning:
- For the four Loop 1 agents, the AI writes the instruction files in the CSTO role: only from approved APR entries, no new rules, and each rule cites its APR number (as APR-0046 requires).
- The CEO approves the four sets once, together, before first use.
- The tool check that APR-0046 gives to the CISO is done by the AI with the health check, because no CISO agent runs in Loop 1.
Changeable: yes. A change is a new APR entry.
Applies to: agent-files for COO, CHO, CoS and CFO (Loop 1 only)

## APR-0056 - Loop 1 cost limits
Status: approved
Decided by: CEO
Your answer: "5. yes"
Meaning:
- Each scenario run has a ceiling of 0.05 USD. A run that reaches it stops and is recorded as a failure.
- Provider alert at 1 USD per day; monthly limit of 5 USD for the life-os project.
Changeable: yes. A change is a new APR entry.
Applies to: OpenAI project settings; the health check; tests/scenario/bad-sleep-reschedule.md

## APR-0057 - A calendar move is not a delete (refines APR-0044)
Status: approved
Decided by: CEO
Your answer: "for step 2. I approve your (a) Recommended"
Meaning:
- A move asked for by the CEO, or by the chief that owns the entry, is not a delete. It needs no CEO approval.
- The old entry stays in the record and is marked moved. The new entry is written under its own name (APR-0034).
- Removing an entry with no replacement is a delete and still needs the CEO's approval first (APR-0044).
Changeable: yes. A change is a new APR entry.
Applies to: CoS and CHO instructions; the calendar journal (APR-0054); Google Calendar writes in Loop 2

## APR-0058 - Loop 1 instruction set v1.1 and v1.2 (amends the set approved under APR-0055)
Status: approved
Decided by: CEO
Your answer: "i approved: Proposed fix (instruction set v1.1, needs your approval under APR-0055)." and "appproved step 3 also"
Meaning:
- v1.1, all four agents: whoever starts a change and was given no event ID creates one: <run ID>-<agent id>-<NN>, counting from 01 within the run. An event ID is never reused.
- v1.2, all four agents: the move rule of APR-0057.
- v1.2, CoS: a journal line is never edited or removed. A move appends the old entry again with status moved, then the new entry with status written. Both carry the run ID and event ID.
- v1.2, COO: the summary to the CEO names every agent that changed something, taken from their replies (APR-0050).
- The source of the set is deploy/loop1/loop1-agent-files.sh. The VM workspaces must match it.
Changeable: yes. A change is a new APR entry.
Applies to: deploy/loop1/loop1-agent-files.sh; Loop 1 agent workspaces

## APR-0059 - Agent sessions reset daily at 04:00 AST
Status: approved
Decided by: CEO
Your answer: "yes to: agent’s session reset daily at 04:00 AST"
Meaning:
- OpenClaw config session.reset is mode daily, atHour 4. The hour is the gateway host's local time; the VM runs on AST (America/Santo_Domingo).
- Each agent starts a fresh conversation every day at 04:00. Agent state lives in the state files, not in chat history, so nothing that matters is lost.
- Reason: with no reset, cross-agent messages pile up in each agent's main session (the CoS main session reached 57k tokens on 2026-10-22). That raises the cost of every turn and lets old runs steer new ones.
- Between scenario runs the main sessions are also cut to one line with openclaw sessions compact (synthetic data only; see guides/loop1-baseline.md section 7).
Changeable: yes. A change is a new APR entry.
Applies to: OpenClaw config (session.reset); Loop 1 scenario procedure

## APR-0060 - Loop 1 model runtime pinned to OpenClaw (closes P-30)
Status: approved
Decided by: CEO
Your answer: "1. yes, wonder if that's going to be a problem for our life-os system"
Meaning:
- For openai/gpt-6-luna the runtime is set to openclaw: agents.defaults.models["openai/gpt-6-luna"].agentRuntime.id = "openclaw".
- Without it, OpenClaw chose the codex harness on its own ("implicit") partway through the 2026-10-22 tests. Same model and billing, but a harness that can change under a test breaks repeatability.
- No conflict with the life-os design: the "codex" in contracts/models/aliases.yaml is the Codex CLI adapter (SPK-05, bypassed in Loop 1 by ADR-0018), not this runtime.
Changeable: yes. A change is a new APR entry.
Applies to: OpenClaw config on the Loop 1 VM; deploy/loop1/health-check.py

## APR-0061 - Memory search and dreaming off for Loop 1
Status: approved
Decided by: CEO
Your answer: "2. yes"
Meaning:
- memory.search.enabled is false and plugins.entries.memory-core.config.dreaming.enabled is false.
- Memory search sends agent text to OpenAI for embeddings (115 requests on 2026-10-23), a cloud path outside the privacy gate (ADR-0003). Dreaming is a nightly model sweep that rewrites agent memory, which conflicts with append-only history (ADR-0011).
- Loop 1 agents keep their state in state files, so neither feature is needed.
- What memory LifeOS should have is open as P-32.
Changeable: yes. A change is a new APR entry.
Applies to: OpenClaw config on the Loop 1 VM; deploy/loop1/health-check.py

## APR-0062 - Loop 1 Slack: one app per agent (changes APR-0048)
Status: approved
Decided by: CEO
Your answer: "ok, (a) is approved, proceed"
Meaning:
- Each Loop 1 agent (COO, CHO, CoS, CFO) has its own Slack app, bot token and channel. This is the fallback written into APR-0053; it replaces the one-app part of APR-0048.
- Why: with one app, only replies to a routed message showed the agent's name and icon. A post an agent made with its message tool after a handoff showed the app name (SPK-10, first run).
- Each agent still has its own channel (APR-0048, unchanged).
- The tokens stay in ~/loop1/slack.env on the VM and never in the repo.
Closes: P-27
Changeable: yes. A change is a new APR entry.
Applies to: research/spikes/SPK-10-slack-one-app-display-names.md; guides/loop1-baseline.md section 7.8; Slack setup for Loop 1

## APR-0063 - Any agent can be addressed; the COO is the normal door (closes P-33)
Status: approved
Decided by: CEO
Your answer: "I was expecting that I can order any agent at any time. but mostly i will only talk to coo and he will handle the rest of the communication."
Meaning:
- The CEO may message any agent in its own channel at any time (option a of P-33). Normally the CEO talks to the COO, who routes to the chiefs and relays the result.
- The Loop 1 channel allowlists keep the CEO's mentions allowed in all four agent channels.
- APR-0048 is otherwise unchanged: each agent has its own channel and the COO channel holds only the CEO and the COO.
- How much context the COO builds up when it routes everything is a design question, kept open in P-32.
Closes: P-33
Changeable: yes. A change is a new APR entry.
Applies to: Slack channel allowlists; P-32

## APR-0064 - Loop 1 instruction set v1.3 (Slack-driven runs)
Status: approved
Decided by: CEO
Your answer: "v1.3 approved"
Meaning:
- COO: after sessions_send, wait with timeoutSeconds 240 and treat the reply as the result; do not ask other agents to confirm and do not read their sessions. Answer the CEO once, as the final answer, and never post with the message tool in the channel it answers in. A reply that arrives after the answer gets one line starting "Late reply:". Every FAILURE message goes into the answer to the CEO.
- CHO, CoS and CFO: after a real change, or after sending a request that asks for one, post one line in their own Slack channel with the message tool (who did what, event ID), once per event ID. Failures go to the COO as a sessions_send message starting FAILURE, not posted by the agent. (APR-0050)
- Why: loop1-scn-007 (first run from Slack) gave a premature "blocked" answer, a late report that woke the COO twice, two duplicate summaries and two incomplete-turn errors, and nothing in the CHO and CoS channels.
- The lines are appended by deploy/loop1/loop1-v13-upgrade.sh. The channel IDs are read from ~/loop1/slack-channels.env on the VM and are not stored in the repo.
Changeable: yes. A change is a new APR entry.
Applies to: deploy/loop1/loop1-v13-upgrade.sh; the four AGENTS.md files on the VM; tests/scenario/bad-sleep-reschedule.md
