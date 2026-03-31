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

---

## Art of the Possible

> These are real, working agentic systems — not demos, not prototypes. Study them to calibrate what's actually achievable with today's tools.

The gap between "agent tutorial" and "production agent system" is enormous. The examples below show what the frontier looks like so you can aim higher in your capstone.

---

### 🐟 MiroFish — Swarm Intelligence Prediction Engine

**GitHub:** [CuriosityQuantified/MiroFish](https://github.com/CuriosityQuantified/MiroFish)

MiroFish is a multi-agent swarm simulation engine that predicts how the world reacts to events — before they happen. Feed it a news article, policy draft, or financial report, and it constructs a high-fidelity digital world populated by AI agents with independent personalities, long-term memory, and behavioral logic. Those agents interact, evolve, and generate emergent patterns. The output: a prediction report.

**Why it matters for this course:**
- Demonstrates the orchestrator-workers pattern at scale (1M+ agents)
- Shows how knowledge graphs (Graphiti + Kuzu) replace static RAG for agent memory
- Illustrates emergence: system-level behavior that no single agent was programmed to produce
- End-to-end example of seed data → agent personas → simulation → prediction report

**Architecture at a glance:**
```
Seed Data (news / policy / report)
        ↓
Knowledge Graph (Graphiti + Kuzu)     ← embedded, no external services
        ↓
Agent Profile Generation              ← personas derived from graph entities
        ↓
OASIS Simulation (CAMEL-AI)           ← Twitter + Reddit social platforms
        ↓
Emergent Pattern Analysis
        ↓
Prediction Report
```

**Use cases it covers:**
- Predict public opinion shifts before a product launch
- Simulate information spread across social networks
- Stress-test strategic decisions against thousands of simulated human reactions
- Generate prediction reports for novel narrative scenarios

**Watch first (6 min):** [MiroFish AI Explained: The Multi-Agent Engine Simulating the Future](https://www.youtube.com/watch?v=dbITcA6sRNo) — Moses Samuel

---

### What to Notice When Studying These Systems

When you look at a production agentic system, ask:

| Question | What it reveals |
|----------|----------------|
| What is the seed input? | The problem scope the agent is designed for |
| How is memory handled? | Whether agents can reason across time and context |
| What triggers a new agent spawn? | The orchestration logic |
| How does the system output its result? | The contract between the agent system and its users |
| Where could this fail? | The engineering investment required for reliability |

Calibrate your capstone against these examples. You don't need 1M agents — but you should be able to articulate what your system does, why it needs agents (not just prompts), and what emergent capability it produces.
