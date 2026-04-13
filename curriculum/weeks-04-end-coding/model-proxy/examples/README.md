# Agent Examples

Four patterns for incorporating the course model proxy into your project. Each file has a reusable function at the top — copy what you need and build on it.

All examples route through `https://model-proxy.curiosityquantified.com` using your semester token. Set up your `.env` before running:

```bash
PROXY_AUTH_TOKEN=<your-semester-token>   # from instructor
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com
```

---

## Examples

| File | Pattern | Key function | Best for |
|------|---------|-------------|----------|
| `01_langchain_agent.py` | `langgraph.prebuilt.create_react_agent` | `create_agent(tools, system)` | Fastest start — one call, batteries included |
| `02_langgraph_agent.py` | Manual `StateGraph` | `create_graph(tools, system)` | Custom routing, HITL, complex state |
| `03_tool_use.py` | Native Anthropic loop | `run_with_tools(messages, tools, handlers)` | Full control, no framework overhead |
| `04_structured_output.py` | Pydantic extraction | `extract(text, Schema)` | Parsing documents, normalizing data |

---

## Install dependencies

```bash
# All examples
pip install anthropic langchain langchain-anthropic langgraph langfuse pydantic python-dotenv

# Or per-example (see the header comment in each file)
```

---

## Which pattern should I use?

**`create_react_agent`** (`01`) — Fastest starting point. One call returns a compiled graph with the full ReAct loop built in. Uses `langgraph.prebuilt.create_react_agent` — the current recommended pattern, replacing the old `langchain.agents.create_react_agent + AgentExecutor`.

**LangGraph** (`02`) — Preferred for anything you'll ship. Explicit state machine, built-in checkpointing, natural human-in-the-loop hooks. More setup, much more control.

**Native tool use** (`03`) — When you don't want a framework. Direct SDK calls, inspect every step, add custom logic between tool calls. Good for understanding what the frameworks abstract away.

**Structured output** (`04`) — When your agent needs to *produce* data, not just text. Pydantic schema forces the model to return valid typed objects — no string parsing.

> See `curriculum/weeks-04-end-coding/model-proxy/client.py` for the base `get_client()` function that examples 03 and 04 are built on.
