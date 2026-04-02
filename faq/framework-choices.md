# Framework Choices — FAQ

---

## LangGraph vs. CrewAI vs. harness — which should I use?

**Short answer:** LangGraph for structured pipelines, harness (Claude Agent SDK / Claude Code) for open-ended tasks.

| Framework | Best for | Avoid when |
|-----------|----------|------------|
| **LangGraph** | Multi-step workflows with defined transitions, human-in-the-loop, production systems that need auditability | You don't yet know what steps your agent will take |
| **CrewAI** | Quick multi-agent prototypes with role-based agents | You need fine-grained control over state or routing |
| **Claude Agent SDK (harness)** | Open-ended tasks, research, coding, anything where the path isn't known in advance | You need strict auditability of every decision point |
| **Claude Code** | Building and iterating on the agent itself (meta-level) | You're running production workloads (it's a development tool) |

**The decision rule from [`concepts/agent-harness.md`](../concepts/agent-harness.md):**
> Can you write a complete flowchart before running the task?
> - Yes → LangGraph
> - No → harness

---

## Do I need LangChain if I'm using LangGraph?

No. LangGraph is a standalone library. You don't need LangChain LCEL or LangChain's chain abstractions to use LangGraph. Most new projects start directly with LangGraph.

LangSmith (observability) is also standalone from LangChain — it works with any agent framework.

---

## Should I use LangSmith or Langfuse for observability?

Both work well. The practical difference:

| | LangSmith | Langfuse |
|---|---|---|
| Best fit | Already on LangChain/LangGraph stack | Framework-agnostic; works with anything |
| Hosting | Cloud (LangChain managed) | Cloud or self-hosted |
| Free tier | Yes | Yes |
| UI | Strong eval + annotation features | Strong trace visualization |

**Recommendation for this course:** Langfuse, because it works regardless of what framework you end up choosing.

---

## Is LangGraph overkill for a capstone project?

Probably not. LangGraph's main value is checkpointing (resumable runs) and explicit state management. Even for a capstone-scale project, knowing where your agent is and being able to restart mid-run without re-running expensive steps is worth the setup cost.

That said: if your capstone is a single-agent, open-ended research or coding task, a harness is faster to get working.

---

## What's the difference between a tool and an MCP server?

A **tool** is a function your agent can call — defined inline in your code. An **MCP server** is a standardized server that exposes tools over a network protocol (Model Context Protocol). The agent connects to it like a plugin.

Practical difference: tools are for capabilities you own and control. MCP is for connecting to external systems (databases, APIs, other services) in a standardized, reusable way.

→ See [MCP Introduction](https://modelcontextprotocol.io/introduction) for the full picture.
