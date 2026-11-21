# Project status and the way to completion (planning chat answers, 2026-11-20)

Saved by the CEO's request to consult later. These are two answers from the planning chat, kept as written. They are advice, not decisions: nothing here is approved, no loop is started, and no APR is recorded for it. They build on research/architecture-review-2026-11-14.md (Fable's review, P-49). Counts and states are as of 2026-11-20.

---

## Answer 1: where we are, what is missing, and do we design each topic one by one?

You're right. The original design names all of this, but the mechanism that would make each new topic cheap was never designed. Below is where we stand and what that means for getting to the end.

### Where we are

Seven loops are closed. Almost all of that work went into the parts every domain shares, and that work only has to happen once:
- **Shared plumbing:** routing between agents, the calendar push, the delete gate (no delete without your approval), the privacy gate (built, but only watching), encrypted backup and restore, compaction, the health check, and a rebuildable repo.
- **Agents:** 5 of the 15 chiefs in design/roster.md are live: COO, CoS, CHO, CFO and CLO. None of the 17 small helper bots in the roster exists yet (nutritionist, travel planner and so on).
- **Real use:** you're running on real data, and 11 real requests are scored so far: 8 passed, 1 partial, 2 failed.

The roster already says what you're describing. It gives the CLO travel, hobbies, home projects, entertainment and vehicle maintenance, and the CHO nutrition, sleep and supplements. So the scope was planned. But of the 16 design files, 12 are empty. Three of the empty ones are exactly the ones that would answer your question: templates-and-learning.md, agent-lifecycle.md and memory-and-data.md. That's the gap you've spotted.

### Do you have to design each topic one by one?

No. There are three different cases.

**1. A new topic inside an existing chief** (CLO for orders, vacations or your dogs; CHO for nutrition). This should not need design or training. The model already knows how to keep a nutrition log or a vet-visit record. You've already seen it: when you asked the CLO to track vehicle maintenance, it set up its own files and columns, with no handover (rows 5 and 6 in the request log).

What gets in the way today is that the instructions are written narrowly. The CLO's file says "starting with the TV shows" and lists show fields. One generic rule would cover dogs, trips and orders without a separate design for each: "when the CEO starts tracking something new, propose a simple log, confirm it with him, then append only."

**2. Anything that touches the outside world or carries risk.** That means calendar writes, deletes, money, health data (high privacy), and live data feeds (a wearable export, an e-commerce account). These do need a decision each time, and that's where most of our effort rightly went. The good news is that most of it is reusable. The calendar path and the delete gate already work for any chief.

**3. A new chief** (Family, Career and so on). This costs real setup each time: a Slack app, config, a routing rule in the COO, health checks. Today that takes about two handovers. It should be one repeatable recipe rather than a fresh design each time.

### Why it has felt slow

Two honest reasons:
- **Platform before domains.** We built the safety work before widening the domains, which was deliberate and is mostly done.
- **Fixing failures with prose rules.** Each failure got another instruction rule in the COO's file, and each rule needed a draft, an approval and a handover. The status-question work (v1.10.10, then v1.10.11) is an example. That pattern doesn't scale. Fable's review made the same point: shared behaviour should live in code (like the routing log, P-51), not in sentences each agent may or may not follow.

### What's missing to reach completion

1. **A definition of done.** There isn't one today. For example: which domains must be live, and what real-request pass rate counts as working (Fable suggested 18 of 20).
2. **A topic recipe.** Generic chief instructions plus the "new topic" rule, so adding a topic is a conversation, not a loop.
3. **A chief recipe.** One script or handover that adds any chief from the roster.
4. **Shared behaviour in code.** A common state format and the routing log, so status questions work for every agent without a rule per agent.
5. **Platform items still open.** Wiring the privacy gate in (one of the four conditions the repo sets before real data), the real Google calendar, and helper bots, which can wait.
6. **The structural choice (P-49).** With many agents, every new chief carries setup cost. With Fable's single agent and topic files, "track my dogs" becomes trivial. The trade-off is weaker separation between domains. You don't need to decide now, but it bears directly on this.

If you want, Loop 8 could be "make domains cheap": the topic rule and the chief recipe, proven by adding nutrition to the CHO and your dogs to the CLO with no design document.

---

## Answer 2: the recommendation

My recommendation: keep the multi-agent design, but change how it grows. Your requirement that each agent works from its own domain context is the strongest reason to keep separate agents, and it's working. Routing to the right chief has passed every time in the request log. What doesn't scale is the way we've been extending it. Fable's review is right about that part, even though I wouldn't take its "one agent" conclusion.

**1. Keep the domain chiefs; turn the technical chiefs into code.**
The roster has 15 chiefs. Five of them (CIO, CISO, CKO, CSTO, CMO) are system functions: infrastructure, security, memory, audits and dashboards. We already do most of that in code that's more reliable than an agent: the health check, backup, compaction, the delete gate and the privacy gate. I'd remove those five as agents. Real agents would then be:
- **The two coordinators:** the COO and the CoS.
- **Domain chiefs:** added only when you actually have work for them. Health, Finance and Lifestyle are live today, and Family and Career would be next.

Fewer agents means less setup and fewer handoffs to go wrong, with domain separation intact.

**2. Make topics cheap inside each chief.**
Each chief gets the same generic instructions plus one rule: a new topic gets its own log, the chief proposes the columns, you confirm, and from then on it only appends. That way, CLO can take on dogs, trips and orders, and CHO can take on nutrition, each through a conversation. Every topic keeps its own file, so context stays specific per domain and even per topic. No design document, no handover, no training.

**3. Take Fable's code ideas instead of adding more prose rules.**
I'd stop fixing failures by adding sentences to the COO's instructions. Three of Fable's ideas cover it:
- **A routing log written by code (P-51).** Status questions would then work for every agent.
- **One structured state format for all chiefs.** SQLite, or a common file layout.
- **A small code check that verifies a chief really logged what it claims.**

These are built once and work for every domain, including ones that don't exist yet.

**4. Write a definition of done.**
For example:
- the chiefs you actually use are live;
- 18 of the last 20 real requests pass (Fable's number);
- the privacy gate is wired in and blocking, not just watching (you're on real data, so this matters);
- adding a topic takes no handover, and adding a chief takes one.

When those hold, the build is complete and anything after it is ordinary use and tuning.

**Proposed Loop 8: "make growth cheap"**
- the generic chief template and the topic rule;
- proof by adding nutrition to the CHO and your dogs to the CLO, with no design document;
- the routing log (P-51) to replace the per-agent status rules;
- the definition of done written down and approved.

The roster trim and wiring the privacy gate would come next, as Loop 9.

I recommend against collapsing to one agent now. You'd give up the domain separation you've asked for, and you'd throw away routing that works. If the cheap-growth loop still feels heavy afterwards, Fable's single-agent option becomes the fallback.

It's your call. If you agree, I'll draft the Loop 8 scope for your approval, and nothing changes until you approve it.
