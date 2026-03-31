# 05 — Code Development (Weeks 4–10)

## Structured Learning Path

Build in layers. Each week adds one new capability on top of what exists. Never build complexity you haven't earned.

---

## Foundation — Weeks 4–5

### 🎓 DeepLearning.AI — AI Agents in LangGraph *(free)*
**The best hands-on entry point.** Builds an agent from scratch in Python, then migrates to LangGraph. You see exactly what the framework is abstracting.
→ https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/

**What you'll build:** A ReAct agent from scratch → LangGraph state machine → persistence → human-in-the-loop

### 🎓 LangChain Academy — Introduction to LangGraph *(free, self-paced)*
Official LangChain curriculum. State, nodes, edges, memory — builds a real email assistant workflow end-to-end.
→ https://academy.langchain.com/courses/intro-to-langgraph

**What you'll build:** A stateful email workflow with routing, tool use, and memory

---

## Intermediate — Weeks 6–7

### 🎓 Hugging Face Agents Course — Full 4 Units *(free, certification available)*
Framework-agnostic → hands-on. Covers fundamentals, then deploys agents on HF Spaces. Certification track available for portfolios.
→ https://huggingface.co/learn/agents-course/en/unit0/introduction

**What you'll build:** Tool-using agents, multi-agent systems, deployment to HF Spaces

### 🎥 LangGraph Tutorial — Build Advanced AI Agent Systems
Intermediate-level walkthrough of multi-agent patterns in LangGraph.
→ https://www.youtube.com/watch?v=1w5cCXlh7JQ

### 🎥 LangChain + LangGraph Explained (2025)
Architecture deep dive — how the pieces fit together.
→ https://www.youtube.com/watch?v=1ykcOVCQdkY

---

## Advanced / Capstone Build — Weeks 8–10

### What to build
A production-ready agentic application that demonstrates the full lifecycle:
1. **Use case** — a real problem with genuine agent-appropriate complexity
2. **Architecture** — explicit state design, tool schemas, memory layer
3. **Code** — LangGraph or Claude Agent SDK, with evaluation
4. **Deployment** — runnable demo (local or HF Spaces / API endpoint)

### Capability checklist before calling it done
- [ ] Agent completes the core task end-to-end without human guidance
- [ ] At least 2 distinct tools the agent selects dynamically
- [ ] Memory: agent uses context from prior steps
- [ ] Error handling: agent recovers from at least one failure mode
- [ ] Evaluation: at least 5 test cases with pass/fail results documented

### Reference resources
| Resource | Why |
|----------|-----|
| [Agentic AI for Beginners — LangGraph walkthrough](https://www.youtube.com/watch?v=CnXdddeZ4tQ) | End-to-end build reference |
| [LangGraph Full Docs](https://langchain-ai.github.io/langgraph/) | Complete API reference |
| [Anthropic Claude API — Agents + Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/agents) | SDK reference |
| [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) | Return to this regularly |

---

## Week-by-Week Summary

| Week | Focus | Deliverable |
|------|-------|-------------|
| 4 | Basics: tools, state, loop | Single-tool agent running locally |
| 5 | Multi-step state machines | 3-node LangGraph workflow |
| 6 | Memory + retrieval | Agent with external memory store |
| 7 | Multi-agent patterns | Orchestrator + 2 specialized subagents |
| 8 | Evaluation + safety | Test suite with documented results |
| 9 | Deployment | Running demo endpoint |
| 10 | Polish + presentation | Final capstone demo |
