# 08 — Observability & Tracing

> **Non-negotiable rule:** Instrument your agent before you run it — not after it breaks.

Observability is not a debugging afterthought. In agentic systems — especially long-horizon tasks — it is the difference between understanding why something failed and guessing. You cannot add it retroactively without rewriting your architecture.

---

## Why Agents Make Observability Hard

Standard logging works fine for deterministic systems: a request comes in, steps execute in order, a response goes out. Agents break this model in three ways:

| Problem | Why it matters |
|---------|---------------|
| **Non-determinism** | The same input can produce different tool call sequences, making log-based debugging unreliable |
| **Nested calls** | An orchestrator calls workers, which call tools, which call sub-agents — each with its own LLM calls. Standard logs flatten this; you lose causal structure |
| **Long-horizon tasks** | A task running 50+ steps over minutes or hours accumulates errors, cost, and drift that compound invisibly |
| **Cost unpredictability** | Agents autonomously decide how many LLM calls to make — without tracing, you have no cost visibility until the bill arrives |
| **Silent failures** | An intermediate step can fail softly (hallucinate a tool result, skip a memory update) and the final output still looks plausible |

---

## What to Instrument

Think in three tiers — instrument all three from day one:

### 1. Traces (the whole task)
A trace captures the complete lifecycle of a single agent run: start time, end time, total cost, final output, and any metadata (user ID, session ID, task type).

### 2. Spans (individual steps)
Every meaningful operation inside a trace gets a span: each LLM call, tool execution, retrieval step, memory read/write, and sub-agent invocation. Spans are nested — you can see the full causal tree.

### 3. Evaluations (quality scores)
Attach scores to traces and spans: LLM-as-judge scores, user feedback, pass/fail assertions, custom rubric scores. Without evals, you can debug individual runs but can't measure quality at scale.

---

## Langfuse — The Open Source Standard

[Langfuse](https://langfuse.com) is the recommended observability platform for this course. It's open source, self-hostable, framework-agnostic (works with LangGraph, OpenAI Agents SDK, CrewAI, Pydantic AI, raw API calls), and converging with OpenTelemetry as the industry standard.

**Key docs:**
- [Observability Overview](https://langfuse.com/docs/observability/overview)
- [Get Started with Tracing](https://langfuse.com/docs/observability/get-started)
- [AI Agent Observability Guide](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse) — comprehensive agent-specific guide
- [Token & Cost Tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)
- [Sessions (multi-turn)](https://langfuse.com/docs/observability/features/sessions)
- [Datasets & Evals](https://langfuse.com/docs/evaluation/experiments/datasets)

---

## Videos

| Video | Channel | Length | Why Watch |
|-------|---------|--------|-----------|
| [Langfuse Intro — Observability & Tracing Deep Dive](https://www.youtube.com/watch?v=pTneXS_m1rk) | Langfuse (official) | 11 min | CEO walkthrough of the full product — start here |
| [LangSmith 101 for AI Observability](https://www.youtube.com/watch?v=Iyc80hY2yYk) | James Briggs | 9 min | LangSmith as alternative if you're already on LangChain stack |
| [Stop Confusing LangChain, LangGraph, and LangSmith](https://www.youtube.com/watch?v=e-GR3PlEOVU) | ByteMonk | 12 min | Clarifies how tracing (LangSmith) fits the broader stack; strong on long-horizon production concerns |

---

## Code Examples

The examples below are in `/examples/observability/`. Study them in order.

### Example 1 — Minimal Langfuse Setup (`01_minimal_trace.py`)

The simplest possible instrumentation. Understand this before anything else.

```python
# examples/observability/01_minimal_trace.py
# Minimal Langfuse tracing setup
# Prerequisites: pip install langfuse openai
# Set env vars: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, OPENAI_API_KEY

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
        metadata={"version": "1.0", "environment": "dev"}
    ) as trace:
        
        # Span for the LLM call
        with langfuse.start_as_current_observation(
            as_type="generation",
            name="llm-call",
            model="gpt-4o-mini",
            input=task
        ) as generation:
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": task}]
            )
            result = response.choices[0].message.content
            
            # Attach token usage — Langfuse tracks cost automatically
            generation.update(
                output=result,
                usage={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens
                }
            )
        
        trace.update(output=result)
        return result

if __name__ == "__main__":
    result = run_agent_step("Summarize the key risks of deploying autonomous agents in healthcare.")
    print(result)
    langfuse.flush()  # Required in short-lived scripts
```

---

### Example 2 — Multi-Step Agent with Nested Spans (`02_multi_step_agent.py`)

This is the pattern to internalize. Every meaningful operation gets its own span. You can see the full execution tree in the Langfuse UI.

```python
# examples/observability/02_multi_step_agent.py
# Multi-step agent with full nested tracing
# Shows: tool calls, memory reads, sub-agent invocations as separate spans

import os
import json
from langfuse import get_client
from openai import OpenAI

langfuse = get_client()
openai_client = OpenAI()

# --- Simulated tools ---

def search_web(query: str) -> str:
    """Simulated web search tool."""
    return f"[Search results for: {query}] Key findings: regulatory frameworks are evolving rapidly."

def read_memory(key: str) -> str:
    """Simulated memory read."""
    memory_store = {
        "user_context": "Nicholas is researching AI governance for a healthcare client.",
        "prior_findings": "Previous search found 3 relevant frameworks."
    }
    return memory_store.get(key, "No memory found.")

def write_memory(key: str, value: str) -> None:
    """Simulated memory write."""
    pass  # In production: write to vector store, Redis, etc.

# --- Agent logic ---

def research_agent(task: str, session_id: str) -> str:
    """
    A simple research agent with 3 steps:
    1. Read memory for context
    2. Search the web
    3. Synthesize and write back to memory
    
    Every step is a separate span — you see the full trace in Langfuse.
    """
    
    with langfuse.start_as_current_observation(
        as_type="trace",
        name="research-agent",
        input={"task": task},
        session_id=session_id,  # Groups traces into a session (multi-turn)
        user_id="msba-student",
        tags=["research", "demo"]
    ) as trace:
        
        # Step 1: Memory read
        with langfuse.start_as_current_observation(
            as_type="span",
            name="memory-read",
            input={"key": "user_context"}
        ) as mem_span:
            context = read_memory("user_context")
            mem_span.update(output={"context": context})
        
        # Step 2: Tool call — web search
        with langfuse.start_as_current_observation(
            as_type="span",
            name="tool-call:search_web",
            input={"query": task},
            metadata={"tool": "search_web"}
        ) as tool_span:
            search_results = search_web(task)
            tool_span.update(output={"results": search_results})
        
        # Step 3: LLM synthesis
        prompt = f"""Context: {context}

Search results: {search_results}

Task: {task}

Synthesize a 2-sentence answer."""

        with langfuse.start_as_current_observation(
            as_type="generation",
            name="synthesis",
            model="gpt-4o-mini",
            input=prompt
        ) as gen:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            gen.update(
                output=answer,
                usage={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens
                }
            )
        
        # Step 4: Write back to memory
        with langfuse.start_as_current_observation(
            as_type="span",
            name="memory-write",
            input={"key": "prior_findings", "value": answer}
        ) as write_span:
            write_memory("prior_findings", answer)
            write_span.update(output={"status": "written"})
        
        trace.update(output=answer)
        return answer

if __name__ == "__main__":
    result = research_agent(
        task="What are the key AI governance frameworks for healthcare?",
        session_id="demo-session-001"
    )
    print(result)
    langfuse.flush()
```

---

### Example 3 — LangGraph + Langfuse Integration (`03_langgraph_traced.py`)

LangGraph auto-instruments with Langfuse via a callback handler. This is the pattern you'll use in your capstone if you're building with LangGraph.

```python
# examples/observability/03_langgraph_traced.py
# LangGraph agent with automatic Langfuse tracing via callback
# Prerequisites: pip install langfuse langchain langgraph langchain-openai

import os
from typing import TypedDict, Annotated
from langfuse.callback import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# --- State definition ---

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    step_count: int
    task_complete: bool

# --- Langfuse callback — one line to instrument the whole graph ---

langfuse_handler = CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host="https://cloud.langfuse.com",
    session_id="langgraph-demo",
    user_id="msba-student",
    tags=["langgraph", "demo"]
)

llm = ChatOpenAI(model="gpt-4o-mini", callbacks=[langfuse_handler])

# --- Graph nodes ---

def agent_node(state: AgentState) -> AgentState:
    """Core reasoning step."""
    response = llm.invoke(state["messages"])
    return {
        "messages": [response],
        "step_count": state["step_count"] + 1,
        "task_complete": "DONE" in response.content
    }

def should_continue(state: AgentState) -> str:
    """Routing logic — stop after 5 steps or when task signals completion."""
    if state["task_complete"] or state["step_count"] >= 5:
        return "end"
    return "continue"

# --- Build graph ---

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_conditional_edges("agent", should_continue, {
    "continue": "agent",
    "end": END
})
graph = builder.compile()

# --- Run ---

if __name__ == "__main__":
    initial_state = {
        "messages": [HumanMessage(content="Analyze the top 3 risks of deploying AI agents in financial services. Be thorough. End with DONE.")],
        "step_count": 0,
        "task_complete": False
    }
    
    result = graph.invoke(
        initial_state,
        config={"callbacks": [langfuse_handler]}
    )
    
    print(result["messages"][-1].content)
    # Full trace visible in Langfuse dashboard — every LLM call, every step
```

---

### Example 4 — Long-Horizon Task: Cost Guard + Step Logging (`04_long_horizon_guard.py`)

For tasks that run many steps, you need two things built in from the start: a **cost guard** (stop before you burn too much money) and **checkpoint logging** (persist state so you can resume if something fails).

```python
# examples/observability/04_long_horizon_guard.py
# Long-horizon agent with cost guard and checkpoint logging
# This pattern is mandatory for any agent running >10 steps

import os
import json
import time
from dataclasses import dataclass, field, asdict
from langfuse import get_client
from openai import OpenAI

langfuse = get_client()
openai_client = OpenAI()

# --- Config ---

MAX_COST_USD = 0.50       # Stop if cumulative cost exceeds this
MAX_STEPS = 20            # Hard ceiling on iterations
CHECKPOINT_FILE = "/tmp/agent_checkpoint.json"

# --- Cost tracking ---

# GPT-4o-mini pricing (update if using different model)
COST_PER_1K_INPUT_TOKENS = 0.000150
COST_PER_1K_OUTPUT_TOKENS = 0.000600

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1000 * COST_PER_1K_INPUT_TOKENS +
            output_tokens / 1000 * COST_PER_1K_OUTPUT_TOKENS)

# --- Checkpoint ---

@dataclass
class AgentCheckpoint:
    task: str
    step: int = 0
    total_cost_usd: float = 0.0
    findings: list = field(default_factory=list)
    complete: bool = False

def save_checkpoint(cp: AgentCheckpoint):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(asdict(cp), f)

def load_checkpoint(task: str) -> AgentCheckpoint:
    try:
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
            if data["task"] == task:
                print(f"Resuming from checkpoint at step {data['step']}")
                return AgentCheckpoint(**data)
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass
    return AgentCheckpoint(task=task)

# --- Agent ---

def long_horizon_research_agent(task: str, subtasks: list[str]) -> dict:
    """
    Research agent that iterates over subtasks.
    Built-in: cost guard, step limit, checkpointing, full trace.
    """
    
    cp = load_checkpoint(task)
    
    with langfuse.start_as_current_observation(
        as_type="trace",
        name="long-horizon-research",
        input={"task": task, "subtask_count": len(subtasks)},
        metadata={"max_cost_usd": MAX_COST_USD, "max_steps": MAX_STEPS}
    ) as trace:
        
        for i, subtask in enumerate(subtasks[cp.step:], start=cp.step):
            
            # Cost guard
            if cp.total_cost_usd >= MAX_COST_USD:
                print(f"⚠️  Cost guard triggered at step {i}: ${cp.total_cost_usd:.4f} >= ${MAX_COST_USD}")
                trace.update(metadata={"stop_reason": "cost_guard", "final_cost_usd": cp.total_cost_usd})
                break
            
            # Step guard
            if i >= MAX_STEPS:
                print(f"⚠️  Step guard triggered at step {i}")
                trace.update(metadata={"stop_reason": "step_limit"})
                break
            
            print(f"Step {i+1}/{len(subtasks)}: {subtask}")
            
            with langfuse.start_as_current_observation(
                as_type="generation",
                name=f"step-{i+1}",
                model="gpt-4o-mini",
                input=subtask,
                metadata={"step": i+1, "cumulative_cost": cp.total_cost_usd}
            ) as gen:
                
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"You are a research assistant working on: {task}"},
                        {"role": "user", "content": subtask}
                    ]
                )
                
                result = response.choices[0].message.content
                step_cost = estimate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                
                cp.total_cost_usd += step_cost
                cp.step = i + 1
                cp.findings.append({"step": i+1, "subtask": subtask, "finding": result})
                
                gen.update(
                    output=result,
                    usage={
                        "input": response.usage.prompt_tokens,
                        "output": response.usage.completion_tokens
                    },
                    metadata={"step_cost_usd": step_cost, "cumulative_cost_usd": cp.total_cost_usd}
                )
            
            # Checkpoint after every step — resume safely if interrupted
            save_checkpoint(cp)
            time.sleep(0.5)  # Rate limiting
        
        cp.complete = True
        save_checkpoint(cp)
        
        summary = {
            "task": task,
            "steps_completed": cp.step,
            "total_cost_usd": cp.total_cost_usd,
            "findings": cp.findings
        }
        trace.update(output=summary, metadata={"total_cost_usd": cp.total_cost_usd})
        return summary

if __name__ == "__main__":
    result = long_horizon_research_agent(
        task="Survey AI governance frameworks across 5 industry sectors",
        subtasks=[
            "What are the key AI governance frameworks in healthcare?",
            "What are the key AI governance frameworks in financial services?",
            "What are the key AI governance frameworks in education?",
            "What are the key AI governance frameworks in government/public sector?",
            "What are the key AI governance frameworks in autonomous vehicles?"
        ]
    )
    
    print(f"\nCompleted {result['steps_completed']} steps")
    print(f"Total cost: ${result['total_cost_usd']:.4f}")
    langfuse.flush()
```

---

## What to Look for in the Langfuse Dashboard

After running any of the examples above, open your Langfuse project and check:

| View | What to look for |
|------|-----------------|
| **Trace timeline** | Are spans nested correctly? Can you see the causal chain? |
| **Token usage per span** | Which step is consuming the most tokens? |
| **Cost by trace** | How much did this run cost? Is it scaling as expected? |
| **Error spans** | Any red spans? What was the input/output at the failure point? |
| **Session view** | For multi-turn agents: can you see the full conversation arc? |

---

## Long-Horizon Specific Patterns

These patterns are non-negotiable for any agent running more than ~10 steps:

### 1. Cost Guards
Set a hard limit in USD before the agent starts. Log a warning when you hit 50% of budget. Stop (or pause for human review) at 100%.

### 2. Step Limits
No agent should run unbounded. Set a maximum iteration count and surface it as a trace attribute.

### 3. Checkpointing
Write state to disk (or a key-value store) after every step. On restart, load from checkpoint and resume — don't re-run completed steps.

### 4. Intermediate Output Logging
Don't only log the final answer. Every intermediate result should be a span with input and output. This is where bugs hide.

### 5. Session IDs for Multi-Turn Tasks
Group related traces into a session. You can then replay the entire task history in the Langfuse UI.

---

## Tooling Landscape

| Tool | Best for | Open source? |
|------|---------|-------------|
| [Langfuse](https://langfuse.com) | Full tracing + evals + cost tracking, self-hostable | ✅ |
| [LangSmith](https://smith.langchain.com) | Deep LangChain/LangGraph integration | ❌ (SaaS) |
| [Phoenix (Arize)](https://phoenix.arize.com) | OpenTelemetry-native, RAG evaluation | ✅ |
| [Helicone](https://helicone.ai) | Lightweight proxy-based tracing | ✅ |

For this course: **Langfuse** is the recommended default. It's open source, has the strongest agent support, and aligns with where the industry is heading (OpenTelemetry standard).

---

## Required Reading — Week 4

| Resource | Time | Why |
|----------|------|-----|
| [Langfuse — AI Agent Observability Guide](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse) | ~20 min | Comprehensive agent tracing guide — read before coding |
| [Langfuse — Get Started with Tracing](https://langfuse.com/docs/observability/get-started) | ~10 min | Hands-on setup guide |
| [LangChain — On Agent Frameworks and Observability](https://blog.langchain.com/on-agent-frameworks-and-agent-observability/) | ~10 min | Industry context on why observability is now a first-class concern |
