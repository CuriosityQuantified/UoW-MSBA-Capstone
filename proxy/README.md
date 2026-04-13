# UW MSBA AI Proxy

A Modal-hosted proxy that provides secure access to Fireworks AI models (Kimi K2.5) for student projects.

## Quick Start for Students

### 1. Install Dependencies

```bash
pip install langfuse openai
```

### 2. Set Environment Variables

Add to your `.env` file or export in your shell:

```bash
# Your Langfuse project (for tracing/observability)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com

# Proxy auth (provided by instructor)
PROXY_AUTH_TOKEN=fall-2026-secret
```

### 3. Use in Your Code

```python
from langfuse.openai import OpenAI  # Drop-in replacement
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize client pointing to the proxy
client = OpenAI(
    api_key=os.environ["PROXY_AUTH_TOKEN"],  # Our shared secret
    base_url="https://nap1320--uw-msba-proxy-serve.modal.run/v1"  # Proxy endpoint
)

# Make a request (automatically traced to YOUR Langfuse)
response = client.chat.completions.create(
    model="kimi-k2.5-fast",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the difference between precision and recall."}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)
```

### 4. View Traces

Log into your Langfuse dashboard to see:
- Request/response content
- Token usage and latency
- Model parameters
- Error rates

## AI-Native Development Methodology

Building with AI requires a different approach than traditional software development. This course follows the [two-loop system](https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle) for AI-native development:

### The Two Loops

**1. The Build Loop (Engineering)**
- Build fast with AI — prototype to answer questions, not just ship features
- Each build reveals something about the problem space
- Curate the output and own its quality
- "Build to reveal, not just ship"

**2. The Insight Loop (Product/PM)**
- Define what winning looks like *before* the build starts
- Write behavior specifications (not PRDs) that become the logic layer
- Run continuous evaluation against real customer scenarios
- Synthesize what each build reveals and feed into the next cycle

> "The person who communicates best will be the most valuable programmer in the future. Specifications, not prompts or code, are becoming the fundamental unit of programming." — Sean Grove, OpenAI

### Spec-First Development

In AI-native development:
- **The spec is the primary artifact; code is the output**
- Pull requests become living specs because teams discover requirements by prototyping
- A precise behavior specification written before any build determines whether AI-generated code solves the right problem

### Eval-Driven Quality

Traditional code review doesn't scale with AI-generated output:
- Write **binary eval criteria** (pass/fail) before the build starts
- Build evals from real-world customer failures
- Run evals continuously against AI output as it's produced
- Feed results back into the product immediately

> "You cannot review ten thousand lines of AI-generated code for quality at the end of a sprint."

### The Build Cycle

**Before the build:**
- Define the behavior spec: what must it do, what must it not do, what does wrong look like?
- Create eval rubric with binary criteria
- Calibrate with engineering: what will this build answer?

**During the build:**
- Scaffold the spec and evals to the build environment
- Run evals against AI output continuously
- Feed results back immediately

**After the build:**
- Synthesize what was revealed
- Measure which assumptions worked
- Feed learnings into the next spec

### Why This Matters for Your Project

Your coursework should demonstrate both loops:
- **Build Loop**: Show rapid prototyping and iteration with AI
- **Insight Loop**: Show clear specifications, eval criteria, and synthesis of learnings
- **Quality**: Binary evals that run automatically, not manual review of AI output

## Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| `kimi-k2.5-fast` | Fast general reasoning | Most tasks, prototyping |
| `kimi-k2.5-turbo` | Higher quality, slower | Final outputs, complex reasoning |

## Streaming Support

```python
stream = client.chat.completions.create(
    model="kimi-k2.5-fast",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Rate Limits

- **60 requests per minute** (global across all students)
- **No individual quotas** — be considerate of classmates

## Troubleshooting

**401 Unauthorized**: Check your `PROXY_AUTH_TOKEN` matches the current semester token.

**502/504 Errors**: The upstream (Fireworks) may be overloaded. Retry with exponential backoff.

**No traces in Langfuse**: Verify your `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are correct and the project exists.

## Architecture

```
Your Code (langfuse.openai)
    → Intercepts & logs to YOUR Langfuse
    → Forwards to Modal Proxy (your auth token)
        → Validates auth
        → Forwards to Fireworks (instructor's API key)
            → Returns response
```

You manage your own observability. The instructor manages the inference endpoint.

## Further Reading

- [The SDLC for Building with AI](https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle) — AI Bar Raiser
- [Your Harness, Your Memory](https://blog.langchain.com/your-harness-your-memory/) — LangChain
- GitHub Spec Kit — Specification-first development
- Amazon Kiro — Spec-driven AI workflows

### Key Concepts from "Your Harness, Your Memory"

**Memory IS the harness, not a plugin.** The harness decides:
- How context loads (AGENTS.md, skills, system prompts)
- What survives compaction vs. what's lost
- How interactions are stored and made queryable

**Ownership matters.** If you don't own your harness, you don't own your memory:
- Closed harnesses (APIs) store state you can't transfer
- Open harnesses let you swap models and resume threads
- This proxy is open — you own the code, you own the memory

**Why this course uses open harnesses:**
- Stateless proxy (no memory lock-in)
- Your Langfuse traces (your observability)
- Your code, your context, your control

### Studying Production Agent Architecture

[Claude Code from Source](https://github.com/alejandrobalderas/claude-code-from-source) — Reverse-engineered architecture of Anthropic's AI coding agent (~400 pages, 18 chapters).  
[claude-code-from-source.com](https://claude-code-from-source.com/) — Web version with searchable chapters.

### LLM Coding Pitfalls & Principles

[andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — Single CLAUDE.md derived from Andrej Karpathy's observations on LLM coding pitfalls.

**Four principles addressing common failures:**

| Principle | Addresses |
|-----------|-----------|
| **Think Before Coding** | Wrong assumptions, hidden confusion, missing tradeoffs |
| **Simplicity First** | Overcomplication, bloated abstractions |
| **Surgical Changes** | Orthogonal edits, touching code you shouldn't |
| **Goal-Driven Execution** | Vague instructions → verifiable success criteria |

**Key insight from Andrej:**
> "Don't tell it what to do, give it success criteria and watch it go."

Transform imperative tasks into verifiable goals:
- ❌ "Add validation" → ✅ "Write tests for invalid inputs, then make them pass"
- ❌ "Fix the bug" → ✅ "Write a test that reproduces it, then make it pass"

**Use this:** Include these principles in your CLAUDE.md or AGENTS.md to improve agent behavior.

### Production-Grade Skill Library

[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — Production-grade engineering skills for AI coding agents.

**6-phase development lifecycle:**

| Phase | Command | Key Principle |
|-------|---------|---------------|
| Define | `/spec` | Spec before code |
| Plan | `/plan` | Small, atomic tasks |
| Build | `/build` | One slice at a time |
| Verify | `/test` | Tests are proof |
| Review | `/review` | Improve code health |
| Ship | `/ship` | Faster is safer |

**20 structured skills** covering:
- `spec-driven-development` — PRD before any code
- `incremental-implementation` — Thin vertical slices, feature flags
- `test-driven-development` — Red-Green-Refactor, 80/15/5 pyramid
- `code-review-and-quality` — Five-axis review, change sizing ~100 lines
- `debugging-and-error-recovery` — Five-step triage, stop-the-line rule
- `context-engineering` — Feed agents right info at right time

**Use this when building:** Reference these skills for your own SKILL.md files.

### Research: Skill Utility in Realistic Settings

[How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) (Apr 2026) — First comprehensive study of skill performance under realistic conditions.

**Key finding:** Skill benefits are **fragile** without proper retrieval and refinement.

| Scenario | Performance |
|----------|-------------|
| Hand-curated skills (idealized) | High |
| Retrieved from 34k real skills | Approaches no-skill baseline |
| + Query-specific refinement | Recovers lost performance |

**Two bottlenecks limiting skill utility:**
1. **Selection**: Agents struggle to determine which skills to load
2. **Content**: Retrieved skills often lack precise task information

**What works:**
- **Agentic hybrid search** — iterative query formulation + candidate evaluation
- **Query-specific refinement** — adapt skills to the specific task (not generic offline improvement)

**Implication for your projects:**
- Don't assume skills automatically help — test with realistic retrieval
- Plan for skill selection logic (not just skill content)
- Consider query-specific refinement pipelines

**Key patterns you can apply:**
- **AsyncGenerator as agent loop** — yields Messages, typed Terminal return, natural backpressure
- **Speculative tool execution** — start read-only tools during model streaming
- **Concurrent-safe batching** — partition tools by safety, parallel reads, serialize writes
- **Fork agents for cache sharing** — parallel children share byte-identical prompt prefixes (~95% token savings)
- **4-layer context compression** — snip, microcompact, collapse, autocompact
- **Two-phase skill loading** — frontmatter at startup, full content on invocation
- **File-based memory with LLM recall** — Sonnet side-query selects relevant memories

This is educational pseudocode — patterns distilled, not proprietary code.
