# 05_deep_agent.py
# Deep agent with sub-agent delegation using the course proxy.
#
# create_deep_agent() builds a supervisor agent that can delegate to
# specialised sub-agents for parallel or multi-step work. The main agent
# decides when to hand off; sub-agents run their own tool loops and return
# results. Sub-agents inherit the main model when no override is set.
#
# Prerequisites:
#   pip install langchain langchain-anthropic deepagents langfuse python-dotenv
#
# Environment variables required (.env):
#   PROXY_AUTH_TOKEN        — semester token from instructor
#   LANGFUSE_PUBLIC_KEY     — from your Langfuse project
#   LANGFUSE_SECRET_KEY
#   LANGFUSE_HOST=https://us.cloud.langfuse.com

import os
from typing import Literal
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langfuse.callback import CallbackHandler
from deepagents import create_deep_agent

load_dotenv()

PROXY_URL = "https://model-proxy.curiosityquantified.com"
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"


# ---------------------------------------------------------------------------
# Core setup
# ---------------------------------------------------------------------------

def get_llm() -> ChatAnthropic:
    """Return a ChatAnthropic instance routed through the course proxy."""
    return ChatAnthropic(
        model=MODEL,
        anthropic_api_key=os.environ["PROXY_AUTH_TOKEN"],
        anthropic_api_url=PROXY_URL,
    )


def get_langfuse_handler(session_id: str = "default") -> CallbackHandler:
    """Return a Langfuse callback — traces every agent, sub-agent, and tool call."""
    return CallbackHandler(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ.get("LANGFUSE_HOST", "https://us.cloud.langfuse.com"),
        session_id=session_id,
    )


# ---------------------------------------------------------------------------
# Deep agent factory
# ---------------------------------------------------------------------------

def create_research_agent(subagent_configs: list[dict] | None = None):
    """
    Build a deep agent that delegates sub-tasks to specialised sub-agents.

    The main agent acts as a supervisor: it receives the user's request,
    plans which sub-agents to invoke (potentially in parallel), synthesises
    their results, and produces a final answer.

    Sub-agent dict shape:
        {
            "name":         str,   # unique identifier
            "description":  str,   # when the main agent should delegate here
            "system_prompt": str,  # the sub-agent's persona and instructions
            "tools":        list,  # tools available only to this sub-agent
            # "model": ...         # omit → inherits the main model
        }

    Args:
        subagent_configs: List of sub-agent dicts. Defaults to a built-in
                          financial research sub-agent if not provided.

    Returns:
        Compiled deep agent — invoke with:
            agent.invoke({"messages": [{"role": "user", "content": "..."}]})
        Or stream with:
            agent.stream({"messages": [...]}, stream_mode="updates", subgraphs=True)
    """
    if subagent_configs is None:
        subagent_configs = [_default_data_subagent()]

    return create_deep_agent(
        model=get_llm(),
        system_prompt=(
            "You are a senior financial research coordinator. "
            "For data lookups and calculations, delegate to your sub-agents. "
            "Synthesise their findings into a clear, concise answer."
        ),
        subagents=subagent_configs,
        name="coordinator",
    )


def _default_data_subagent() -> dict:
    """Pre-built financial data sub-agent used in the demo."""
    return {
        "name": "financial-data-agent",
        "description": (
            "Delegate to this sub-agent for financial data lookups and "
            "arithmetic calculations. Give it one focused question at a time."
        ),
        "system_prompt": (
            "You are a precise financial data analyst. "
            "Use your tools to look up company data and run calculations. "
            "Return structured results with the numbers clearly labelled."
        ),
        "tools": [lookup_company, calculate],
        # No "model" key → inherits the main agent's ChatAnthropic instance
    }


# ---------------------------------------------------------------------------
# Sub-agent tools (financial data + calculator)
# ---------------------------------------------------------------------------

@tool
def lookup_company(ticker: str) -> str:
    """
    Look up financial snapshot for a company by ticker symbol.
    Returns mock data — replace with a real data source (Yahoo Finance, etc.).
    """
    db = {
        "AAPL": {"revenue": 383, "net_income": 97,  "employees": 161_000, "sector": "Technology"},
        "MSFT": {"revenue": 212, "net_income": 72,  "employees": 221_000, "sector": "Technology"},
        "AMZN": {"revenue": 575, "net_income": 30,  "employees": 1_540_000, "sector": "E-commerce"},
        "NVDA": {"revenue": 130, "net_income": 55,  "employees": 29_600,  "sector": "Semiconductors"},
    }
    t = ticker.upper().strip()
    d = db.get(t)
    if not d:
        return f"No data for '{ticker}'. Available tickers: {', '.join(db)}"
    return (
        f"{t}: revenue=${d['revenue']}B, net_income=${d['net_income']}B, "
        f"profit_margin={d['net_income']/d['revenue']:.1%}, "
        f"employees={d['employees']:,}, sector={d['sector']}"
    )


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input: a valid Python math expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# ---------------------------------------------------------------------------
# Demo — invoke and streaming
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = create_research_agent()
    handler = get_langfuse_handler(session_id="deep-agent-demo")
    config = {"callbacks": [handler]}

    question = (
        "Compare Apple and NVIDIA by profit margin. "
        "Which is more profitable, and by how many percentage points?"
    )

    # --- Option A: invoke (waits for full response) ---
    print("=== invoke ===")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
    )
    print(result["messages"][-1].content)

    # --- Option B: stream (prints updates as they arrive) ---
    print("\n=== stream ===")
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
        stream_mode="updates",
        subgraphs=True,
    ):
        if chunk.get("type") == "updates":
            label = f"[subagent: {chunk['ns']}]" if chunk.get("ns") else "[coordinator]"
            messages = chunk.get("data", {}).get("messages", [])
            for msg in (messages if isinstance(messages, list) else []):
                if hasattr(msg, "content") and msg.content:
                    print(f"{label} {msg.content[:120]}")

    # Check your Langfuse dashboard — the coordinator and sub-agent each appear
    # as separate traced spans with their own tool calls.
