# Week 4 — Coding Foundations + Observability

**Goal:** Start building with code. Write your first agent loop, instrument it with tracing from day one, and establish the observability patterns you'll use throughout development.

> Rule: **Never run an agent without tracing.** Instrumentation isn't an afterthought — it's a prerequisite for debugging, cost control, and evaluation.

---

## This Week's Structure

Week 4 is where you transition from planning to building. You'll:
1. Set up your development environment
2. Write your first instrumented agent
3. Learn the observability patterns that will save you hours of debugging

---

## Part 1: Environment Setup (Day 1)

### Required Setup
- Python 3.11+
- OpenAI API key (or Anthropic, as preferred)
- Langfuse account (free tier is fine)

### Install Dependencies
```bash
pip install langchain langchain-openai langfuse
```

---

## Part 2: Observability First (Days 1–2)

Before writing your first agent, understand how to watch it work.

### Required Reading
1. [Langfuse — AI Agent Observability Guide](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse) (~20 min)
2. [Langfuse — Get Started with Tracing](https://langfuse.com/docs/observability/get-started) (~15 min)
3. [LangChain — On Agent Frameworks and Observability](https://blog.langchain.com/on-agent-frameworks-and-agent-observability/) (~10 min)

### Required Videos
| Video | Speaker | Why |
|-------|---------|-----|
| [Langfuse Intro — Observability & Tracing Deep Dive](https://www.youtube.com/watch?v=pTneXS_m1rk) | Langfuse (Marc, CEO) | Official product walkthrough, 11 min |
| [LangSmith 101 for AI Observability](https://www.youtube.com/watch?v=Iyc80hY2yYk) | James Briggs | Alternative if on LangChain stack, 9 min |

### Hands-On: Run the Observability Examples
Work through these in order. Each builds on the previous.

```
examples/observability/01_minimal_trace.py       ← start here
examples/observability/02_multi_step_agent.py
examples/observability/03_cost_guard.py
examples/observability/04_long_horizon_guard.py
```

→ See [`examples/README.md`](../examples/README.md) for setup instructions.

---

## Part 3: First Agent Build (Days 3–5)

Now build something real with tracing integrated from the start.

### Recommended Course
| Resource | Platform | Time |
|----------|----------|------|
| [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) | DeepLearning.AI | 4–6h |

### What to Build This Week
A minimal agent that:
- Takes a user query
- Uses at least one tool
- Logs traces to Langfuse
- Has a basic cost guard (max tokens or max cost)

### Code Checklist
- [ ] Agent can receive input and produce output
- [ ] At least one tool integrated
- [ ] Langfuse tracing enabled
- [ ] Cost guard configured (token or dollar limit)
- [ ] Can read a trace and identify what the agent did step-by-step

---

## Concept Docs

- [`concepts/code-development.md`](../concepts/code-development.md) — Full learning path, project scaffolding
- [`concepts/observability-tracing.md`](../concepts/observability-tracing.md) — Deep dive on traces, spans, cost guards
- [`concepts/progressive-disclosure.md`](../concepts/progressive-disclosure.md) — How to structure your codebase as it grows

---

## What You Should Be Able to Do After This Week

- [ ] Set up a new agent project with tracing in <10 minutes
- [ ] Add Langfuse to any agent and see traces in the dashboard
- [ ] Set a token/cost budget that stops the agent before it runs away
- [ ] Read a trace and identify which step took longest / cost most
- [ ] Explain the difference between a trace, a span, and a generation
- [ ] Build a simple tool-using agent with observability baked in

---

## Next Week
→ [`week-05-advanced-coding.md`](./week-05-advanced-coding.md) — Multi-agent, memory, and evaluation.
