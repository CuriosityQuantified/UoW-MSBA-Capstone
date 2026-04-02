# 01 — What Is a Modern Agent?

## The Core Definition

An AI agent is a system where a language model **perceives input, reasons about what to do, takes action, observes the result, and repeats** — autonomously, until a goal is reached or a human intervenes.

The key distinction from a plain LLM call: **the agent controls its own execution loop.**

---

## Components of a Modern Agent

Every production agent is built from the same component stack:

### 1. LLM (Reasoning Core)
The model that perceives input, reasons through a plan, and decides the next action. Not just for generation — it drives the entire control loop. The LLM doesn't just produce text; it decides *what to do next*.

### 2. Tools
Functions the LLM can invoke to act on the world:
- **MCP (Model Context Protocol)** — the emerging open standard; tools declared as schemas, the model calls them by name
- **Custom** — any function you expose: APIs, databases, internal services
- **Built-in** — web search, code execution, file I/O, subprocess calls

### 3. Prompts (Three Layers)
Not just "the system prompt." A structured agent has:
- **Core agent prompt** — defines identity, behavior, and constraints
- **Workflow prompts** — per-task instructions injected at runtime
- **Skills & custom prompts** — skill-specific instructions loaded on demand (see [Progressive Disclosure](./progressive-disclosure.md))

### 4. Skills / Skill Files
A self-contained capability bundle: a SKILL.md (instructions), optional scripts, and tool definitions. The agent loads skill instructions *on demand* — not all upfront. This is progressive disclosure in practice.

### 5. Memory
| Type | Description | Persistence |
|------|-------------|-------------|
| **In-context** | Everything in the current prompt window | Expires at session end |
| **External / Long-term** | Vector DB, structured store, files | Persists across sessions |
| **Episodic** | Logs of past runs the agent can retrieve and reason about | Queryable |

### 6. The Agent Loop
The core execution cycle:

```
Perceive → Think → Act → Observe → (repeat)
```

This loop may be:
- **Explicit** (LangGraph): developer-defined nodes and edges control every transition
- **Implicit** (harness): the harness manages the loop; the LLM decides next steps autonomously

### 7. Subagents & Orchestration
Complex tasks spawn child agents. The orchestrator decomposes work; subagents execute specialized subtasks — potentially in parallel — each with their own tools, memory, and loops.

### 8. Hooks & Lifecycle Events
Injection points in the loop where custom logic fires:
- `pre-tool` / `post-tool` — intercept before/after every tool call
- `on-error` — catch failed tool calls, trigger recovery
- `on-complete` — signal task done, trigger downstream actions

Used for: logging, safety checks, human-in-the-loop approval, audit trails.

---

## The Three Agent Paradigms

### Type 1 — General-Purpose Harness Agent
*Examples: Claude Code, OpenAI Codex, Gemini CLI, Claude Agent SDK*

The LLM is the agent loop. Given a system prompt and tools, it reasons into sequential tool calls with no explicit graph. The "harness" provides scaffolding: system prompt management, tool definitions, context tracking, loop control.

**Best for:** open-ended tasks, coding, research, anything requiring high autonomy.

### Type 2 — Graph / Node-Based Orchestration
*Examples: LangGraph, CrewAI, LangChain LCEL*

The developer defines an explicit state machine: nodes (LLM calls or functions) + edges (routing logic). LLM decision-making is embedded inside nodes; overall flow is deterministic and auditable.

**Best for:** production systems, multi-step pipelines, human-in-the-loop workflows, enterprise auditability.

### Type 3 — Multi-Agent Systems
An orchestrator agent delegates tasks to specialized subagents. Each subagent has its own tools, memory, and loop. The orchestrator synthesizes results.

**Best for:** complex tasks requiring parallelism, specialization, or independent verification.

---

## Required Reading — Week 1

| Resource | Time | Why |
|----------|------|-----|
| [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) | ~30 min | Primary text for the entire course. The definitive production guide. |
| [HuggingFace — What Is an Agent? (Unit 1)](https://huggingface.co/learn/agents-course/unit1/introduction) | ~45 min | Clean conceptual intro, framework-agnostic. |
| [Anthropic — Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | ~20 min | How harness-based agents work in practice. |
| [LangGraph — Concepts Overview](https://langchain-ai.github.io/langgraph/concepts/) | Reference | The vocabulary of graph-based agents. |

## Videos — Week 1

| Video | Why |
|-------|-----|
| [Harrison Chase — Interrupt 2025 Keynote](https://www.youtube.com/watch?v=DrygcOI-kG8) | State of agents + LangGraph direction |
| [Harrison Chase — Building Reliable Agents (Amsterdam)](https://www.youtube.com/watch?v=DSdyqPzdlQU) | Enterprise patterns, production realities |
| [Skills Files: Agent-First Design & Three-Tier Architecture](https://www.youtube.com/watch?v=0cVuMHaYEHE) | Nate B Jones — skills as org infrastructure, description-as-routing, versioning |
