# Week 3 — Architecture Development

**Goal:** Choose your framework, design your state, and plan your tool/memory structure before writing code.

A week spent on architecture saves three weeks of refactoring. The decisions you make here — framework, state shape, memory type — are expensive to change later.

---

## Required Reading

1. [LangGraph — Concepts Overview](https://langchain-ai.github.io/langgraph/concepts/) — Reference
2. [MCP — Introduction](https://modelcontextprotocol.io/introduction) (~15 min)
3. [Anthropic — Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) (~20 min)

---

## Required Videos

| Video | Speaker | Why |
|-------|---------|-----|
| [Skills Files: Agent-First Design & Three-Tier Architecture](https://www.youtube.com/watch?v=0cVuMHaYEHE) | Nate B Jones | How skills/tools should be organized for agent-readable architecture |
| [Long-Term Memory in LangGraph](https://www.youtube.com/watch?v=R0OdB-p-ns4) | Harrison Chase (LangChain) | Memory architecture patterns — cross-session state |

---

## Concept Docs

- [`concepts/architecture-development.md`](../concepts/architecture-development.md) — Framework selection, state design, tool patterns, memory types, eval
- [`concepts/progressive-disclosure.md`](../concepts/progressive-disclosure.md) — Why you should NOT front-load all tools/context into the system prompt

---

## Framework Decision

| If your task is... | Use... |
|---|---|
| Open-ended, high autonomy, unknown steps | Harness (Claude Agent SDK, Claude Code) |
| Structured pipeline, needs auditability | LangGraph |
| Multi-step with human-in-the-loop checkpoints | LangGraph |
| Rapid prototype / research task | Harness |

→ See [`faq/framework-choices.md`](../faq/framework-choices.md) for a fuller breakdown.

---

## Architecture Checklist

Before coding, answer these:
- [ ] Harness or graph? Why?
- [ ] What is my state shape? (what data persists across steps?)
- [ ] What tools does my agent need? List them.
- [ ] What type of memory? (in-context only / external store / episodic logs?)
- [ ] How will I verify the agent did the right thing? (eval plan)

---

## Next Week
→ [`week-04-coding-foundations.md`](./week-04-coding-foundations.md) — Start coding. Instrument first, build second.
