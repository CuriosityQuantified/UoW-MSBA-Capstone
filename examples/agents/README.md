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
| `01_langchain_agent.py` | LangChain ReAct | `create_agent(tools, system)` | Quick agents with familiar tooling |
| `02_langgraph_agent.py` | LangGraph graph | `create_graph(tools, system)` | Production agents, complex routing, HITL |
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

**LangChain** (`01`) — Good starting point. Familiar ReAct loop, easy to swap tools, plenty of community examples.

**LangGraph** (`02`) — Preferred for anything you'll ship. Explicit state machine, built-in checkpointing, natural human-in-the-loop hooks. More setup, much more control.

**Native tool use** (`03`) — When you don't want a framework. Direct SDK calls, inspect every step, add custom logic between tool calls. Good for understanding what the frameworks abstract away.

**Structured output** (`04`) — When your agent needs to *produce* data, not just text. Pydantic schema forces the model to return valid typed objects — no string parsing.

> See `curriculum/weeks-04-end-coding/model-proxy/client.py` for the base `get_client()` function that examples 03 and 04 are built on.
