# 03_langgraph_traced.py
# LangGraph agent with automatic Langfuse tracing via callback handler.
#
# One line of setup traces every LLM call, every state transition,
# every tool invocation — automatically.
#
# Prerequisites:
#   pip install langfuse langchain langgraph langchain-openai
#
# Environment variables required:
#   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, OPENAI_API_KEY

import os
from typing import TypedDict, Annotated

from langfuse.callback import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


# ---------------------------------------------------------------------------
# Langfuse callback — one line to instrument the entire graph
# ---------------------------------------------------------------------------

langfuse_handler = CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host="https://cloud.langfuse.com",
    session_id="langgraph-demo",
    user_id="msba-student",
    tags=["langgraph", "demo"],
)

llm = ChatOpenAI(model="gpt-4o-mini", callbacks=[langfuse_handler])


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    step_count: int
    task_complete: bool


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

def agent_node(state: AgentState) -> AgentState:
    """Core reasoning step — each invocation is a traced LLM call."""
    response = llm.invoke(state["messages"])
    return {
        "messages": [response],
        "step_count": state["step_count"] + 1,
        "task_complete": "DONE" in response.content,
    }


def should_continue(state: AgentState) -> str:
    """Route: stop after 5 steps or when the agent signals completion."""
    if state["task_complete"] or state["step_count"] >= 5:
        return "end"
    return "continue"


# ---------------------------------------------------------------------------
# Build and compile graph
# ---------------------------------------------------------------------------

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "agent", "end": END},
)
graph = builder.compile()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    initial_state = {
        "messages": [
            HumanMessage(
                content=(
                    "Analyze the top 3 risks of deploying AI agents in financial services. "
                    "Be thorough. When finished, end your response with the word DONE."
                )
            )
        ],
        "step_count": 0,
        "task_complete": False,
    }

    result = graph.invoke(
        initial_state,
        config={"callbacks": [langfuse_handler]},
    )

    print(result["messages"][-1].content)
    # Open your Langfuse dashboard — every LLM call and state transition is visible.
