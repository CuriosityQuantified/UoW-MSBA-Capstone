# Continual Learning for AI Agents

*Source: [LangChain Blog](https://blog.langchain.com/continual-learning-for-ai-agents/)*

Most discussions of continual learning in AI focus on one thing: updating model weights. But for AI agents, learning can happen at three distinct layers: **the model**, **the harness**, and **the context**. Understanding the difference changes how you think about building systems that improve over time.

---

## The Three Layers of Agentic Systems

### 1. Model
The model weights themselves.

### 2. Harness
The harness around the model that powers all instances of the agent. This refers to the code that drives the agent, as well as any instructions or tools that are always part of the harness.

### 3. Context
Additional context (instructions, skills) that lives outside the harness, and can be used to configure it.

#### Examples

**Coding agent like Claude Code:**
- Model: claude-sonnet, etc
- Harness: Claude Code
- User context: CLAUDE.md, /skills, mcp.json

**OpenClaw:**
- Model: many
- Harness: Pi + other scaffolding
- Agent context: SOUL.md, skills from clawhub

---

## Continual Learning at the Model Layer

When most people talk about continual learning, this is what they most commonly refer to: updating the model weights.

### Techniques
- **SFT** (Supervised Fine-Tuning)
- **RL** (Reinforcement Learning), e.g., GRPO

### Challenge: Catastrophic Forgetting
When a model is updated on new data or tasks, it tends to degrade on things it previously knew. This is an open research problem.

### Practical Application
When people train models for a specific agentic system (e.g., OpenAI codex models for their Codex agent), they largely do this for the agentic system as a whole. In theory, you could do this at a more granular level (e.g., a LORA per user), but in practice this is mostly done at the agent level.

---

## Continual Learning at the Harness Layer

The harness refers to the code that drives the agent, as well as any instructions or tools that are always part of the harness.

### Meta-Harness: End-to-End Optimization
A recent paper, [Meta-Harness](https://yoonholee.com/meta-harness/), describes how to optimize harnesses:

1. Run the agent in a loop over many tasks
2. Evaluate the results
3. Store all logs into a filesystem
4. Run a coding agent to analyze these traces and suggest changes to the harness code

Similar to continual learning for models, this is usually done at the agent level. You could in theory do this at a more granular level (e.g., learn a different code harness per user).

---

## Continual Learning at the Context Layer

"Context" sits outside the harness and can be used to configure it. Context consists of things like instructions, skills, even tools. This is also commonly referred to as **memory**.

### Levels of Context Learning

#### Agent Level
The agent has a persistent "memory" and updates its own configuration over time. Example: OpenClaw maintains its own [SOUL.md](https://docs.openclaw.ai/concepts/soul) that gets updated over time.

#### Tenant Level (User, Org, Team)
Each tenant gets their own context that is updated over time:
- [Hex's Context Studio](https://hex.tech/product/context-studio/)
- [Decagon's Duet](https://decagon.ai/blog/introducing-duet)
- [Sierra's Explorer](https://sierra.ai/blog/explorer)

#### Mixed Approach
You can have agent-level context updates, user-level context updates, AND org-level context updates simultaneously.

### Update Mechanisms

**Offline Job (After the Fact)**
Similar to harness updates — run over recent traces to extract insights and update context. OpenClaw calls this ["dreaming"](https://docs.openclaw.ai/concepts/memory-dreaming).

**Hot Path (During Execution)**
The agent can decide to (or the user can prompt it to) update its memory as it works on the core task.

**Explicit vs. Implicit**
Another dimension: Is the user prompting the agent to remember, or is the agent remembering based on core instructions in the harness itself?

---

## Comparison: Three Layers of Learning

| Aspect | Model Layer | Harness Layer | Context Layer |
|--------|-------------|---------------|---------------|
| **What** | Model weights | Code, instructions, tools | Instructions, skills, memory |
| **Granularity** | Usually agent-level | Usually agent-level | Agent, user, org, or mixed |
| **Update freq** | Expensive, infrequent | Medium | Flexible, frequent |
| **Techniques** | SFT, RL, LoRA | Meta-harness, trace analysis | Dreaming, hot-path updates |
| **Key challenge** | Catastrophic forgetting | Trace quality | Memory management |

---

## Traces: The Foundation of All Learning

All of these flows are powered by **traces** — the full execution path of what an agent did. [LangSmith](https://docs.langchain.com/langsmith/home) helps collect traces.

### Using Traces for Different Learning Types

**Model Updates**
Collect traces and work with providers like [Prime Intellect](https://www.primeintellect.ai/) to train your own model.

**Harness Improvements**
Use [LangSmith CLI](https://docs.langchain.com/langsmith/langsmith-cli) and [LangSmith Skills](https://github.com/langchain-ai/langsmith-skills) to give a coding agent access to traces. This pattern was used to improve [Deep Agents](https://github.com/langchain-ai/deepagents) on terminal bench.

**Context Learning**
The agent harness needs to support this. Deep Agents provides production-ready support for:
- [User-scoped memory](https://docs.langchain.com/oss/python/deepagents/memory#user-scoped-memory)
- [Background consolidation](https://docs.langchain.com/oss/python/deepagents/memory#background-consolidation)
- And more memory patterns

---

## Key Takeaways

1. **Learning happens at three layers**, not just model weights
2. **Context layer learning** is the most flexible and frequently updated
3. **Traces are foundational** — you need observability to improve anything
4. **Consider mixed approaches** — agent-level + user-level + org-level updates can coexist
5. **Choose the right layer** for the right problem: model for fundamental capability, harness for system behavior, context for personalization

---

**Related Topics**

- [agent-harness.md](./agent-harness.md) — Understanding the harness concept
- [observability-tracing.md](./observability-tracing.md) — Traces and observability foundations
- [continual-learning.md](./continual-learning.md) — How agents learn at model, harness, and context layers
