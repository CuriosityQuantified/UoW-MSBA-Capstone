# 03 — Use Case Identification

## The Core Question

> **"Can I write a complete flowchart for this task before running it?"**
> - Yes → **workflow** (deterministic pipeline, no agent needed)
> - No → **agent** (the sequence of steps must be discovered at runtime)

This is the single most important decision in agentic development. Agents add cost, latency, and unpredictability. Use them only when the task genuinely requires autonomous decision-making.

---

## When to Use an Agent

| Signal | Meaning |
|--------|---------|
| The sequence of steps is unknown in advance | Agent must plan dynamically |
| The task requires self-correction or reflection | Agent must evaluate its own outputs |
| Multiple tools must be combined dynamically | Fixed pipeline can't anticipate the combination |
| The problem is too ambiguous for a fixed workflow | Need the LLM to resolve ambiguity at runtime |
| Failure modes are diverse and unpredictable | Agent must handle novel error conditions |

## When NOT to Use an Agent

| Signal | Better approach |
|--------|----------------|
| The execution path is fully predictable | Prompt chaining or fixed pipeline |
| Latency and cost are critical | Deterministic workflow |
| Auditability requires human-defined steps | LangGraph workflow with explicit edges |
| The task is a single LLM call | Just call the API |

---

## Anthropic's 5 Agentic Patterns

From [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — these are the building blocks of every agentic system:

### 1. Prompt Chaining
Sequential LLM calls, each building on the previous output.
- Use when: a complex task can be decomposed into discrete, predictable sequential steps
- Trade-off: each step adds latency; errors compound

### 2. Routing
An LLM classifies input and directs it to the right sub-pipeline.
- Use when: different types of inputs need fundamentally different handling
- Example: a customer service agent routes billing → billing LLM, technical → tech LLM

### 3. Parallelization
Multiple LLM calls run simultaneously; outputs are aggregated.
- Use when: subtasks are independent and can be parallelized for speed
- Example: analyzing 5 documents simultaneously, then synthesizing

### 4. Orchestrator-Workers
One LLM breaks down the task and delegates to worker LLMs.
- Use when: the task has complex, variable subtasks that benefit from specialization
- This is the multi-agent pattern

### 5. Evaluator-Optimizer
One LLM generates, another evaluates. Loop until the output meets a threshold.
- Use when: output quality is hard to achieve in one pass (e.g., code that must pass tests, writing that must hit a rubric)

---

## Andrew Ng's 4 Agentic Design Patterns

From [AI Agentic Design Patterns](https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/):

| Pattern | Description |
|---------|-------------|
| **Reflection** | The agent critiques and revises its own outputs iteratively |
| **Tool Use** | The agent calls external tools (search, code execution, APIs) |
| **Planning** | The agent decomposes a goal into a sequence of steps before acting |
| **Multi-Agent** | Multiple agents with different roles collaborate or compete |

---

## Required Reading — Week 2

| Resource | Time | Why |
|----------|------|-----|
| [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) | Re-read | Focus on "When to use agents" and the 5 patterns |
| [Andrew Ng — AI Agentic Design Patterns](https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/) | ~15 min | The 4 canonical design patterns |
| [LangChain — Workflows vs. Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) | ~10 min | Practical decision guide |

## Video — Week 2

| Video | Why |
|-------|-----|
| [Harrison Chase — 3 Ingredients for Reliable Enterprise Agents](https://www.youtube.com/watch?v=kTnfJszFxCg) | Use case scoping + production realities |
