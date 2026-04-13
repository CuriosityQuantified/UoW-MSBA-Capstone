# Weeks 4-End — Code Development

**Goal:** Build production-capable agentic systems. Move from planning to evaluated, observable, deployable code.

> Rule: **Never run an agent without tracing.** Instrumentation isn't an afterthought — it's a prerequisite for debugging, cost control, and evaluation.

---

## This Week's Structure

Week 4 is where you transition from planning to building. This is a 6-week arc:
- **Weeks 4–5**: Single-agent fundamentals with observability baked in
- **Weeks 6–7**: Multi-agent, memory, and routing
- **Weeks 8–9**: Evaluation, cost guards, error handling
- **Week 10+**: Deployment / demo-ready

---

## Phase 1: Environment + Observability (Week 4 Days 1–2)

Before writing your first agent, set up your observability stack.

### Required Setup
- Python 3.11+
- OpenAI API key (or Anthropic, as preferred)
- Langfuse account (free tier is fine)

```bash
pip install langchain langchain-openai langfuse
```

### Required Reading
1. [Langfuse — AI Agent Observability Guide](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse) (~20 min)
2. [Langfuse — Get Started with Tracing](https://langfuse.com/docs/observability/get-started) (~15 min)
3. [LangChain — On Agent Frameworks and Observability](https://blog.langchain.com/on-agent-frameworks-and-agent-observability/) (~10 min)

### Hands-On: Run the Observability Examples
Work through these in order:

```
examples/observability/01_minimal_trace.py       ← start here
examples/observability/02_multi_step_agent.py
examples/observability/03_cost_guard.py
examples/observability/04_long_horizon_guard.py
```

→ See [`../../examples/README.md`](../../examples/README.md) for setup.

---

## Phase 2: First Agent Build (Week 4 Days 3–5, Week 5)

Build your first real agent with tracing integrated from the start.

### Recommended Learning Path

| Step | Resource | Platform | Time | Why |
|------|----------|----------|------|-----|
| 1 | [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) | DeepLearning.AI | 4–6h | First hands-on with LangGraph — tools, memory |
| 2 | [Introduction to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph) | LangChain Academy | 6–8h | Deeper: state, checkpointing, human-in-the-loop |
| 3 | [HuggingFace Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction) | HuggingFace | 15–20h | Framework-agnostic depth; earns a certificate |

### Build Targets
- Agent that takes user query + uses at least one tool
- Langfuse tracing enabled from day one
- Basic cost guard (max tokens or max cost)

---

## Phase 3: Advanced Topics (Weeks 6–7)

Move to multi-agent flows, persistent memory, and routing.

### Videos
| Video | Why |
|-------|-----|
| [Build Advanced AI Agent Systems](https://www.youtube.com/watch?v=1w5cCXlh7JQ) | Intermediate builds — tools, routing, memory |
| [LangChain + LangGraph Explained (2025)](https://www.youtube.com/watch?v=1ykcOVCQdkY) | Architecture deep dive |
| [Long-Term Memory in LangGraph](https://www.youtube.com/watch?v=R0OdB-p-ns4) | Harrison Chase — cross-session memory |
| [How Claude Code's Creator Starts Every Project](https://youtu.be/KWrsLqnB6vA) | Austin Marchese — 6 production workflows |
| [MiroFish AI Explained](https://www.youtube.com/watch?v=dbITcA6sRNo) | Swarm intelligence, orchestrator-workers |

---

## Phase 4: Hardening (Weeks 8–9)

Evaluation, cost guards, error handling, retry logic.

---

## Phase 5: Deployment (Week 10)

Demo-ready system.

---

## Capstone Milestones

| Week | Milestone |
|------|-----------|
| Week 4 | Agent scaffolding complete — tools defined, state designed, tracing on |
| Week 5 | First working end-to-end run |
| Week 6 | Multi-step or multi-agent flow working |
| Week 7 | Eval loop in place — agent scores its own outputs |
| Week 8 | Cost guards + error handling + retry logic |
| Week 9 | Performance optimization, edge cases |
| Week 10 | Deployed / demo-ready |

---

## Concept Docs

- [`concepts/code-development.md`](../../concepts/code-development.md) — Learning path, project scaffolding
- [`concepts/observability-tracing.md`](../../concepts/observability-tracing.md) — Traces, spans, cost guards
- [`concepts/progressive-disclosure.md`](../../concepts/progressive-disclosure.md) — Codebase organization
- [`concepts/continual-learning.md`](../../concepts/continual-learning.md) — How agents improve over time

## Agent Execution (New)

- [`agent-execution.md`](./agent-execution.md) — Sandboxes and streaming for secure, real-time agent execution (Deep Agents implementation)

---

## Claude Code Workflows

If using Claude Code for capstone development:

### The Golden Rule: Think Before Building
*From [OpinionAI on Claude Code workflow](https://substack.com/@opinionai/note/c-238928597)*

Most people use Claude Code too early and too fast. The better workflow is about **sequencing**, not just prompting:

1. **Ask for the plan first** — Make it think before it builds
2. **Define rules in `claude.md`** — Lock in constraints before execution
3. **Write the failing test** — Define "done" before implementing
4. **Then execute** — Only after the plan is clear

That one shift saves a lot of messy refactoring later.

### Six Key Strategies 

1. **Plan mode first** — `Shift+Tab` twice before every session
2. **Minimal `claude.md`** — Keep it under a few thousand tokens
3. **Verification loops** — Give Claude a tool to see its own output
4. **Parallel sessions** — Run multiple sessions on non-overlapping files
5. **Inner loops → slash commands** — Document anything you do twice
6. **Build for the future** — Focus on information architecture, not micro-prompts

---

## FAQ

- [`faq/README.md`](../../faq/README.md) — Common questions
- [`faq/framework-choices.md`](../../faq/framework-choices.md) — When to use what
- [`faq/common-errors.md`](../../faq/common-errors.md) — Debugging guide
