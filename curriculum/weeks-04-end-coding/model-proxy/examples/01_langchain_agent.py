# 01_langchain_agent.py
# LangChain ReAct agent using the course proxy.
#
# create_agent(tools, system) is your starting point — give it tools,
# get back a compiled LangGraph you can invoke with any task.
#
# Uses create_react_agent from langgraph.prebuilt — the current recommended
# pattern. Returns a CompiledStateGraph directly; no AgentExecutor needed.
#
# Prerequisites:
#   pip install langchain langchain-anthropic langgraph langfuse python-dotenv
#
# Environment variables required (.env):
#   PROXY_AUTH_TOKEN        — semester token from instructor
#   LANGFUSE_PUBLIC_KEY     — from your Langfuse project
#   LANGFUSE_SECRET_KEY
#   LANGFUSE_HOST=https://us.cloud.langfuse.com

import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from langfuse.callback import CallbackHandler

load_dotenv()

PROXY_URL = "https://model-proxy.curiosityquantified.com"
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"


# ---------------------------------------------------------------------------
# Core setup — reuse these in your own project
# ---------------------------------------------------------------------------

def get_llm() -> ChatAnthropic:
    """Return a ChatAnthropic instance routed through the course proxy."""
    return ChatAnthropic(
        model=MODEL,
        anthropic_api_key=os.environ["PROXY_AUTH_TOKEN"],
        anthropic_api_url=PROXY_URL,
    )


def get_langfuse_handler(session_id: str = "default") -> CallbackHandler:
    """Return a Langfuse callback that traces every LLM call and tool use."""
    return CallbackHandler(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ.get("LANGFUSE_HOST", "https://us.cloud.langfuse.com"),
        session_id=session_id,
    )


def create_agent(tools: list, system: str = "You are a helpful assistant.") -> CompiledStateGraph:
    """
    Build a ReAct agent with the given tools.

    Uses create_react_agent from langgraph.prebuilt, which handles the
    tool-calling loop internally and returns a compiled graph directly.

    Args:
        tools:  List of @tool-decorated functions the agent can call.
        system: System prompt describing the agent's role and behavior.

    Returns:
        CompiledStateGraph — invoke with:
            agent.invoke({"messages": [HumanMessage(content="your task")]})
    """
    return create_react_agent(
        model=get_llm(),
        tools=tools,
        prompt=system,
    )


# ---------------------------------------------------------------------------
# Example tools — replace with tools relevant to your use case
# ---------------------------------------------------------------------------

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input: a Python math expression string."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307
    except Exception as e:
        return f"Error: {e}"


@tool
def lookup_exchange_rate(currency_pair: str) -> str:
    """
    Look up an exchange rate. Input format: 'USD/EUR'.
    Returns a mock rate for demonstration — replace with a real API call.
    """
    mock_rates = {"USD/EUR": 0.92, "USD/GBP": 0.79, "USD/JPY": 149.5, "EUR/GBP": 0.86}
    rate = mock_rates.get(currency_pair.upper(), "unknown")
    if rate == "unknown":
        return f"No rate found for {currency_pair}. Available: {list(mock_rates.keys())}"
    return f"1 {currency_pair.split('/')[0]} = {rate} {currency_pair.split('/')[1]}"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = create_agent(
        tools=[calculate, lookup_exchange_rate],
        system="You are a financial analysis assistant. Use tools to answer quantitative questions.",
    )

    handler = get_langfuse_handler(session_id="langchain-demo")

    result = agent.invoke(
        {"messages": [HumanMessage(content="If I convert $5,000 USD to EUR and then multiply by 1.15, what do I get?")]},
        config={"callbacks": [handler]},
    )

    print("\nFinal answer:", result["messages"][-1].content)
    # Check your Langfuse dashboard — every ReAct step and tool call is traced.
