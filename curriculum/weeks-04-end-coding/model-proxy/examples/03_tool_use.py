# 03_tool_use.py
# Native Anthropic SDK tool use — no framework, full control.
#
# run_with_tools(messages, tools, system) is the agentic loop.
# Use this when you want to stay close to the metal: inspect every
# tool call, add custom logic between steps, or avoid framework overhead.
#
# Builds on client.py from the model-proxy folder.
# Copy client.py into your project root, then: from client import get_client, MODEL
#
# Prerequisites:
#   pip install anthropic langfuse python-dotenv
#
# Environment variables required (.env):
#   PROXY_AUTH_TOKEN        — semester token from instructor
#   LANGFUSE_PUBLIC_KEY     — from your Langfuse project
#   LANGFUSE_SECRET_KEY
#   LANGFUSE_HOST=https://us.cloud.langfuse.com

import json
import os
from typing import Any, Callable
from dotenv import load_dotenv

import anthropic
from langfuse.anthropic import anthropic as langfuse_anthropic

load_dotenv()

PROXY_URL = "https://model-proxy.curiosityquantified.com"
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"
MAX_STEPS = 10  # safety limit on tool-call rounds


def get_client() -> anthropic.Anthropic:
    """Return a Langfuse-traced Anthropic client via the course proxy."""
    return langfuse_anthropic.Anthropic(
        api_key=os.environ["PROXY_AUTH_TOKEN"],
        base_url=PROXY_URL,
    )


# ---------------------------------------------------------------------------
# Core agentic loop
# ---------------------------------------------------------------------------

def run_with_tools(
    messages: list[dict],
    tools: list[dict],
    tool_handlers: dict[str, Callable],
    system: str = "You are a helpful assistant.",
    max_tokens: int = 1024,
) -> str:
    """
    Run an agentic loop: LLM calls tools until it produces a final text response.

    Args:
        messages:      Initial conversation as Anthropic message dicts.
        tools:         Tool definitions in Anthropic tool schema format.
        tool_handlers: Dict mapping tool name → Python function to call.
        system:        System prompt.
        max_tokens:    Max tokens per LLM call.

    Returns:
        The final text response from the model.

    Example:
        result = run_with_tools(
            messages=[{"role": "user", "content": "What's the weather in Seattle?"}],
            tools=[WEATHER_TOOL_SCHEMA],
            tool_handlers={"get_weather": get_weather},
        )
    """
    client = get_client()
    conversation = list(messages)

    for step in range(MAX_STEPS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=conversation,
        )

        # If no tool calls, we have the final answer
        if response.stop_reason == "end_turn":
            return next(
                (block.text for block in response.content if hasattr(block, "text")),
                "",
            )

        # Process tool calls
        if response.stop_reason == "tool_use":
            # Add assistant's response (including tool_use blocks) to conversation
            conversation.append({"role": "assistant", "content": response.content})

            # Execute each tool call and collect results
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                handler = tool_handlers.get(block.name)
                if not handler:
                    result = f"Error: no handler registered for tool '{block.name}'"
                else:
                    try:
                        result = handler(**block.input)
                        if not isinstance(result, str):
                            result = json.dumps(result)
                    except Exception as e:
                        result = f"Tool error: {e}"

                print(f"  [tool] {block.name}({block.input}) → {result[:80]}{'…' if len(result) > 80 else ''}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            conversation.append({"role": "user", "content": tool_results})

    return "Reached step limit without a final answer."


# ---------------------------------------------------------------------------
# Example tool definitions (Anthropic schema) + handlers
# ---------------------------------------------------------------------------

WEATHER_TOOL: dict[str, Any] = {
    "name": "get_weather",
    "description": "Get current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Seattle'"},
        },
        "required": ["city"],
    },
}

CALCULATE_TOOL: dict[str, Any] = {
    "name": "calculate",
    "description": "Evaluate a mathematical expression.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "A Python math expression, e.g. '(72 - 32) * 5/9'"},
        },
        "required": ["expression"],
    },
}


def get_weather(city: str) -> str:
    """Mock weather lookup — replace with a real API (OpenWeatherMap, etc.)."""
    mock = {
        "seattle": "55°F, overcast",
        "new york": "68°F, partly cloudy",
        "miami": "85°F, sunny",
        "chicago": "61°F, windy",
    }
    return mock.get(city.lower(), f"Weather data unavailable for {city}")


def calculate(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    answer = run_with_tools(
        messages=[{
            "role": "user",
            "content": (
                "What's the weather in Seattle? Convert that temperature to Celsius "
                "and tell me if I need a jacket (under 15°C = yes)."
            ),
        }],
        tools=[WEATHER_TOOL, CALCULATE_TOOL],
        tool_handlers={"get_weather": get_weather, "calculate": calculate},
        system="You are a concise weather assistant. Use tools to get data, then answer directly.",
    )

    print("\nAnswer:", answer)
