# 01_minimal_trace.py
# Minimal Langfuse tracing setup — start here before anything else.
#
# Prerequisites:
#   pip install langfuse openai
#
# Environment variables required:
#   LANGFUSE_PUBLIC_KEY   — from https://cloud.langfuse.com/settings
#   LANGFUSE_SECRET_KEY   — from https://cloud.langfuse.com/settings
#   OPENAI_API_KEY

import os
from langfuse import get_client
from openai import OpenAI

langfuse = get_client()
openai_client = OpenAI()


def run_agent_step(task: str) -> str:
    """A single agent step, fully traced."""

    # Top-level trace for the whole task
    with langfuse.start_as_current_observation(
        as_type="trace",
        name="agent-step",
        input=task,
        metadata={"version": "1.0", "environment": "dev"},
    ) as trace:

        # Nested span for the LLM call
        with langfuse.start_as_current_observation(
            as_type="generation",
            name="llm-call",
            model="gpt-4o-mini",
            input=task,
        ) as generation:

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": task}],
            )
            result = response.choices[0].message.content

            # Attach token usage — Langfuse calculates cost automatically
            generation.update(
                output=result,
                usage={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                },
            )

        trace.update(output=result)
        return result


if __name__ == "__main__":
    result = run_agent_step(
        "Summarize the key risks of deploying autonomous agents in healthcare."
    )
    print(result)
    langfuse.flush()  # Required in short-lived scripts to flush the event queue
