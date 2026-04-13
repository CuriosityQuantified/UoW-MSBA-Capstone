# 01_langchain_agent.py
# LangChain ReAct agent using the course proxy.
#
# create_agent(tools, system) is your starting point — give it tools,
# get back an AgentExecutor you can invoke with any task.
#
# Prerequisites:
#   pip install langchain langchain-anthropic langfuse python-dotenv
#
# Environment variables required (.env):
#   PROXY_AUTH_TOKEN        — semester token from instructor
#   LANGFUSE_PUBLIC_KEY     — from your Langfuse project
#   LANGFUSE_SECRET_KEY
#   LANGFUSE_HOST=https://us.cloud.langfuse.com

import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
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


def create_agent(tools: list, system: str = "You are a helpful assistant.") -> AgentExecutor:
    """
    Build a LangChain ReAct agent with the given tools.

    Args:
        tools:  List of @tool-decorated functions the agent can call.
        system: System prompt describing the agent's role and behavior.

    Returns:
        AgentExecutor — call with agent.invoke({"input": "your task"})
    """
    llm = get_llm()

    prompt = PromptTemplate.from_template(
        system + "\n\n"
        "You have access to the following tools:\n\n"
        "{tools}\n\n"
        "Use this format:\n"
        "Question: the input question\n"
        "Thought: reason about what to do\n"
        "Action: the tool to use, one of [{tool_names}]\n"
        "Action Input: the input to the tool\n"
        "Observation: the result\n"
        "... (repeat Thought/Action/Observation as needed)\n"
        "Thought: I now know the final answer\n"
        "Final Answer: the answer\n\n"
        "Begin!\n\n"
        "Question: {input}\n"
        "Thought: {agent_scratchpad}"
    )

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


# ---------------------------------------------------------------------------
# Example tools — replace with tools relevant to your use case
# ---------------------------------------------------------------------------

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input: a Python math expression string."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        return str(result)
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
        {"input": "If I convert $5,000 USD to EUR and then multiply by 1.15, what do I get?"},
        config={"callbacks": [handler]},
    )

    print("\nFinal answer:", result["output"])
    # Check your Langfuse dashboard — every ReAct step is traced.
