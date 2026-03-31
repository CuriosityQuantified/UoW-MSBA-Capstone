# 04_long_horizon_guard.py
# Long-horizon agent with cost guard, step limit, and checkpointing.
#
# This pattern is mandatory for any agent running more than ~10 steps.
# Without these guards, a runaway agent can exhaust your API budget
# and leave you with no way to resume or understand what happened.
#
# Built-in safeguards:
#   - Cost guard: stops if cumulative spend exceeds MAX_COST_USD
#   - Step limit: hard ceiling on iterations
#   - Checkpointing: persists state after every step; resumes on restart
#   - Full Langfuse tracing: every step is a span with cost metadata
#
# Prerequisites:
#   pip install langfuse openai
#
# Environment variables required:
#   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, OPENAI_API_KEY

import json
import os
import time
from dataclasses import asdict, dataclass, field

from langfuse import get_client
from openai import OpenAI

langfuse = get_client()
openai_client = OpenAI()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_COST_USD = 0.50        # Stop if cumulative cost exceeds this
MAX_STEPS = 20             # Hard ceiling on iterations regardless of cost
CHECKPOINT_FILE = "/tmp/agent_checkpoint.json"

# GPT-4o-mini pricing as of 2026 — update if model changes
COST_PER_1K_INPUT_TOKENS = 0.000150
COST_PER_1K_OUTPUT_TOKENS = 0.000600


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1000 * COST_PER_1K_INPUT_TOKENS
        + output_tokens / 1000 * COST_PER_1K_OUTPUT_TOKENS
    )


# ---------------------------------------------------------------------------
# Checkpoint — persist state so the agent can resume after interruption
# ---------------------------------------------------------------------------

@dataclass
class AgentCheckpoint:
    task: str
    step: int = 0
    total_cost_usd: float = 0.0
    findings: list = field(default_factory=list)
    complete: bool = False


def save_checkpoint(cp: AgentCheckpoint) -> None:
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(asdict(cp), f, indent=2)


def load_checkpoint(task: str) -> AgentCheckpoint:
    """Load an existing checkpoint for this task, or start fresh."""
    try:
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
        if data.get("task") == task:
            print(f"Resuming from checkpoint at step {data['step']}")
            return AgentCheckpoint(**data)
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass
    return AgentCheckpoint(task=task)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

def long_horizon_research_agent(task: str, subtasks: list[str]) -> dict:
    """
    Iterates over a list of subtasks, one LLM call per step.

    Stops early if:
      - Cost exceeds MAX_COST_USD
      - Steps exceed MAX_STEPS

    Checkpoints after every step so partial results are never lost.
    Full execution trace visible in Langfuse with per-step cost metadata.
    """

    cp = load_checkpoint(task)

    with langfuse.start_as_current_observation(
        as_type="trace",
        name="long-horizon-research",
        input={"task": task, "subtask_count": len(subtasks)},
        metadata={
            "max_cost_usd": MAX_COST_USD,
            "max_steps": MAX_STEPS,
            "resuming_from_step": cp.step,
        },
    ) as trace:

        remaining = subtasks[cp.step:]

        for i, subtask in enumerate(remaining, start=cp.step):

            # --- Guards ---
            if cp.total_cost_usd >= MAX_COST_USD:
                print(
                    f"⚠️  Cost guard at step {i}: "
                    f"${cp.total_cost_usd:.4f} >= ${MAX_COST_USD}"
                )
                trace.update(
                    metadata={
                        "stop_reason": "cost_guard",
                        "final_cost_usd": cp.total_cost_usd,
                    }
                )
                break

            if i >= MAX_STEPS:
                print(f"⚠️  Step limit reached at step {i}")
                trace.update(metadata={"stop_reason": "step_limit"})
                break

            print(f"Step {i + 1}/{len(subtasks)}: {subtask}")

            with langfuse.start_as_current_observation(
                as_type="generation",
                name=f"step-{i + 1}",
                model="gpt-4o-mini",
                input=subtask,
                metadata={
                    "step": i + 1,
                    "cumulative_cost_usd": round(cp.total_cost_usd, 6),
                },
            ) as gen:

                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a research assistant working on: {task}",
                        },
                        {"role": "user", "content": subtask},
                    ],
                )

                result = response.choices[0].message.content
                step_cost = estimate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                )

                cp.total_cost_usd += step_cost
                cp.step = i + 1
                cp.findings.append(
                    {"step": i + 1, "subtask": subtask, "finding": result}
                )

                gen.update(
                    output=result,
                    usage={
                        "input": response.usage.prompt_tokens,
                        "output": response.usage.completion_tokens,
                    },
                    metadata={
                        "step_cost_usd": round(step_cost, 6),
                        "cumulative_cost_usd": round(cp.total_cost_usd, 6),
                    },
                )

            # Checkpoint after every step — safe to interrupt at any point
            save_checkpoint(cp)
            time.sleep(0.3)  # Avoid rate limit bursts

        cp.complete = True
        save_checkpoint(cp)

        summary = {
            "task": task,
            "steps_completed": cp.step,
            "total_cost_usd": round(cp.total_cost_usd, 6),
            "findings": cp.findings,
        }
        trace.update(
            output=summary,
            metadata={"total_cost_usd": round(cp.total_cost_usd, 6)},
        )
        return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = long_horizon_research_agent(
        task="Survey AI governance frameworks across 5 industry sectors",
        subtasks=[
            "What are the key AI governance frameworks in healthcare?",
            "What are the key AI governance frameworks in financial services?",
            "What are the key AI governance frameworks in education?",
            "What are the key AI governance frameworks in government/public sector?",
            "What are the key AI governance frameworks in autonomous vehicles?",
        ],
    )

    print(f"\nCompleted {result['steps_completed']} steps")
    print(f"Total cost: ${result['total_cost_usd']:.6f}")
    print("\nFindings summary:")
    for f in result["findings"]:
        print(f"  Step {f['step']}: {f['subtask'][:60]}...")

    langfuse.flush()
