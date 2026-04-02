# Week 4 — Observability & Tracing

**Goal:** Instrument your agent before you run it at scale. Know what it's doing, what it's costing, and when it's going wrong.

> Rule: **Never run an agent in production without tracing.** An agent that runs unobserved is a liability, not an asset.

---

## Required Reading

1. [Langfuse — AI Agent Observability Guide](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse) (~20 min)
2. [Langfuse — Get Started with Tracing](https://langfuse.com/docs/observability/get-started) (~15 min)
3. [LangChain — On Agent Frameworks and Observability](https://blog.langchain.com/on-agent-frameworks-and-agent-observability/) (~10 min)

---

## Required Videos

| Video | Speaker | Why |
|-------|---------|-----|
| [Langfuse Intro — Observability & Tracing Deep Dive](https://www.youtube.com/watch?v=pTneXS_m1rk) | Langfuse (Marc, CEO) | Official product walkthrough, 11 min |
| [LangSmith 101 for AI Observability](https://www.youtube.com/watch?v=Iyc80hY2yYk) | James Briggs | LangSmith as an alternative if you're on the LangChain stack, 9 min |
| [Stop Confusing LangChain, LangGraph, and LangSmith](https://www.youtube.com/watch?v=e-GR3PlEOVU) | ByteMonk | How tracing fits the full stack, long-horizon concerns, 12 min |

---

## Concept Docs

- [`concepts/observability-tracing.md`](../concepts/observability-tracing.md) — Full deep dive: traces, spans, cost guards, Langfuse setup, long-horizon patterns

---

## Hands-On: Run the Examples

Work through these in order. Each builds on the previous.

```
examples/observability/01_minimal_trace.py       ← start here
examples/observability/02_multi_step_agent.py
examples/observability/03_cost_guard.py
examples/observability/04_long_horizon_guard.py
```

→ See [`examples/README.md`](../examples/README.md) for setup instructions and prereqs.

---

## What You Should Be Able to Do After This Week

- [ ] Add Langfuse tracing to any agent in <10 minutes
- [ ] Set a token budget / cost guard that stops the agent before it runs away
- [ ] Read a trace and identify which tool call took the longest
- [ ] Explain the difference between a trace, a span, and a generation

---

## Next Week
→ [`weeks-05-10-coding.md`](./weeks-05-10-coding.md) — You have the foundations. Now build.
