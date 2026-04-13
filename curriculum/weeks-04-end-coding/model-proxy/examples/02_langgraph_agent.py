# 02_langgraph_agent.py
# LangGraph agent with custom graph construction using the course proxy.
#
# create_graph(tools, system) returns a compiled StateGraph. Use this when
# you need control that create_agent doesn't expose: custom routing logic,
# additional state fields, human-in-the-loop interrupts, or checkpointing.
#
# Uses MessagesState and the Graph API — the standard LangGraph pattern.
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
from typing import Literal
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langfuse.callback import CallbackHandler

load_dotenv()

PROXY_URL = "https://model-proxy.curiosityquantified.com"
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"


# ---------------------------------------------------------------------------
# Core setup
# ---------------------------------------------------------------------------

def get_llm(tools: list | None = None) -> ChatAnthropic:
    """Return a ChatAnthropic instance routed through the course proxy.
    Pass tools to bind them for tool calling."""
    llm = ChatAnthropic(
        model=MODEL,
        anthropic_api_key=os.environ["PROXY_AUTH_TOKEN"],
        anthropic_api_url=PROXY_URL,
    )
    return llm.bind_tools(tools) if tools else llm


def get_langfuse_handler(session_id: str = "default") -> CallbackHandler:
    """Return a Langfuse callback — traces every node, LLM call, and tool use."""
    return CallbackHandler(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ.get("LANGFUSE_HOST", "https://us.cloud.langfuse.com"),
        session_id=session_id,
    )


# ---------------------------------------------------------------------------
# Graph factory — the function you build on top of
# ---------------------------------------------------------------------------

def create_graph(tools: list, system: str = "You are a helpful assistant."):
    """
    Build a LangGraph agent with explicit node and edge definitions.

    Graph structure:
      START → llm_call ⇄ tool_node → END

    Use this pattern (vs 01_langchain_agent) when you need:
      - Additional state fields beyond messages
      - Custom routing between multiple tool nodes
      - Human-in-the-loop interrupts (interrupt_before=["tool_node"])
      - Checkpointing / persistent memory

    Args:
        tools:  List of @tool-decorated functions the agent can call.
        system: System prompt describing the agent's role and behavior.

    Returns:
        Compiled StateGraph — invoke with:
            graph.invoke({"messages": [HumanMessage(content="...")]})
    """
    llm_with_tools = get_llm(tools=tools)
    tool_node = ToolNode(tools)

    def llm_call(state: MessagesState) -> MessagesState:
        """LLM decides whether to call a tool or produce a final response."""
        messages = state["messages"]
        # Prepend system message if not already present
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=system)] + list(messages)
        return {"messages": [llm_with_tools.invoke(messages)]}

    def should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
        """Route to tool execution or stop based on whether the LLM called a tool."""
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tool_node"
        return END

    builder = StateGraph(MessagesState)
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)
    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    builder.add_edge("tool_node", "llm_call")

    return builder.compile()


# ---------------------------------------------------------------------------
# Example tools
# ---------------------------------------------------------------------------

@tool
def search_company_data(company: str) -> str:
    """
    Look up basic financial data for a company by name or ticker.
    Returns mock data — replace with a real data source (Yahoo Finance, etc.).
    """
    mock_db = {
        "AAPL": {"revenue": "$383B", "employees": 161_000, "sector": "Technology"},
        "MSFT": {"revenue": "$212B", "employees": 221_000, "sector": "Technology"},
        "AMZN": {"revenue": "$575B", "employees": 1_540_000, "sector": "E-commerce"},
    }
    ticker = company.upper()
    data = mock_db.get(ticker)
    if not data:
        return f"No data found for '{company}'. Try: AAPL, MSFT, AMZN"
    return f"{ticker}: revenue={data['revenue']}, employees={data['employees']:,}, sector={data['sector']}"


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input: a valid Python math expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    graph = create_graph(
        tools=[search_company_data, calculate],
        system=(
            "You are a financial research assistant. "
            "Use your tools to gather data and calculate metrics. "
            "Always show your reasoning before giving a final answer."
        ),
    )

    handler = get_langfuse_handler(session_id="langgraph-demo")

    result = graph.invoke(
        {"messages": [HumanMessage(
            content="Compare Apple and Microsoft by revenue. Which is larger, and by what percentage?"
        )]},
        config={"callbacks": [handler]},
    )

    print("\nFinal answer:")
    print(result["messages"][-1].content)
    # Check your Langfuse dashboard — every node transition and tool call is traced.
