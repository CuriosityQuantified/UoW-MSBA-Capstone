# 🤖 Agentic Applications — UW MSBA Capstone

**Curated by Nicholas Pate — AI Strategy & Engineering**

A structured guide for building production-grade agentic AI applications. Covers first principles, architecture, observability, development methodology, and a week-by-week resource curriculum.

---

## 🚀 First 30 Minutes

New here? Do these three things:

1. **Read** [`concepts/agent-overview.md`](./concepts/agent-overview.md) — the mental model (~15 min)
2. **Watch** [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic's definitive guide (~30 min)
3. **Run** [`examples/observability/01_minimal_trace.py`](./examples/observability/01_minimal_trace.py) — your first instrumented agent call

---

## 📅 Weekly Curriculum

Follow the weekly guides in order. Each links to the right concepts, readings, and exercises for that week.

| Week | Guide | Topic |
|------|-------|-------|
| **Week 1** | [`curriculum/week-01-foundations.md`](./curriculum/week-01-foundations.md) | What agents are, taxonomy, the agent loop |
| **Week 2** | [`curriculum/week-02-use-cases.md`](./curriculum/week-02-use-cases.md) | When to use agents, Anthropic's 5 patterns, feasibility |
| **Week 3** | [`curriculum/week-03-architecture.md`](./curriculum/week-03-architecture.md) | Framework selection, state design, orchestration |
| **Week 4** | [`curriculum/week-04-coding.md`](./curriculum/week-04-coding.md) | Coding starts: build agent with observability integrated |

---

## 📚 Concepts (Deep Reference)

Core concepts — read when the weekly curriculum sends you here, or when you need to go deeper.

| File | What it covers |
|------|---------------|
| [`concepts/agent-overview.md`](./concepts/agent-overview.md) | What is a modern agent? Components, taxonomy, the agent loop |
| [`concepts/agent-harness.md`](./concepts/agent-harness.md) | What is an agent harness? Harness vs. graph-based agents |
| [`concepts/use-case-identification.md`](./concepts/use-case-identification.md) | When to use agents, the 5 agentic patterns, Andrew Ng's 4 design patterns |
| [`concepts/architecture-development.md`](./concepts/architecture-development.md) | Framework selection, state, tools, memory, eval |
| [`concepts/progressive-disclosure.md`](./concepts/progressive-disclosure.md) | Development methodology: progressive disclosure |
| [`concepts/code-development.md`](./concepts/code-development.md) | Structured learning path (foundation → intermediate → capstone) |
| [`concepts/observability-tracing.md`](./concepts/observability-tracing.md) | Tracing, cost guards, Langfuse setup, long-horizon patterns |
| [`concepts/continual-learning.md`](./concepts/continual-learning.md) | How agents learn: model layer, harness layer, context layer updates |

---

## 🔗 Resources

| File | What it covers |
|------|---------------|
| [`resources/RESOURCES.md`](./resources/RESOURCES.md) | All links: readings, docs, courses, videos — organized by week |
| [`resources/data-sources.md`](./resources/data-sources.md) | 80+ curated datasets across government, financial, healthcare, NLP, academic |

---

## 💻 Examples

Runnable code you can execute locally. See [`examples/README.md`](./examples/README.md) for setup and order.

| Folder | What it contains |
|--------|-----------------|
| [`examples/observability/`](./examples/observability/) | 4 Python scripts: minimal trace → cost guard → multi-agent → long-horizon |

---

## ❓ FAQ

Common questions answered in one place. If you have a question, check here first.

| File | Questions answered |
|------|-------------------|
| [`faq/README.md`](./faq/README.md) | Index of all FAQ topics |
| [`faq/common-errors.md`](./faq/common-errors.md) | Setup errors, API issues, tracing not working |
| [`faq/framework-choices.md`](./faq/framework-choices.md) | LangGraph vs CrewAI vs harness — when to use what |

---

## 🗺️ Assets

- [`assets/agent-harness-sdk-diagram.png`](./assets/agent-harness-sdk-diagram.png) — Claude Agent SDK architecture (Thariq Shihipar, Anthropic)

---

*All external links are free and publicly available. Questions? See [`faq/`](./faq/) or open an issue.*
