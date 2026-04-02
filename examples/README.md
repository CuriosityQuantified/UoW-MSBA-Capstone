# Examples

Runnable Python scripts. Each is self-contained and executable.

---

## Setup (do once)

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install langfuse langchain-anthropic langgraph python-dotenv

# Set your API keys (or add to .env file)
export ANTHROPIC_API_KEY="sk-ant-..."
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
```

You can get free Langfuse API keys at [cloud.langfuse.com](https://cloud.langfuse.com).

---

## Observability Examples

Run these in order — each builds on the previous.

| Script | What it demonstrates | Time |
|--------|---------------------|------|
| [`observability/01_minimal_trace.py`](./observability/01_minimal_trace.py) | Add tracing to a single LLM call in 5 lines | 2 min |
| [`observability/02_multi_step_agent.py`](./observability/02_multi_step_agent.py) | Trace a multi-step agent with tool calls | 5 min |
| [`observability/03_cost_guard.py`](./observability/03_cost_guard.py) | Stop the agent when token budget is exceeded | 5 min |
| [`observability/04_long_horizon_guard.py`](./observability/04_long_horizon_guard.py) | Guard patterns for long-running agents | 10 min |

### Run a script
```bash
python examples/observability/01_minimal_trace.py
```

Then open [cloud.langfuse.com](https://cloud.langfuse.com) → your project → Traces to see the result.

---

## Adding New Examples

When adding an example:
1. Put it in a subfolder named for the concept (e.g., `examples/memory/`, `examples/multi-agent/`)
2. Add setup instructions and a one-line description to this README
3. Keep each script self-contained — no imports from sibling scripts
4. Add a comment at the top of the file explaining what it demonstrates
