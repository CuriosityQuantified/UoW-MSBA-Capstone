# 04 — Architecture Development

## The 5 Core Architecture Decisions

Before writing a line of code, make these decisions explicitly. Changing them mid-build is expensive.

---

### Decision 1: Framework Selection

| Framework | When to choose it |
|-----------|-------------------|
| **Anthropic Claude Agent SDK** | General-purpose harness, coding tasks, high-autonomy, open-ended research |
| **LangGraph** | Production systems, stateful multi-step workflows, HITL, auditability |
| **CrewAI** | Rapid multi-agent prototyping, role-based agent teams |
| **AutoGen** | Conversational multi-agent patterns, back-and-forth agent dialogue |
| **Raw API** | Simple 1–2 step pipelines; avoid over-engineering |

**Default recommendation for new builders:**
- Learn on **LangGraph** (explicit, debuggable, closest to how production systems work)
- Graduate to **Claude Agent SDK** for high-autonomy tasks
- Avoid agent frameworks entirely for anything that fits a simple prompt chain

---

### Decision 2: State Design

State is what your agent remembers between steps. Design it before building nodes.

Questions to answer:
1. What data flows through the entire task? → Goes in global state
2. What does each step need from prior steps? → Must be in state
3. What triggers a human-in-the-loop checkpoint? → Add a `needs_review` flag
4. What gets written to long-term memory at the end? → Define your memory schema

```python
# LangGraph example state schema
from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    messages: Annotated[List, operator.add]   # conversation history
    task: str                                   # current goal
    tools_used: List[str]                       # audit trail
    needs_human_review: bool                    # HITL checkpoint flag
    final_output: str                           # result
```

---

### Decision 3: Tool Design

Rules for well-designed tools:
1. **One responsibility** — each tool does exactly one thing
2. **Explicit error handling** — return structured errors the agent can reason about
3. **Schema-first** — define the input/output schema before implementing
4. **MCP-ready** — design tools as if they'll eventually be MCP-compliant

```python
# Good: one responsibility, structured error return
def search_web(query: str) -> dict:
    """Search the web and return top results."""
    try:
        results = brave_search(query, count=5)
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e), "query": query}

# Bad: multiple responsibilities, no error handling
def do_research(topic: str) -> str:
    results = search(topic)
    summary = summarize(results)
    return summary
```

**MCP (Model Context Protocol)** is the emerging standard for connecting agents to tools. Learn the protocol early — it's becoming the default for production tool connectivity.
- Docs: https://modelcontextprotocol.io/introduction

---

### Decision 4: Memory Architecture

| Layer | What | When |
|-------|------|------|
| **In-context** | Entire current prompt window | Always available; expires at session end |
| **Working memory** | State passed between nodes | Lives for the duration of one task run |
| **External / Vector** | Embeddings in a vector DB (Chroma, Pinecone, Weaviate) | Persists across sessions; requires retrieval |
| **Structured store** | Key-value or SQL (Redis, Postgres) | Fast lookups; deterministic retrieval |
| **Episodic** | Logs of past agent runs | Retrieved by similarity; enables learning from history |

**Progressive Disclosure principle applied to memory:** Don't load all memory into context upfront. Use retrieval to pull only what's relevant to the current step. See [`06-progressive-disclosure.md`](./06-progressive-disclosure.md).

---

### Decision 5: Evaluation Strategy

Design this *before* you build. You cannot improve what you cannot measure.

| Level | What to measure | How |
|-------|----------------|-----|
| **Tool accuracy** | Did the agent call the right tool with the right args? | Log + inspect |
| **Task completion** | Did the agent complete the assigned task? | Pass/fail test cases |
| **Output quality** | Is the final output correct? | LLM-as-judge, rubric scoring |
| **Safety** | Did the agent attempt unsafe actions? | Guardrail checks |
| **Cost / latency** | Tokens used, time to complete | Monitoring |

---

## Required Reading — Week 3

| Resource | Time | Why |
|----------|------|-----|
| [LangGraph — Tutorials](https://langchain-ai.github.io/langgraph/tutorials/) | ~2h | Multi-agent, RAG, HITL worked examples |
| [Anthropic — MCP Introduction](https://modelcontextprotocol.io/introduction) | ~20 min | The standard for agent tool connectivity |
| [Anthropic — Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) | ~20 min | Tool search, dynamic discovery, orchestration |
| [Skills Files: Agent-First Design & Three-Tier Architecture](https://www.youtube.com/watch?v=0cVuMHaYEHE) | ~26 min | Skills as org infrastructure: description-as-routing, three-tier skill architecture, versioning |
| [LangGraph — Agentic RAG](https://docs.langchain.com/oss/python/langgraph/agentic-rag) | ~30 min | Worked architecture example |

## Video — Week 3

| Video | Why |
|-------|-----|
| [Harrison Chase — Long-Term Memory in LangGraph](https://www.youtube.com/watch?v=R0OdB-p-ns4) | Memory architecture patterns |
