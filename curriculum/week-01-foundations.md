# Week 1 — Foundations: What Is an Agent?

**Goal:** Build the mental model before writing a single line of code.

By end of week you should be able to: define an agent, distinguish between harness-based and graph-based agents, and explain why the agent loop matters.

---

## Required Reading (do in this order)

1. [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (~30 min)
   → This is the primary text for the entire course. Read it once now, you'll return to it each week.

2. [HuggingFace — What Is an Agent? (Unit 1)](https://huggingface.co/learn/agents-course/unit1/introduction) (~45 min)
   → Framework-agnostic conceptual intro. Covers the agent loop cleanly.

3. [Anthropic — Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (~20 min)
   → How harness-based agents work in practice. Read after #1 and #2.

---

## Required Videos

| Video | Speaker | Why |
|-------|---------|-----|
| [Claude Agent SDK Full Workshop](https://www.youtube.com/watch?v=TqC1qOfiVcQ) | Thariq Shihipar (Anthropic) | Harness architecture — watch the 6:01 diagram section closely |
| [Interrupt 2025 Keynote](https://www.youtube.com/watch?v=DrygcOI-kG8) | Harrison Chase (LangChain) | State of agents in 2025 + LangGraph direction |
| [Building Reliable Agents (Amsterdam)](https://www.youtube.com/watch?v=DSdyqPzdlQU) | Harrison Chase (LangChain) | Enterprise patterns, production realities |
| [Skills Files: Agent-First Design & Three-Tier Architecture](https://www.youtube.com/watch?v=0cVuMHaYEHE) | Nate B Jones | Skills as organizational infrastructure, description-as-routing signal |

---

## Concept Docs

- [`concepts/agent-overview.md`](../concepts/agent-overview.md) — Components, taxonomy, the 3 agent paradigms
- [`concepts/agent-harness.md`](../concepts/agent-harness.md) — What the harness provides, harness vs. graph decision rule

---

## Discussion Questions

1. What is the difference between a workflow and an agent? When does each make sense?
2. What does the harness provide that a raw API call doesn't?
3. Look at the Claude Agent SDK diagram in the workshop video (6:01). What would you have to build yourself if you weren't using a harness?

---

## Next Week
→ [`week-02-use-cases.md`](./week-02-use-cases.md) — Now that you know what agents are, learn when to use them.
