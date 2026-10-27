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

## APR-0065 - Loop 1 instruction set v1.4 (wait for the result; answer once)
Status: approved
Decided by: CEO
Your answer: "v1.4 approved."
Meaning:
- CHO: when it asks another agent for a change, it waits (timeoutSeconds 120) and treats the reply as the result. It reports done only from that reply. If the wait ends with no reply, it reports "no reply from <agent>" and sends the COO a FAILURE message.
- CHO, CoS and CFO: when another agent's message asks them to do something, their answer to that message is their report. They do not also send a separate sessions_send message about it to that agent or to the COO. Failures still go to the COO as FAILURE messages (v1.3).
- This changes one rule of instruction set v1 (wording of APR-0044 and APR-0050): the CoS no longer sends the COO a second message after a calendar add. The requester's report carries the result to the COO, and the CEO still sees the CoS's own-channel line (APR-0050).
- Why: loop1-scn-010 (Slack run). The CHO reported "pending" while the CoS had already written the move, the COO told the CEO "pending" and named only the CHO, and the CoS's confirmation to the CHO failed twice (SESSION_WORK_START_CHANGED).
- The lines are appended by deploy/loop1/loop1-v14-upgrade.sh (AGENTS.md only; skips agents already on v1.4).
Changeable: yes. A change is a new APR entry.
Applies to: deploy/loop1/loop1-v14-upgrade.sh; the CHO, CoS and CFO AGENTS.md files on the VM; tests/scenario/bad-sleep-reschedule.md

## APR-0066 - Loop 1 instruction set v1.5: the COO carries the whole task in its handoff (closes P-34)
Status: approved
Decided by: CEO
Your answer: "v1.5 is approved"
Meaning:
- The COO puts the whole task in the sessions_send body in plain words (what to do, the dates and times, the run ID). It never tells an agent to find the task in its own history or queue.
- If an agent replies that it cannot find the task details, the COO resends once with the full details inline and treats that reply as the result. It reports the retry to the CEO only if the resend also fails.
- Why: in loop1-scn-011 and loop1-scn-013 the CHO found no task details on the COO's first routed message (011 wrote nothing; 013 needed a resend and showed the CEO a FAILURE note).
- The line is appended by deploy/loop1/loop1-v15-upgrade.sh (COO AGENTS.md only). Its text cites P-34, the proposal this entry closes.
Closes: P-34
Changeable: yes. A change is a new APR entry.
Applies to: deploy/loop1/loop1-v15-upgrade.sh; the COO AGENTS.md file on the VM; tests/scenario/bad-sleep-reschedule.md

## APR-0067 - Loop 1 instruction set v1.6: the CoS reports an acknowledgement error as delivered, not as FAILURE (P-35 stays open)
Status: approved
Decided by: CEO
Your answer: "Keep P-35 open and change the CoS's wording."
Meaning:
- When the CoS sends a message to a waiting agent and the acknowledgement fails (a session-start error or SESSION_WORK_START_CHANGED), it does not report FAILURE to the COO. It reports "delivered; acknowledgement error (P-35)" and says whether the receiving agent has replied with the content.
- The CoS does not resend in that case, to avoid duplicates. FAILURE is for a message that was not sent, or where the receiving agent says it did not get the content.
- This changes the wording only. It does not fix the cause. P-35 stays open.
- Applied by deploy/loop1/loop1-v16-upgrade.sh (CoS AGENTS.md only).
Closes: none
Changeable: yes. A change is a new APR entry.
Applies to: deploy/loop1/loop1-v16-upgrade.sh; the CoS AGENTS.md file on the VM.

## APR-0068 - P-35 closed: SESSION_WORK_START_CHANGED is a retryable timing race
Status: approved
Decided by: CEO
Your answer: "close p-35 and proceed"
Meaning:
- The error comes from OpenClaw's session ingress (dist/work-start-error and dist/ingress-drain): a message that reaches a session while that session is starting work fails with "Session ... changed while starting work. Retry." and is retried. It is dropped only at the retry limit, logged as session-start-conflict-retry-limit.
- The gateway logs for 2026-10-24 and 2026-10-25 have no such drop. In every run from 010 to 019, the CHO received the CoS's content.
- The CoS sees the first failed attempt and reports it. Instruction set v1.6 (APR-0067) already reports it as "delivered; acknowledgement error", not FAILURE. No further change.
- Reopen if a session-start-conflict-retry-limit line appears, or if an agent does not receive a reply's content.
Closes: P-35
Changeable: yes. A change is a new APR entry.
Applies to: decisions/PENDING.md; the CoS AGENTS.md (v1.6, unchanged).

## APR-0069 - Scenario bad-sleep-reschedule closed for Loop 1
Status: approved
Decided by: CEO
Your answer: "Proposal A: is approved let's close it. Claude will review the logs to have the final decision" (to the VM agent, 2026-10-25), then "proceed" after Claude's log review.
Meaning:
- The scenario is closed on pass criteria 1 to 5. Clean Slack pass: loop1-scn-019 under instruction set v1.6 (one run per agent; the COO named the CHO and the CoS; numstat 2 0; no late reply, no FAILURE note). CLI passes: runs 003 to 006.
- Criterion 6 (under 0.05 USD per run) was not measured from 2026-10-24 on; deferred by the CEO. Measured earlier: about 0.047 USD (run 007), at most about 0.020 USD (run 010).
- Claude's log review covered runs 015 to 019 against the CoS journal diff, the CHO health plan, the three Slack channels and the gateway log.
- This closes the scenario, not Loop 1. Closing Loop 1 ends the APR-0052 exception and needs its own CEO sign-off.
Changeable: yes. A change is a new APR entry.
Applies to: tests/scenario/bad-sleep-reschedule.md; deploy/loop1/LOOP1-CLOSE-RECORD.md

## APR-0070 - SPK-03 deferred
Status: approved
Decided by: CEO
Your answer: "proposal C: lets defer I dont not expect to do any docker isolation for a while." (to the VM agent, 2026-10-25)
Meaning:
- SPK-03 stays partial. Loop 1 checks passed (file canary, shell refusal, transcript refusal with a cloud model). JavaScript Code Mode and the Docker sandbox were not tested and are not scheduled.
Changeable: yes. A change is a new APR entry.
Applies to: research/spikes/SPK-03-workspace-isolation.md

## APR-0071 - Loop 1 closed; the cloud-only exception ends
Status: approved
Decided by: CEO
Your answer: "close loop 1"
Meaning:
- Loop 1 is closed on 2026-10-25. The close record is deploy/loop1/LOOP1-CLOSE-RECORD.md.
- APR-0052 and ADR-0018 expire now. The entries APR-0052 suspended apply again (APR-0018, APR-0021, APR-0051, APR-0031, APR-0047, APR-0049, and the router path of ADR-0003 and ADR-0004), unless a new APR entry changes them.
- The Loop 1 agents ran on openai/gpt-6-luna only under that exception, so the Loop 1 gateway stays stopped. Running the agents again needs a new APR entry.
- Open items move to Loop 2: P-26, P-28, P-31, P-32, P-37. P-36 (04:00 reset check) stays pending.
Closes: Loop 1. Ends: APR-0052, ADR-0018.
Changeable: yes. A change is a new APR entry.
Applies to: decisions/adr/ADR-0018-loop-1-cloud-only-exception.md; deploy/loop1/LOOP1-CLOSE-RECORD.md; deploy/loop1/STATE.md; the Loop 1 gateway on the VM

## APR-0072 - Calendar journal: 14-day active window, monthly archive (P-28, SD-004)
Status: approved
Decided by: CEO
Your answer: "yes" (to SD-004, 2026-10-25)
Meaning:
- The active calendar journal holds future entries, the last 14 days and anything not yet pushed to Google.
- Older lines move once a month to state/archive/calendar-YYYY-MM.md. The workspace git keeps the full history; nothing is deleted.
- The move runs in code, not in the model (ADR-0008, ADR-0011). The journal stays append-only (APR-0054, APR-0057).
- The rest of P-28 (status set, push job) is still open.
Changeable: yes. A change is a new APR entry.
Applies to: P-28; the CoS calendar journal in Loop 2; research/sandbox/2026-10-25-agy/P-28-calendar-sync.md

## APR-0073 - Loop 2 runs cloud-only on synthetic data (time-boxed exception)
Status: approved
Decided by: CEO
Your answer: "cloud only, the local model will be byoass for a future implementation due to technicly issues slowing down the progress. so perform with synthetic data-only on your own"; end date 2026-12-31: "Approved"; who runs it: "i will execute your guidilines and intrcutions from ubunut user, le't's leave the sandbiox for other tasks"; calendar: "it does not matter use google."; cost: "let's dont worry about cost ight no, defere for later." (2026-10-25)
Meaning:
- Loop 2 agents run on openai/gpt-6-luna through OpenClaw, cloud-only. Local model work is deferred.
- Data: synthetic only, under the same data rules as APR-0052. No real personal data in the agents' state or in Loop 2 Slack posts.
- The entries APR-0052 suspended are suspended again for Loop 2 (APR-0018, APR-0021, APR-0051, APR-0047, APR-0049, and the router path of ADR-0003 and ADR-0004), except APR-0031: Loop 2 writes to Google Calendar (P-28).
- Synthetic events may be written to the CEO's Google Calendar. Every delete still needs the CEO's approval (APR-0044).
- The CEO starts the gateway and runs the tests from the main VM account, following Claude's instructions. The sandbox account and its agent do not run the gateway and have no keys.
- Cost limits for Loop 2 are deferred (P-31). APR-0056 was for Loop 1. The OpenAI project limit stays as set in the OpenAI project settings.
- Expiry: when Loop 2 closes or on 2026-12-31, whichever comes first.
Changeable: yes. A change is a new APR entry.
Applies to: the Loop 2 OpenClaw setup on the VM; deploy/loop1/STATE.md; P-28; P-31

## APR-0074 - Moves and deletes by event ID use the Google Calendar REST API; gcalcli stays
Status: approved
Decided by: CEO
Your answer: "i accept your proposal. however don't remove gcalc and dont remove the guides we created for it. we should have a script in the repo for each scenario if we are goind to be using python for this." (2026-10-25)
Evidence: test on the VM, 2026-10-25. gcalcli 4.5.1 has no ID option: delete and edit take search text, and edit is interactive. The Google Calendar REST API created, moved, read and deleted one test event by its Google event ID.
Meaning:
- Moves and deletes by Google event ID go through the Google Calendar REST API, run by Python scripts in scripts/gcal/. Reads stay on gcalcli.
- gcalcli stays installed and documented (guides/calendar-gcalcli.md, APR-0041). It is not removed. It remains the fallback and the tool for reads and for actions by title.
- Every calendar scenario has its own script in the repo: list, find by title, get by ID, create, move, delete, and a round-trip test. No ad hoc scripts on the VM for these.
- The scripts use the existing gcalcli login (same file, same rules as APR-0041). No new credential.
- Rules the scripts enforce: only title, start and end go to Google (APR-0032); every title follows the mandate (APR-0034, APR-0035, APR-0037); only mandated, single events are moved or deleted, so personal events are never touched; every delete needs the CEO's approval first (APR-0044) and a matching title; no duplicate titles; every write script has --dry-run.
- Create: the repo also has a REST create script, because it returns the Google event ID that the journal records. Which tool the sync runner uses for create is decided when the runner is built (P-28).
- Not covered here: the sync runner itself, and how a high-privacy event shows as busy (APR-0032) alongside the mandated title. Both stay in P-28.
Closes: none (P-28 stays open)
Changeable: yes. A change is a new APR entry.
Applies to: scripts/gcal/; tests/unit/test_gcal_scripts.py; guides/calendar-rest-api.md; guides/calendar-gcalcli.md; decisions/PENDING.md (P-28)

## APR-0075 - Instruction set v1.7: the CHO's exact sessions_send call to the CoS; the CoS replies by answering
Status: approved
Decided by: CEO
Your answer: "1.7 approved" (2026-10-26)
Evidence: trajectory exports of the CHO and CoS sessions after runs loop2-scn-001 and loop2-scn-002 (2026-10-25 and 26), read on the VM and compared with the OpenClaw 2026.10.5 docs (concepts/session-tool.md, tools/subagents/tool-reference.md).
- In both runs the CHO's first sessions_send to the CoS set mode notify and watch true. watch was refused (forbidden: it needs status visibility, which the CHO does not have on the CoS session). notify only queues a message for the target's next turn and starts nothing (runStarted false). The CHO then tried mode resume, which is for paused native children, and was rejected. Only mode followup started a CoS turn (run 001 at 03:59:31 UTC, run 002 at 04:08:46 UTC). In run 002 one followup carried no task details, so the CoS could not act on it. This is the likely cause of the CoS running twice in run 018 too (not confirmed; run 018 was not exported).
- The CHO had not read the tool's declaration before calling it: describeCount stayed 0 until after the first errors, and its own reasoning said the schema was unknown. Our instructions never mentioned mode or watch.
- Every CoS sessions_send back to the CHO (1 in run 001, 3 in run 002) returned SESSION_WORK_START_CHANGED with sentBeforeError true: the message was delivered and only the acknowledgement failed. The CHO's followup calls already return the CoS's answer in the same result, with no error. The string appears in the tool result only, not in the gateway log, so a log count cannot show it (P-35 stays closed, APR-0068).
Meaning:
- CHO rule, appended to cho/AGENTS.md: "Handoff call (APR-0075, instruction set v1.7): to ask the CoS for a calendar change, call sessions_send with exactly these fields: sessionKey agent:cos:main, message (the whole task: what to do, dates and times, run ID, event ID), mode followup, timeoutSeconds 120. Never set watch. Never use mode notify or resume. Do not look up the tool's API files or list sessions first. The returned reply is the result. If a call fails or returns queued, resend the same message once with the same fields."
- CoS rule, appended to cos/AGENTS.md: "Reply by answering (APR-0075, instruction set v1.7): when the CHO's message asks for a calendar change, your answer to that message is the report to the CHO, with the run ID, the event ID and the two journal lines. Never call sessions_send to the CHO. If a send returns sentBeforeError true, it was delivered: do not send again."
- Apply with deploy/loop1/loop1-v17-upgrade.sh (gateway stopped; AGENTS.md of cho and cos only; run it with --dry-run first). No config change.
- Check: two Loop 2 scenario runs (P-38), read with scripts/verify/check_sessions_send.py.
- If the CoS still sends to the CHO after v1.7, the next step is a config rule (agents.entries.cos.tools.agentToAgent.send limited to coo). That needs its own APR entry; it is not decided here.
Closes: none (P-38 tracks the check)
Changeable: yes. A change is a new APR entry.
Applies to: the CHO and CoS instructions (v1.7); deploy/loop1/loop1-v17-upgrade.sh; scripts/verify/check_sessions_send.py; tests/scenario/bad-sleep-reschedule.md; deploy/loop1/STATE.md; P-38

## APR-0076 - Instruction set v1.7 verified in two Loop 2 runs; P-38 closed
Status: approved
Decided by: CEO
Your answer: "If the transcript is clean, a yes!" (2026-10-26, about run loop2-scn-004; Claude judged the transcript clean against the criteria below)
Evidence: v1.7 was applied on the VM at 01:43 AST on 2026-10-26 (loop1-v17-upgrade.sh; health check 43 PASS afterwards). Runs loop2-scn-003 (01:55 AST) and loop2-scn-004 (02:00 AST), both from Slack with the post starting with @COO:
- Checker (scripts/verify/check_sessions_send.py): all checks passed in both runs. Each run had exactly one CHO sessions_send to the CoS (mode followup, timeoutSeconds 120, no watch, status ok); the CoS sent nothing to the CHO; no SESSION_WORK_START_CHANGED in any result. Under v1.6, runs 001 and 002 had 5 and 4 CHO calls and 1 and 3 errors.
- Journal numstat 2 0 in both runs; the CHO logged -cho-01 (sleep) and -cho-02 (move).
- The COO reply named the CHO and the CoS with the event IDs in both runs; one line in the CoS channel; two lines in the CHO channel (one per event, as in runs 001, 015 and 016); no late reply; no FAILURE note.
Meaning:
- Instruction set v1.7 (APR-0075) stays as applied. P-38 is closed.
- The config option named in APR-0075 (remove cho from the CoS send list) is not needed. It stays available if a later run shows the CoS sending to the CHO again.
- Reopen P-38 (new APR entry needed) if the checker fails in a later run: the CHO sets mode notify or resume or watch, or the CoS sends to the CHO.
- The checker found the run by its run ID from this entry on (fix-68); the first version also counted the previous run's call from the same export.
Closes: P-38
Changeable: yes. A change is a new APR entry.
Applies to: the CHO and CoS instructions (v1.7); tests/scenario/bad-sleep-reschedule.md; deploy/loop1/STATE.md; scripts/verify/check_sessions_send.py

## APR-0077 - P-28: the Loop 2 calendar status set and the push job, as proposed
Status: approved
Decided by: CEO
Your answer: "P-28 is yes on the proposed" (2026-10-26). "The proposed" is the P-28 text in decisions/PENDING.md as it stood on 2026-10-26, summarised below. The sandbox draft research/sandbox/2026-10-25-agy/P-28-calendar-sync.md is a draft; this entry does not approve its details.
Meaning:
- Status set for the Loop 2 journal: requested, written, pushed, failed (with an attempt count and the last error), conflict, moved and delete-pending-approval, plus the Google event ID once pushed. Each change of status is a new line; the journal stays append-only (APR-0054, APR-0057), with the 14-day active window (APR-0072).
- Push job: a scheduled job in code, not the model (ADR-0008, ADR-0011), retries pending entries every 5 minutes (S-06, APR-0043). Before a retry it searches Google for the entry's unique name (APR-0034), so a write that succeeded but looked failed is not repeated.
- After 5 failures the COO is told and the CEO checks (S-06).
- If the Google token is revoked, all writes pause and an alert is posted (S-07, APR-0043).
- Unchanged: Google stays the calendar of record and the journal is the hold and audit trail (APR-0031); only title, start and end go to Google (APR-0032); moves and deletes by event ID use scripts/gcal/ (APR-0074); every delete needs the CEO's approval (APR-0044).
Not decided here (stays in P-28):
- Who posts the token-revoked alert while the CIO does not exist (Loop 2 has four agents).
- The status of an approved delete (the sandbox draft suggests "deleted"; it is not in the approved set).
- How a high-privacy event shows as busy together with the mandated title (APR-0032).
- What starts the job on the VM (the OpenClaw cron stays off).
- Which tool the job uses to create events (APR-0074 left it to this step), and the journal line format for the new statuses.
Closes: none (P-28 stays open until the job is built and tested)
Changeable: yes. A change is a new APR entry.
Applies to: P-28; the CoS calendar journal in Loop 2; scripts/gcal/ (the future push job); decisions/PENDING.md

## APR-0078 - P-28: answers to the four open points, and the push job built
Status: approved
Decided by: CEO
Your answer: asked with four choices on 2026-10-26; you picked "COO channel (Recommended)", "deleted (Recommended)", "Later, before real data (Recommended)" and "Plain cron under ubuntu (Recommended)".
Meaning:
- Alert target (point 1): the push job posts its alerts in the COO channel while the CIO does not exist. The channel ID is kept outside the repo (an environment setting on the VM). Every alert is also written to alerts.log in the job's state folder.
- Status of an approved delete (point 2): the status is "deleted". It joins the Loop 2 status set from APR-0077. The job runs a delete only after a delete-pending-approval line for the same event ID (APR-0044).
- High-privacy busy (point 3): deferred. It is decided before real data comes in, not now (APR-0073: Loop 2 runs on synthetic data).
- What starts the job (point 4): plain cron under ubuntu on the VM, every 5 minutes. The OpenClaw cron stays off. The CEO adds the cron line himself after a manual dry run and an alert test.
Build choices made by Claude, inside these answers (a change is a new APR entry):
- The job creates events with scripts/gcal/gcal_common.py (create_event, move_event, delete_event), so every rule of APR-0074 applies.
- Journal lines the job writes: same 7 columns plus a detail column, requested by "sync": pushed (google=<id>), failed (attempt=N; error=...), conflict (reason=...). A conflict is not retried.
- Deletes only run when the job is started with --allow-deletes. The default is off. The CEO turns it on later.
- A revoked login writes a pause file, sends one alert and stops all writes until the CEO logs in again and removes the file (S-07).
Closes: none (P-28 stays open until the job has run on the VM)
Changeable: yes. A change is a new APR entry.
Applies to: P-28; scripts/gcal/gcal_sync.py; scripts/gcal/gcal_sync_cron.sh; guides/calendar-sync-job.md; the CoS calendar journal in Loop 2

## APR-0079 - P-28: high-privacy events show as busy, built and tested now with fake data
Status: approved
Decided by: CEO
Your answer: "yes, item 1 and 2 is a go, but also include the high-privacy test with fake data to see it shown as busy in the test calendar, we dont need real data again for testing." (2026-10-26)
Meaning:
- Point 3 of P-28, deferred by APR-0078, is brought forward: it is built and tested now, on the test calendar, with fake data. The outcome is the one APR-0032 already decided: a high-privacy event appears in Google as "busy".
- Items 1 and 2 (five failed attempts, revoked login) are tested on the VM with throwaway state folders and a broken copy of the login file. Results: guides/calendar-sync-job.md.
Build choices made by Claude inside APR-0032 (a change is a new APR entry):
- A journal line is high privacy when its detail column holds privacy=high. The mark is remembered through the job's pushed line, and it follows a move: if the old name was high privacy, the new name is too, even if the new line has no mark.
- Google gets the title "busy", the start, the end, and the setting that shows the time as busy. The mandated title never goes to Google for these events.
- One extra field is stored in Google for these events: a hidden key that holds the journal's event ID (for example r1-cho-01). It holds no personal data. It is how the job finds the event again, because the title no longer identifies it. This is one field beyond title, start and end (APR-0032). You can say no to it.
- Moves and deletes of these events go by the Google event ID written in the journal's pushed line, and only touch an event that is titled busy and carries the hidden key. A delete still needs the delete-pending-approval line and --allow-deletes (APR-0044).
- The CoS does not write privacy=high today. Making it write the mark is an agent instruction change and needs a new yes from you. Until then nothing in Loop 2 is marked, and Loop 2 stays on synthetic data (APR-0073). Who decides that an entry is high privacy (the privacy gate, ADR-0003) and how that reaches the CoS must be decided before real data.
Closes: none (P-28 stays open until the high-privacy test has run on the VM)
Changeable: yes. A change is a new APR entry.
Applies to: P-28; scripts/gcal/gcal_busy.py; scripts/gcal/gcal_sync.py; guides/calendar-sync-job.md; contracts/policy/calendar.yaml (high_privacy_title)

## APR-0080 - P-28 closed: the calendar push job is built and tested
Status: approved
Decided by: CEO
Your answer: "close p28" (2026-10-26)
Evidence (2026-10-26, VM, Google test calendar, fake data; guides/calendar-sync-job.md has the commands and results):
- Unit tests: 137 pass on the repo, 116 of them on the VM.
- Push job by hand: dry run wrote nothing; create; second run with no change; move in place with a new title; conflict (same title at another time) left Google unchanged; delete gate refused without the delete-pending-approval line and without --allow-deletes, and ran with both (APR-0044).
- Failures: five failed attempts counted, the fifth marked final, one alert, no sixth try. A revoked login (broken copy of the login file) paused all writes, sent one alert and nothing was written.
- Alerts reached the COO channel once the gateway (terminal T1) was running. They need the gateway; otherwise they go to alerts.log only.
- High-privacy events (APR-0079): created as busy with a hidden key, the mandated title never in Google, moved and deleted by the same path.
- Cron (APR-0078): plain cron under ubuntu, every 5 minutes, installed 2026-10-26 13:31 AST on the test calendar. Scenario run loop2-scn-005 with the cron live: the CoS's move was pushed as a move of the same Google event.
Meaning:
- P-28 is closed. The job, the cron wrapper, the tests and the guide stay as built (APR-0077, APR-0078, APR-0079).
- Not part of this closure, moved to a new item P-40: the CoS writing the privacy mark and the privacy gate, switching the cron from the test calendar to the real calendar, the monthly journal archive job (APR-0072), and a look at the busy block in the Google Calendar app. All of it is needed before real data.
- Not part of this closure either: P-39 (the CHO did not write the health plan in run 005). It is a scenario finding, not a calendar one.
Closes: P-28
Changeable: yes. A change is a new APR entry.
Applies to: scripts/gcal/gcal_sync.py; scripts/gcal/gcal_busy.py; scripts/gcal/gcal_sync_cron.sh; guides/calendar-sync-job.md; decisions/PENDING.md

## APR-0081 - P-39: option A, instruction set v1.8 for the CHO
Status: approved
Decided by: CEO
Your answer: "lets go with A as recommended." (2026-10-26, after the root cause in P-39: the COO's wording differed between runs 005 and 006, and the setup note does not say what a change is)
Meaning:
- Option A of P-39: the health plan holds health facts and plan changes; calendar moves stay in the CoS journal.
- One rule is added to the CHO's AGENTS.md (instruction set v1.8), by deploy/loop1/loop1-v18-upgrade.sh (gateway stopped, AGENTS.md only, CHO only), in these words:
  - Health facts (APR-0081, instruction set v1.8): when a message reports a health fact (sleep, weight, a symptom), append a line to state/health-plan.md with the run ID and its own event ID, even if the message also asks for something else.
- Criterion 2 of the scenario (tests/scenario/bad-sleep-reschedule.md) becomes: the CHO logs the sleep fact in state/health-plan.md with its own event ID. It no longer asks for a line for the calendar move.
- The COO, the CoS and the CFO are not changed. The calendar path is not changed.
- Verification: two scenario runs in a row, each with the sleep line in the health plan (own event ID), the checker passing (APR-0075) and no deletions in the journal numstat. P-39 closes after that, with a new APR entry. If a run fails, P-39 stays open.
Closes: none (P-39 stays open until the two runs)
Changeable: yes. A change is a new APR entry.
Applies to: the CHO instructions (v1.8); deploy/loop1/loop1-v18-upgrade.sh; tests/scenario/bad-sleep-reschedule.md; decisions/PENDING.md (P-39)

## APR-0082 - P-39 closed: instruction set v1.8 verified by two passing runs
Status: approved
Decided by: CEO
Your answer: "yes close p39" (2026-10-26)
Evidence (2026-10-26, VM, Slack, calendar cron live on the Google test calendar, fake data):
- v1.8 (APR-0081) was applied on the VM at 17:17 AST (commit d26a5e8 in the CHO workspace, AGENTS.md only).
- loop2-scn-007 and loop2-scn-008, in a row, each passed: the CHO wrote the sleep fact (cho-01) in state/health-plan.md with its own event ID, and the move (cho-02) as well; the checker passed all checks (one CHO call to the CoS, followup, ok; no CoS send; no SESSION_WORK_START_CHANGED); the COO reply named the CHO and the CoS with both event IDs; numstat 5 0 then 6 0 (no deletions); the job moved the Google event in place.
Meaning:
- P-39 is closed. The CHO rule of APR-0081 stays as applied.
- The scenario passes with criterion 2 as reworded in APR-0081.
Closes: P-39
Changeable: yes. A change is a new APR entry.
Applies to: the CHO instructions (v1.8); tests/scenario/bad-sleep-reschedule.md; decisions/PENDING.md

## APR-0083 - P-31 closed for Loop 2: cost kill and alert
Status: approved
Decided by: CEO
Your answer: "It treats 5USD per day as a kill;  an alert at 1 USD per day. this is already done and verify so close it foor lop 2" (2026-10-26)
Meaning:
- Cost control for Loop 2: 5 USD per day is a kill, 1 USD per day is an alert. The CEO states this is done and verified; the repo holds no run record of it, so this entry rests on the CEO's statement.
- The enforced 5 USD monthly project limit (CEO 2026-10-23) and the per-run ceiling of APR-0056 are not changed.
- This replaces the earlier "can wait" (SD-002, 2026-10-25) and the deferral in APR-0073 for cost limits.
- P-31 is closed for Loop 2. Anything for later loops is a new item.
Closes: P-31
Changeable: yes. A change is a new APR entry.
Applies to: decisions/PENDING.md (P-31); OpenAI project settings

## APR-0084 - P-37 closed for Loop 2: COO SQLite maintenance warning
Status: approved
Decided by: CEO
Your answer: "yes on closing P-31, P-37 and P-32 (with the narrow version);" (2026-10-26)
Evidence: on the gateway logs of the Loop 2 runs loop2-scn-001 to -008 (2026-10-25 and 2026-10-26): one 'SQLite session write failed' on the COO (2026-10-26 01:55:50 AST, at the post of run 003), none in the other seven runs, and 0 'maintenance paused' lines (OpenClaw's 3-rejection limit was never reached). No visible effect in any run.
Meaning:
- P-37 is closed for Loop 2. The earlier condition (keep it open until checked on real Loop 2 runs) is met.
- Reopen if a 'maintenance paused' line appears in a gateway log, or if a run shows a visible effect of the warning.
Closes: P-37
Changeable: yes. A change is a new APR entry.
Applies to: decisions/PENDING.md (P-37)

## APR-0085 - P-32 closed for Loop 2: memory is the state files
Status: approved
Decided by: CEO
Your answer: "yes on closing P-31, P-37 and P-32 (with the narrow version);" (2026-10-26)
Meaning:
- Memory search (memory-core) and dreaming stay off through Loop 2 (APR-0061 stands).
- Agent memory for Loop 2 is the state files: the calendar journal, the health plan and the other state files. Loop 2 runs 001 to 008 worked on this basis.
- ADR-0011 is written (append-only history, projected state) from what is built.
- Not decided and moved to a new item P-41: local embeddings (SD-005), checking state files before answering (SD-006), short COO handoffs (SD-007), and how much context the COO builds up.
Closes: P-32
Changeable: yes. A change is a new APR entry.
Applies to: decisions/adr/ADR-0011-append-only-history-projected-state.md; decisions/PENDING.md (P-32, P-41)

## APR-0086 - Privacy mark: the chief marks it; health and finance default to high (P-40 item 1)
Status: approved
Decided by: CEO
Your answer: "yes on "chief marks it, health and finance default to high"" (2026-10-26)
Meaning:
- The CoS does not decide privacy. When it writes a journal line it writes privacy=high in the detail column if (a) the requesting chief marks the entry high privacy, or (b) the requesting chief owns health or finance (the CHO or the CFO), which is high by default. The push job then shows the entry as busy in Google (APR-0079).
- The CEO can ask for any entry to be private in a request; the CoS then writes the mark.
- Lowering a default (showing a health or finance entry in full) is not allowed until the CEO decides it in a new entry.
- This changes the CoS and the CHO/CFO instructions (instruction set v1.9). It is built as a script and tested on fake data before it is applied. Nothing changes on the VM with this entry.
- Verification: a scenario run on fake health data in which the Google test calendar shows the entry as busy, the mandated title is not in Google, and the journal numstat has no deletions.
Closes: none (P-40 stays open for the real calendar and the archive job)
Changeable: yes. A change is a new APR entry.
Applies to: the CoS, CHO and CFO instructions (v1.9); decisions/PENDING.md (P-40)

## APR-0087 - Busy block seen in the Google Calendar app (P-40 item 4)
Status: approved
Decided by: CEO
Your answer: "i checke earlier and the calendar showed busy, so we can close this aswell" (2026-10-26)
Meaning:
- The CEO looked at the test calendar in the Google Calendar app earlier and the high-privacy event showed as busy. P-40 item 4 is done.
Closes: none (item of P-40)
Changeable: yes. A change is a new APR entry.
Applies to: decisions/PENDING.md (P-40)

## APR-0088 - Instruction set v1.9 and the job change for privacy (carries out APR-0086)
Status: approved
Decided by: CEO
Your answer: "yes on 'chief marks it, health and finance default to high'" (APR-0086, 2026-10-26); this entry records what was built from it
Meaning:
- Built, not yet applied on the VM: deploy/loop1/loop1-v19-upgrade.sh (CHO, CoS and CFO; AGENTS.md only; gateway stopped). Rules: the CHO and the CFO say privacy=high in every message to the CoS; the CoS writes privacy=high in the journal detail column for an entry the chief marked, for every CHO or CFO entry, or when the CEO asked, on the moved line and the new line; it never writes a lower privacy for an entry that was high.
- Needed by the rule, so built with it: the push job turns a normal Google event into a busy event when the entry is marked high later or a move carries the mark (`made busy`). Before this a move of a normal event into a high-privacy entry was a conflict. Busy to normal is still not supported.
- Added with it: gcal_delete.py --busy-key, so a leftover busy event can be deleted with the CEO's approval.
- Verification: the scenario run in tests/scenario/bad-sleep-reschedule.md ("Loop 2 privacy checks under v1.9"). If a run fails, nothing else changes.
Closes: none (P-40 stays open for the real calendar and the archive job)
Changeable: yes. A change is a new APR entry.
Applies to: scripts/gcal/gcal_busy.py; scripts/gcal/gcal_sync.py; scripts/gcal/gcal_delete.py; deploy/loop1/loop1-v19-upgrade.sh; the CHO, CoS and CFO instructions (v1.9); tests/scenario/bad-sleep-reschedule.md; guides/calendar-sync-job.md

## APR-0089 - Instruction set v1.9.1: the CoS never edits the journal header (Claude Code handover)
Status: approved
Decided by: CEO
Your answer: "i will install claudei the terminal, prepare a prompt to handover this loop to him, i will give me him ful autority based on your prompt then i will tell you what he did and found" (2026-10-26). The prompt allowed a smallest-change fix of an agent instruction on the condition that its text and reason are recorded here. Then: "here you go" (the report).
Evidence (2026-10-26, VM, Slack, fake data, test calendar; report in ops/handover-2026-10-26-claude-code-report.md):
- Run loop2-scn-009 (first under v1.9): everything passed except the journal numstat (6 1, then 7 1). Cause found by Claude Code in the CoS trajectory: the CoS edited the journal header line, adding "| detail" to "requested by", because the v1.9 rule describes an 8-column line and the header has 7. The seed lines and the job were not involved.
- Fix, applied on the VM by Claude Code with the gateway stopped: one rule appended to the CoS AGENTS.md (commit 78b71ff, "Loop 1 instructions v1.9.1 (journal append only)"):
  - Journal append only (instruction set v1.9.1): the header line "name | start | end | status | run ID | event ID | requested by" stays exactly as it is. The detail column is not added to it. Never edit, replace or delete an existing journal line, including the header. Only add new lines at the end of the file, and put privacy=high in the detail column of those new lines.
- Run loop2-scn-010 is void (a prep error: the CHO session compaction failed right after a gateway restart, so the CHO remembered run 009 and did not call the CoS; not an instruction fault).
- Runs loop2-scn-011 and loop2-scn-012, in a row, passed all criteria: numstat 5 0 then 6 0, checker all passed, both CoS lines carry privacy=high, header untouched, sleep line with its own event ID, COO summary names the CHO and the CoS with both event IDs, Google shows one busy event on 10-29 07:00 and no Workout title for 10-28 or 10-29. 0 'maintenance paused'; no 'SQLite session write failed' from the current gateway process.
Meaning:
- The v1.9.1 rule stays as applied. The verification asked in APR-0086 (a scenario run that shows busy in the test calendar) is met by runs 011 and 012. P-40 item 1 is done.
- Since this handover the gateway runs from Claude Code's shell in the background (log ~/loop1/gateway.log), not from terminal T1. The CEO decides when T1 owns it again (see deploy/loop1/STATE.md).
Closes: none (P-40 stays open for the real calendar and the archive job)
Changeable: yes. A change is a new APR entry.
Applies to: the CoS instructions (v1.9.1); deploy/loop1/loop1-v191-upgrade.sh; tests/scenario/bad-sleep-reschedule.md; decisions/PENDING.md (P-40); deploy/loop1/STATE.md

## APR-0090 - Next steps for Loop 2: 04:00 reset report, gateway keep-alive, real-calendar test, Loop 2 close record
Status: approved
Decided by: CEO
Your answer (2026-10-26, evening): "if part 1 need a red on the logs in the morning, why woundnlt'd we be able to see the resets fro other nights?? or if it reset we should be able to create a script that runs say at 5:00 to read it and maybe post it to slack for me to see it. have claude code do that on the prompt, also you should tell claude that the gateway need to keep running and i might close the laptop to sleep losing terminal and he should still be running it i the vm." / "2. ok let him do the test on the real calendar" (his primary Google calendar; the address is not written in the repo) / "3. do it" / "4. defer"
Meaning:
- P-36 (04:00 reset check): first look at the evidence of past nights (gateway logs, session stores) to see the resets. Then a read-only script runs at 05:00 AST by cron on the VM and posts a short report to Slack (the COO channel) and to a log file. The reset is lazy (applied at the first message after 04:00), so "no message yet, reset pending" is a normal result. The "not to be raised" request of 2026-10-25 is lifted.
- The gateway must keep running on the VM without a terminal. Claude Code runs and keeps it (detached; one process); the CEO may close his laptop.
- P-40 item 2: Claude Code does a test on the CEO's primary Google calendar with the existing job and test events only (create, move, make busy, delete by key), reads no personal event titles, and leaves the cron on the test calendar. Moving the cron to the real calendar is NOT approved by this entry; it stays a separate decision.
- P-40 item 3 (monthly journal archive job, APR-0072): deferred.
- Loop 2 close record drafted at deploy/loop2/LOOP2-CLOSE-RECORD.md. It is a draft; Loop 2 closes only on the CEO's sign-off in a new APR entry.
- The agents' instructions are not changed by this entry.
Closes: none
Changeable: yes. A change is a new APR entry.
Applies to: decisions/PENDING.md (P-36, P-40); deploy/loop2/LOOP2-CLOSE-RECORD.md; deploy/loop1/STATE.md; the gateway and cron on the VM

## APR-0091 - Gateway as a systemd user service; 05:00 reset report cron (carries out APR-0090)
Status: approved
Decided by: CEO
Your answer: the words recorded in APR-0090 ("the gateway need to keep running and i might close the laptop to sleep losing terminal and he should still be running it i the vm"; "create a script that runs say at 5:00 to read it and maybe post it to slack for me to see it. have claude code do that on the prompt"). This entry records what Claude Code built from them; the CEO can refuse or change either part.
Evidence (2026-10-26 evening, VM; report in ops/handover-2026-10-26-claude-code-report-2.md, files in deploy/loop2/vm/):
- Gateway: user service openclaw-loop1-gateway (unit file deploy/loop2/vm/openclaw-loop1-gateway.service, installed at ~/.config/systemd/user/). Restart=always (5 s), starts at boot (linger on), log ~/loop1/gateway.log, secrets only through EnvironmentFile (never printed). A kill -9 of the main process was followed by an automatic restart with one process and Slack connected on all four accounts. Commands from any terminal on the VM: systemctl --user status|stop|start|restart openclaw-loop1-gateway. Stop it before changing any AGENTS.md; do not start a second gateway by hand. Stopping can take up to 330 s (graceful drain). Terminal T1 is no longer needed.
- 05:00 report: cron line 0 5 * * * bash $HOME/loop1/daily-reset-report.sh >> $HOME/loop1/reset-check/cron.out 2>&1 (AST). The script (daily-reset-report.py) is read-only on the agents' databases, never messages an agent, saves an append-only snapshot, appends to ~/loop1/reset-check/report.log and posts to the COO channel. One real run at 20:05 AST posted. A result of "no message since 04:00, reset pending" is normal (the reset is lazy).
- P-36 history (read-only on the databases): one daily reset confirmed (COO channel session, reason daily, 2026-10-24 18:41, the first message after 04:00). The reset is a marker inside the channel session, not a new session ID; main sessions got new IDs at the first activity after 04:00, but the prep compactions ran at the same times, so daily reset and compaction cannot be separated there. The CHO, CoS and CFO channel sessions show no readable marker; the 05:00 reports will settle it.
Meaning:
- The systemd service is the gateway's owner. Claude Code or the CEO may stop and start it with systemctl on the VM.
- The 05:00 report cron stays on. P-36 stays open until the reports have shown the resets of the CHO, CoS and CFO.
Closes: none
Changeable: yes. A change is a new APR entry.
Applies to: deploy/loop2/vm/openclaw-loop1-gateway.service; deploy/loop2/vm/daily-reset-report.sh; deploy/loop2/vm/daily-reset-report.py; the gateway and cron on the VM; deploy/loop1/STATE.md; decisions/PENDING.md (P-36)

## APR-0092 - Delete gate, approval requests, CFO route, overlaps, confirmed reports (instruction set v1.10)
Status: approved
Decided by: CEO
Your answer: "yes to all, proceed" (2026-10-26, to the six proposals a to f below, after handover 3 showed the gaps; the CEO's own points: "the report should always be confirmed. nothing to assumptions"; on overlaps "COS should log this information and there should be an easy understanding for me to know what happend ... the system can't depend all the time on my to self heal"; on approvals "an agent tell me ... risk analysis and then i can say explain more or approved")
Evidence: handover 3 (ops/handover-2026-10-26-claude-code-report-3.md; tests/scenario/delete-approval.md, cfo-entry.md, overlap-conflict.md, privacy-request.md): runs loop2-scn-013 and -017 wrote deleted at once with no delete-pending-approval line, the COO said the CEO had approved when he had only asked, and reported Google as deleted when nothing changed (the job's guard held); in 015 the CFO could not message the CoS, so the COO relayed; in 016 the CoS refused an overlap and logged nothing.
Meaning:
- a) Deletes (refines APR-0044): the CEO's own clear instruction to delete a named entry is his approval: the CoS appends delete-pending-approval and deleted (same event ID). A delete a chief asks for, or a delete the CEO only asks about, gets only the pending line and the COO asks the CEO. Moves are not deletes (APR-0057).
- b) Deletes reach Google through the 5-minute job only when GCAL_ALLOW_DELETES=1 is set in ~/loop1/gcal-sync/env, and only after the delete gate passes its re-runs. The job still deletes only a LifeOS-titled event with a pending line and a deleted line for the same event ID; personal events are never touched.
- c) Approval requests: anything that needs the CEO's yes is asked in one standard message: What. Used for. Why now. Risk if approved. Risk if not. Recommendation. Reply: approve, explain more, or keep. It applies to every agent that asks the CEO (the COO today; the CIO for system changes later).
- d) The CFO sends its calendar entries straight to the CoS (as APR-0044 intends; the CoS relieves the COO), with the CHO's handoff call and its own event IDs. Its OpenClaw send list must include the CoS (a VM config change).
- e) Overlaps (S-08): the existing entry keeps its slot; the CoS appends a conflict line (reason=overlaps <entry>), offers the nearest free slot, writes the entry when the requester accepts, and the COO sends the CEO a one-line notice (no action needed unless he overrides). Only when the time cannot move does the CEO decide. Which domain wins a hard clash is not decided here.
- f) The COO reports only what the CHO, CFO or CoS confirmed, names who confirmed it, says "not confirmed" otherwise, never says Google changed and never makes up an event ID.
- The exact rule text is in deploy/loop1/loop1-v110-upgrade.sh (CoS: deletes, overlaps; COO: confirmed reports, approval requests and notices; CFO: handoff call). Built and unit-tested; not applied on the VM by this entry's fix script.
- Verification (P-42): scenario re-runs of delete (CEO instruction, CEO question, chief request), CFO entry, overlap, and the bad-sleep regression; then GCAL_ALLOW_DELETES=1 and one approved delete that reaches the test calendar.
Closes: none (P-42 opened)
Changeable: yes. A change is a new APR entry.
Applies to: the CoS, COO and CFO instructions (v1.10); deploy/loop1/loop1-v110-upgrade.sh; scripts/gcal/gcal_sync_cron.sh; the CFO send list in the OpenClaw config on the VM; tests/scenario/*.md; decisions/PENDING.md (P-42)

## APR-0093 - Delete order, delete-line event IDs, approval layout, delete flag (instruction set v1.10.1)
Status: approved
Decided by: CEO
Your answer: "yes, proceed" (2026-10-26 23:30, to the four proposals below, after Claude Code's handover 4 and the assistant's verification message)
Evidence: handover 4 (ops/handover-2026-10-26-claude-code-report-4.md; tests/scenario/delete-approval.md): run loop2-scn-018 failed (the CoS wrote only the deleted line, after the COO wrote that the CEO's exact words approved the deletion); 019 wrote the entry title as the event ID on the delete lines and 025 an ID the COO made up; the seven-item approval request (020) came out on one line. Runs 019, 020, 021 and 025 passed; the job's guard held in every run.
Meaning:
- 1) GCAL_ALLOW_DELETES=1 stays ON in ~/loop1/gcal-sync/env while the cron pushes only to the test calendar. The cron is not moved to the real calendar until the delete gate passes repeatedly (at least three D1 runs in a row after v1.10.1).
- 2) The CoS always appends delete-pending-approval first, even when the message says the CEO approved; deleted comes second and only on the CEO's own quoted words. The COO never writes approving or approved unless the CEO's words say so.
- 3) Both delete lines carry the event ID of the entry's existing journal line (for example seed-3), never the title and never an ID the COO makes up. If the CoS cannot find the entry it writes nothing and says so.
- 4) Each item of the seven-item approval request is printed on its own line.
- The exact rule text is in deploy/loop1/loop1-v1101-upgrade.sh (CoS: delete order and event ID; COO: delete requests and approval layout). Built and unit-tested; not applied on the VM by this entry's fix script.
- Verification (P-42): the D1 delete scenario run at least three times in a row with new run IDs, each with pending then deleted lines, the entry's event ID, and the COO reply true; D2 once more; the regression bad-sleep-reschedule once.
Closes: none (P-42 stays open until the re-runs pass)
Changeable: yes. A change is a new APR entry.
Applies to: the CoS and COO instructions (v1.10.1); deploy/loop1/loop1-v1101-upgrade.sh; the delete flag in the VM cron environment; the move of the cron to the real calendar (waits); tests/scenario/delete-approval.md; decisions/PENDING.md (P-42)
