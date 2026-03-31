# 02_multi_step_agent.py
# Multi-step agent with full nested tracing.
#
# Demonstrates:
#   - Trace → span → generation nesting
#   - Tool calls as spans
#   - Memory reads/writes as spans
#   - Session grouping for multi-turn tasks
#
# Prerequisites:
#   pip install langfuse openai
#
# Environment variables required:
#   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, OPENAI_API_KEY

import os
from langfuse import get_client
from openai import OpenAI

langfuse = get_client()
openai_client = OpenAI()


# ---------------------------------------------------------------------------
# Simulated tools — replace with real implementations in your capstone
# ---------------------------------------------------------------------------

def search_web(query: str) -> str:
    """Simulated web search tool."""
    return (
        f"[Search results for: {query}] "
        "Key finding: regulatory frameworks are evolving rapidly, with 12 new "
        "guidelines published in Q1 2026."
    )


def read_memory(key: str) -> str:
    """Simulated memory read from a key-value store."""
    memory_store = {
        "user_context": "Researcher studying AI governance for a healthcare client.",
        "prior_findings": "Previous session identified 3 relevant frameworks.",
    }
    return memory_store.get(key, "No memory found for this key.")


def write_memory(key: str, value: str) -> None:
    """Simulated memory write — in production, write to Redis/Pinecone/etc."""
    pass


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

def research_agent(task: str, session_id: str) -> str:
    """
    A 4-step research agent:
      1. Read memory for prior context
      2. Search the web
      3. Synthesize with an LLM call
      4. Write findings back to memory

    Every step is a separate span — you can see the full causal tree
    in the Langfuse dashboard.
    """

    with langfuse.start_as_current_observation(
        as_type="trace",
        name="research-agent",
        input={"task": task},
        session_id=session_id,   # Groups related traces into a session
        user_id="msba-student",
        tags=["research", "demo"],
    ) as trace:

        # Step 1: Memory read
        with langfuse.start_as_current_observation(
            as_type="span",
            name="memory-read",
            input={"key": "user_context"},
        ) as mem_span:
            context = read_memory("user_context")
            mem_span.update(output={"context": context})

        # Step 2: Tool call — web search
        with langfuse.start_as_current_observation(
            as_type="span",
            name="tool-call:search_web",
            input={"query": task},
            metadata={"tool": "search_web"},
        ) as tool_span:
            search_results = search_web(task)
            tool_span.update(output={"results": search_results})

        # Step 3: LLM synthesis
        prompt = (
            f"Context: {context}\n\n"
            f"Search results: {search_results}\n\n"
            f"Task: {task}\n\n"
            "Synthesize a 2-sentence answer."
        )

        with langfuse.start_as_current_observation(
            as_type="generation",
            name="synthesis",
            model="gpt-4o-mini",
            input=prompt,
        ) as gen:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            answer = response.choices[0].message.content
            gen.update(
                output=answer,
                usage={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                },
            )

        # Step 4: Memory write
        with langfuse.start_as_current_observation(
            as_type="span",
            name="memory-write",
            input={"key": "prior_findings", "value": answer},
        ) as write_span:
            write_memory("prior_findings", answer)
            write_span.update(output={"status": "written"})

        trace.update(output=answer)
        return answer


if __name__ == "__main__":
    result = research_agent(
        task="What are the key AI governance frameworks for healthcare?",
        session_id="demo-session-001",
    )
    print(result)
    langfuse.flush()
