# Week 2 — Use Case Identification & Prioritization

**Goal:** Learn to identify, evaluate, and prioritize AI use cases systematically. Move from "I have an idea" to "I've validated this is worth solving."

The biggest mistake in capstone projects is falling in love with a solution before understanding the problem. This week is about building a rigorous process for finding and selecting the right problem to solve.

---

## The Process: From Market Research to Problem Statement

### Phase 1: Broad Market Research
Before committing to a use case, understand the landscape of problems out there.

**Key Questions:**
- What problems are organizations actually trying to solve with AI?
- Which industries are seeing the most agentic AI adoption?
- What are the common pain points across sectors?

**Resources:**
- [`market-research/research-findings.md`](./market-research/research-findings.md) — Curated research from McKinsey, BCG, Deloitte, PwC, Gartner, and other consulting firms (past 6 months)
- Industry reports, whitepapers, and market analysis on AI adoption

**Exercise:**
Review 3–5 research reports from different industries. Note:
- The specific problems being solved
- The expected benefits quantified (time saved, cost reduced, errors prevented)
- The common patterns across industries

---

### Phase 2: Frameworks for Evaluation
Once you have a list of potential problems, you need a systematic way to evaluate them.

**Key Questions:**
- How do you compare two different use case ideas?
- What criteria matter most for a 10-week capstone?
- How do you avoid picking something too easy or impossible?

**Resources:**
- [`use-case-frameworks/framework-findings.md`](./use-case-frameworks/framework-findings.md) — 12 different frameworks for evaluating and prioritizing AI use cases

**Common Evaluation Criteria:**
| Criterion | Why It Matters |
|-----------|----------------|
| **Problem Severity** | How painful is this problem? (1–5) |
| **Data Availability** | Do you have (or can you get) the data needed? |
| **Technical Feasibility** | Can this be built in 10 weeks? |
| **Team Expertise** | Do you understand the domain? |
| **Competitive Landscape** | Who else is solving this? Is there an angle? |
| **User Validation** | Have you talked to 3–5 people with this problem? |
| **Success Metrics** | How will you know you solved it? |
| **Failure Modes** | What could kill this project? (cost, API limits, hallucinations) |

**Exercise:**
Pick a framework from the resources. Apply it to 2–3 potential use case ideas. Document your scoring and rationale.

---

### Phase 3: Problem Statement Framing
Once you've selected a use case, frame it clearly and convincingly.

**The Y Combinator Format:**
> "[Specific user type] struggles with [specific problem] because [root cause]. Currently they [current workaround], which causes [specific pain]. If solved, they would [measurable benefit]."

**What Makes a Good Problem Statement:**
1. **Specific** — Not "improve healthcare" but "reduce patient no-shows at urban clinics"
2. **Measurable** — Define how you'll know it's solved
3. **Current Pain** — Describe the status quo and why it hurts
4. **Target User** — Who exactly has this problem?
5. **Expected Benefit** — What changes when this is solved?

**Resources:**
- [`problem-statement-framing/problem-statement-examples.md`](./problem-statement-framing/problem-statement-examples.md) — Examples from successful YC companies and startups

**Good Example:**
> "Supply chain managers at mid-size manufacturers (50–500 employees) spend 6+ hours weekly reconciling inventory data across 3+ disconnected systems. Currently they use Excel macros that break when data formats change, causing stockouts that cost $10K+ per incident. If solved, they would reduce reconciliation time by 80% and prevent 90% of stockouts."

**Bad Example:**
> "We want to build an AI for supply chain optimization to help businesses work better."

**Exercise:**
Write problem statements for your top 2 use case ideas using the YC format. Test them:
- Is the user specific?
- Is the pain quantified?
- Is the benefit measurable?

---

## Required Reading

| Resource | Time | Why |
|----------|------|-----|
| [Y Combinator — How to Build a Great Series A Pitch](https://www.ycombinator.com/library/8d-how-to-build-a-great-series-a-pitch-and-deck) | ~20 min | The gold standard for problem statement framing |
| [Agility at Scale — AI Use Case Identification](https://agility-at-scale.com/ai/strategy/ai-use-case-identification-and-prioritization/) | ~15 min | Practical framework for enterprise use case prioritization |
| Your selected research reports from market-research/ | ~30 min | Build domain awareness |

---

## Required Videos

| Video | Speaker | Why |
|-------|---------|-----|
| [3 Ingredients for Reliable Enterprise Agents](https://www.youtube.com/watch?v=kTnfJszFxCg) | Harrison Chase (LangChain) | Use case scoping, how to qualify an agent problem |
| [Y Combinator — How to Pitch Your Startup](https://www.youtube.com/watch?v=17XZGUX_9iM) | YC Partners | Problem statement examples and common mistakes |

---

## Deliverables for This Week

By end of Week 2, you should have:

- [ ] Reviewed 3–5 market research reports from different industries
- [ ] Applied an evaluation framework to 2–3 potential use cases
- [ ] Written problem statements for your top 2 ideas in YC format
- [ ] Validated with at least 1 potential user (informal conversation counts)
- [ ] Documented why you selected your primary use case (and why you rejected others)

---

## The Core Test (Preview of Week 3)

Once you've identified your use case, you'll need to validate:

> **"Can I write a complete flowchart for this task before running it?"**
> - Yes → workflow (no agent needed)
> - No → agent

But first: make sure you're solving a problem worth solving.

---

## Next Week
→ [`../week-03-architecture/week-03-architecture.md`](../week-03-architecture/week-03-architecture.md) — Once you've validated your use case, learn when to use agents vs workflows and design the architecture.
