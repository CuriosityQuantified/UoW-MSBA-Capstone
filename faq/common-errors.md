# Common Errors — FAQ

---

## Setup & Installation

### `ModuleNotFoundError: No module named 'langfuse'`
You haven't installed the dependencies. Run:
```bash
pip install langfuse langchain-anthropic langgraph
```
If you're using a virtual environment (you should be), make sure it's activated first.

---

### `AuthenticationError: Invalid API key`
Check that your API key is set correctly. For Anthropic:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
Or add it to a `.env` file and load it with `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

### `RateLimitError` on first run
You're likely on a free/trial API tier. Either:
- Add a small `time.sleep(1)` between calls
- Upgrade your API tier
- Use a smaller model (Haiku instead of Sonnet) for testing

---

## Tracing

### Langfuse traces aren't appearing in the dashboard
Check in this order:
1. Is `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` set in your environment?
2. Did you call `langfuse.flush()` at the end of your script? (Langfuse batches sends — if your script exits before flush, traces are lost)
3. Are you looking at the right project in the dashboard?

---

### Traces show up but spans are missing
Make sure you're wrapping each logical step in a span:
```python
with langfuse.start_as_current_span("my-step"):
    # your code here
```
Without explicit spans, you only get a top-level trace.

---

## LangGraph

### `InvalidUpdateError: At key X: expected ...`
Your state update is returning the wrong shape. Every node must return a dict matching your `StateGraph` type annotations. Check that all required keys are present in your return value.

---

### Graph runs forever / never reaches END
You have a cycle with no exit condition. Add a conditional edge that routes to `END` when a completion condition is met:
```python
graph.add_conditional_edges(
    "agent",
    lambda state: "end" if state["done"] else "tools",
    {"end": END, "tools": "tool_node"}
)
```

---

## General

### My agent keeps hallucinating tool calls that don't exist
Your tool descriptions are ambiguous or your system prompt is too vague about what tools are available. Be explicit:
- List available tools by name in the system prompt
- Make tool descriptions specific: what it does, what it takes, what it returns
- Add a "do not call tools that aren't listed above" instruction

---

*Don't see your error? Open an issue and it'll be added here.*
