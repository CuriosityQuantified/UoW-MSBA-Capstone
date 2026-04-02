# Week 2 — Use Case Identification

**Goal:** Learn to recognize when a problem actually needs an agent — and when it doesn't.

The most expensive mistake in agentic development is building an agent for a task that a prompt chain or simple API call would handle in 1/10th the time and cost.

---

## Required Reading

1. Re-read [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — this time focus on the **5 patterns** section
2. [AI Agentic Design Patterns](https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/) — Andrew Ng / DeepLearning.AI (~15 min)

---

## Required Videos

| Video | Speaker | Why |
|-------|---------|-----|
| [3 Ingredients for Reliable Enterprise Agents](https://www.youtube.com/watch?v=kTnfJszFxCg) | Harrison Chase (LangChain) | Use case scoping, how to qualify an agent problem |

---

## Concept Docs

- [`concepts/use-case-identification.md`](../concepts/use-case-identification.md) — The 5 patterns, the decision framework, common failure modes

---

## The Core Test

> **"Can I write a complete flowchart for this task before running it?"**
> - Yes → workflow (no agent needed)
> - No → agent

Apply this test to your capstone project idea this week.

---

## Exercise

Take your capstone project idea and answer:
1. What is the sequence of steps? Is it knowable in advance?
2. Which of Anthropic's 5 patterns does it most resemble?
3. What would break if you tried to implement it as a fixed pipeline instead?

---

## Next Week
→ [`week-03-architecture.md`](./week-03-architecture.md) — Once you've validated your use case, design the architecture.
