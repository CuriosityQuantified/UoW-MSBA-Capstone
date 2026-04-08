# Deep Agents: Core Concepts & First Principles

*A foundational guide to LangChain Deep Agents architecture, context engineering, and documentation retrieval tools.*

---

## Table of Contents

1. [Deep Agents Overview](#1-deep-agents-overview)
2. [Harness Architecture](#2-harness-architecture)
3. [Model Routing & Selection](#3-model-routing--selection)
4. [Context Engineering Fundamentals](#4-context-engineering-fundamentals)
5. [Documentation Retrieval: Context7 & DeepWiki](#5-documentation-retrieval-context7--deepwiki)

---

## 1. Deep Agents Overview

### Core Concept

Deep Agents is a framework for building **long-running, autonomous AI agents** that can handle complex multi-step tasks. Unlike simple chatbots or single-turn LLM calls, Deep Agents are designed to:

- Execute extended workflows that span minutes or hours
- Maintain state across interactions
- Delegate work to subagents
- Interact with filesystems, code, and external tools
- Compress and manage context to stay within token limits

**Why it matters:** Traditional LLM interactions are stateless and limited by context windows. Deep Agents solve the "deep work" problem—tasks that require planning, iteration, tool use, and persistence.

### First Principles

1. **Agents need structure to scale** — Unstructured LLM conversations don't scale to complex tasks. Deep Agents provide architectural patterns (harness, subagents, skills) that impose necessary structure.

2. **Context is a scarce resource** — Context windows are finite. Deep Agents treat context engineering as a first-class concern with offloading, summarization, and isolation patterns.

3. **Delegation beats monolithic design** — Complex work should be decomposed and delegated. Subagents provide isolation, parallelism, and specialization.

4. **Tool use should be transparent** — Agents should use filesystems, code execution, and external APIs through well-defined, observable interfaces.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Planning** | Built-in `write_todos` tool for structured task tracking |
| **Virtual Filesystem** | Pluggable backends for file operations, multimodal support |
| **Subagents** | Delegate work to isolated child agents (inline and async) |
| **Context Management** | Automatic offloading, summarization, and compression |
| **Code Execution** | Sandboxed execution environments |
| **Human-in-the-Loop** | Interrupt at critical operations for approval |
| **Skills** | Progressive disclosure of specialized capabilities |
| **Memory** | Persistent cross-thread storage via `AGENTS.md` |

### When to Use Deep Agents

**Use Deep Agents when:**
- Tasks require multiple steps with planning
- Work may exceed a single context window
- You need filesystem/code interaction
- Parallel execution would speed up work
- You want persistent memory across sessions
- Human oversight is required at certain steps

**Don't use when:**
- Simple Q&A or single-turn responses suffice
- Latency is critical (overhead exists)
- Stateless, ephemeral behavior is desired

### Reference Links

- [Deep Agents v0.5 Blog Post](https://blog.langchain.com/deep-agents-v0-5/)
- [Deep Agents Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart)
- [Deep Agents Documentation](https://docs.langchain.com/oss/python/deepagents/)

---

## 2. Harness Architecture

### Core Concept

The **Harness** is the execution environment that combines capabilities making long-running agents feasible. Think of it as the "operating system" for your agent—providing filesystem access, planning tools, subagent delegation, context management, and more.

The harness is not a monolithic block but a **composition of middleware** that can be configured and extended.

### First Principles

1. **Capabilities should be composable** — Each harness feature (planning, filesystem, subagents) is implemented as middleware. Add only what you need.

2. **Abstractions must not leak** — The virtual filesystem works the same regardless of backend (local, cloud, sandbox).

3. **Safety by default** — Code execution requires explicit sandbox backend configuration. No accidental `rm -rf /`.

4. **Observability is essential** — Built-in tracing, interrupt points, and state inspection for debugging.

### Key Capabilities

#### Planning Tools
```python
# Built-in write_todos tool
write_todos(todos=[
    {"id": "1", "content": "Research API options", "status": "in_progress"},
    {"id": "2", "content": "Implement authentication", "status": "pending"},
])
```

**Features:**
- Track tasks with statuses (`pending`, `in_progress`, `completed`)
- Persisted in agent state
- Organizes complex multi-step work

#### Virtual Filesystem

| Tool | Purpose |
|------|---------|
| `ls` | List files with metadata |
| `read_file` | Read with offset/limit; supports multimodal (images, video, audio, PDFs) |
| `write_file` | Create new files |
| `edit_file` | Exact string replacements with global mode |
| `glob` | Pattern matching (`**/*.py`) |
| `grep` | Search with context |
| `execute` | Shell commands (sandbox only) |

**Supported Multimodal Extensions:**
- **Images:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.heic`, `.heif`
- **Video:** `.mp4`, `.mpeg`, `.mov`, `.avi`, `.flv`, `.mpg`, `.webm`, `.wmv`, `.3gpp`
- **Audio:** `.wav`, `.mp3`, `.aiff`, `.aac`, `.ogg`, `.flac`
- **Documents:** `.pdf`, `.ppt`, `.pptx`

#### Task Delegation (Subagents)

**Inline Subagents:**
- Block until completion
- Context isolation
- Return single report

**Async Subagents (v0.5+):**
- Fire-and-forget execution
- Stateful across interactions
- Five management tools: `start_async_task`, `check_async_task`, `update_async_task`, `cancel_async_task`, `list_async_tasks`

```python
from deepagents import AsyncSubAgent, create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[
        AsyncSubAgent(
            name="researcher",
            description="Performs deep research on a topic",
            url="https://my-agent-server.dev",
            graph_id="research_agent",
        ),
    ],
)
```

#### Human-in-the-Loop

```python
agent = create_deep_agent(
    model="claude-sonnet-4-6",
    interrupt_on={"edit_file": True}  # Pause before edits
)
```

**Use cases:**
- Safety gates for destructive operations
- Verification before expensive API calls
- Interactive debugging

#### Skills

Skills follow the [Agent Skills standard](https://agentskills.io/) with progressive disclosure:

```python
agent = create_deep_agent(
    model="claude-sonnet-4-6",
    skills=["/skills/research/", "/skills/web-search/"],
)
```

- Frontmatter read at startup
- Full content loaded only when relevant
- Reduces token usage vs. always-loaded context

#### Memory

Persistent `AGENTS.md` files always loaded:

```python
agent = create_deep_agent(
    model="claude-sonnet-4-6",
    memory=["/project/AGENTS.md", "~/.deepagents/preferences.md"],
)
```

**vs. Skills:**
- Memory: Always loaded, for critical conventions
- Skills: On-demand, for specialized workflows

### When to Use Each Capability

| Capability | When to Enable |
|------------|----------------|
| Planning | Multi-step tasks requiring tracking |
| Filesystem | Any file/code interaction |
| Sandbox + Execute | Code generation, dependency installation |
| Subagents | Parallel work, context isolation needed |
| Async Subagents | Long-running background tasks |
| Human-in-the-Loop | Destructive ops, high-cost actions |
| Skills | Reusable, domain-specific workflows |
| Memory | User preferences, project conventions |

### Reference Links

- [Harness Capabilities](https://docs.langchain.com/oss/python/deepagents/harness)
- [Sandbox Backends](https://docs.langchain.com/oss/python/deepagents/sandboxes)
- [Subagents](https://docs.langchain.com/oss/python/deepagents/subagents)
- [Async Subagents](https://docs.langchain.com/oss/python/deepagents/async-subagents)
- [Skills](https://docs.langchain.com/oss/python/deepagents/skills)

---

## 3. Model Routing & Selection

### Core Concept

Deep Agents work with any LangChain chat model supporting tool calling. The framework provides flexible model specification—from simple strings to runtime-configurable model switching.

### First Principles

1. **Models are interchangeable** — The agent harness works with any tool-calling model. No vendor lock-in.

2. **Model selection should be data-driven** — Choose models based on eval performance, cost, latency—not brand preference.

3. **Runtime flexibility matters** — User preferences, task complexity, and cost constraints may require model switching.

4. **Model capabilities vary** — Multimodal support, context windows, and reasoning abilities differ. Check model profiles.

### Key Capabilities

#### Simple Model Specification

```python
from deepagents import create_deep_agent

# String format: "provider:model"
agent = create_deep_agent(model="openai:gpt-5.3-codex")
agent = create_deep_agent(model="anthropic:claude-sonnet-4-6")
```

#### Model-Specific Configuration

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

# With thinking/reasoning
model = init_chat_model(
    model="anthropic:claude-sonnet-4-6",
    thinking={"type": "enabled", "budget_tokens": 10000},
)
agent = create_deep_agent(model=model)
```

#### Runtime Model Selection

```python
from dataclasses import dataclass
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from deepagents import create_deep_agent
from typing import Callable

@dataclass
class Context:
    model: str

@wrap_model_call
def configurable_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    model_name = request.runtime.context.model
    model = init_chat_model(model_name)
    return handler(request.override(model=model))

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[configurable_model],
    context_schema=Context,
)

# User selects model at runtime
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hello!"}]},
    context=Context(model="openai:gpt-4.1"),
)
```

#### Model Profiles

Check model capabilities programmatically:

```python
# Check multimodal support, context window, tool calling
model_profile = model.get_profile()
```

### Suggested Models (Based on Eval Suite)

| Provider | Recommended Models |
|----------|-------------------|
| **Anthropic** | `claude-opus-4-6`, `claude-opus-4-5`, `claude-sonnet-4-6`, `claude-sonnet-4-5` |
| **OpenAI** | `gpt-5.4`, `gpt-4o`, `gpt-4.1`, `o4-mini`, `gpt-5.2-codex`, `o3` |
| **Google** | `gemini-3-flash-preview`, `gemini-3.1-pro-preview` |
| **Open-weight** | `GLM-5`, `Kimi-K2.5`, `MiniMax-M2.5`, `qwen3.5-397B-A17B`, `devstral-2-123B` |

*Available via providers: Baseten, Fireworks, OpenRouter, Ollama*

### When to Use Each Pattern

| Pattern | Use Case |
|---------|----------|
| String spec | Quick prototyping, static model selection |
| `init_chat_model` | Provider-specific parameters (thinking, temperature) |
| Provider class | Fine-grained control over model behavior |
| Runtime middleware | User-configurable models, cost optimization |
| Dynamic routing | Task-complexity-based model selection |

### Reference Links

- [Models in Deep Agents](https://docs.langchain.com/oss/python/deepagents/models)
- [Chat Model Integrations](https://docs.langchain.com/oss/python/integrations/chat)
- [Dynamic Model Patterns](https://docs.langchain.com/oss/python/langchain/agents#dynamic-model)
- [Model Profiles](https://docs.langchain.com/oss/python/langchain/models#model-profiles)

---

## 4. Context Engineering Fundamentals

### Core Concept

**Context engineering** is the practice of providing the right information in the right format so agents can accomplish tasks reliably. Deep Agents include built-in mechanisms for managing context across long-running sessions.

### First Principles

1. **Context is finite** — Even 200K token windows fill up. Plan for compression.

2. **Recency != Relevance** — The most recent messages aren't always the most important. Smart summarization preserves intent, artifacts, and next steps.

3. **Isolation preserves context** — Subagents quarantine heavy work, returning only results.

4. **Persistence is separate from working memory** — Long-term memory requires different storage patterns than conversation history.

5. **Progressive disclosure optimizes tokens** — Load detailed instructions only when needed.

### Types of Context

| Context Type | What You Control | Scope |
|--------------|------------------|-------|
| **Input Context** | System prompt, memory, skills | Static, each run |
| **Runtime Context** | User metadata, API keys, connections | Per run, propagates to subagents |
| **Context Compression** | Offloading and summarization | Automatic at limits |
| **Context Isolation** | Subagent work quarantine | Per subagent |
| **Long-term Memory** | Persistent cross-thread storage | Across conversations |

### Input Context Components

The final system prompt is assembled from:

1. **Custom `system_prompt`** — Your custom instructions
2. **Base agent prompt** — Built-in guidance for planning, tools
3. **To-do list prompt** — Instructions for `write_todos`
4. **Memory prompt** — `AGENTS.md` + guidelines (if configured)
5. **Skills prompt** — Skills list with frontmatter (if configured)
6. **Virtual filesystem prompt** — Tool documentation
7. **Subagent prompt** — Task tool usage guidance
8. **Custom middleware prompts** — Your added middleware
9. **Human-in-the-loop prompt** — Interrupt usage (if configured)

### Context Compression Mechanisms

#### Offloading

When tool inputs/results exceed 20,000 tokens:

```
Large tool result → Saved to filesystem → Replaced with file reference + preview
```

**Trigger points:**
- Tool call inputs > 20K tokens at 85% context window
- Tool call results > 20K tokens immediately offloaded

#### Summarization

When context exceeds 85% of `max_input_tokens`:

1. **In-context summary** — LLM generates structured summary (intent, artifacts, next steps)
2. **Filesystem preservation** — Original messages written to disk
3. **Recent context kept** — Last 10% of tokens preserved

**Configuration:**
- Trigger: 85% of model's `max_input_tokens`
- Recent buffer: 10% of tokens
- Fallback: 170K trigger / 6 messages if no model profile

**Optional Summarization Tool:**

```python
from deepagents.middleware.summarization import create_summarization_tool_middleware

agent = create_deep_agent(
    model=model,
    middleware=[create_summarization_tool_middleware(model, backend)],
)
```

Allows agents to trigger summarization at opportune times (between tasks).

### Runtime Context

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    user_id: str
    api_key: str

@tool
def fetch_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    user_id = runtime.context.user_id
    return f"Data for user {user_id}"

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    tools=[fetch_user_data],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Get my activity"}]},
    context=Context(user_id="user-123", api_key="sk-..."),
)
```

**Key property:** Runtime context propagates to all subagents automatically.

### Long-Term Memory

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

def make_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memories/": StoreBackend(runtime)},  # Persisted path
    )

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    store=InMemoryStore(),
    backend=make_backend,
    system_prompt="""When users tell you preferences, save them to
    /memories/user_preferences.txt for future conversations.""",
)
```

### Best Practices

1. **Keep memory minimal** — Always-relevant conventions only
2. **Use skills for workflows** — Progressive disclosure saves tokens
3. **Delegate heavy work** — Subagents keep main context clean
4. **Instruct subagent brevity** — "Return summaries under 500 words"
5. **Use filesystem for large data** — Offload automatically or explicitly
6. **Document memory structure** — Tell agent what lives in `/memories/`
7. **Use runtime context for tools** — User metadata, API keys, connections

### Reference Links

- [Context Engineering](https://docs.langchain.com/oss/python/deepagents/context-engineering)
- [Context Concepts](https://docs.langchain.com/oss/python/concepts/context)
- [Long-term Memory](https://docs.langchain.com/oss/python/deepagents/memory)
- [Subagents Context Management](https://docs.langchain.com/oss/python/deepagents/subagents#context-management)
- [Backends](https://docs.langchain.com/oss/python/deepagents/backends)

---

## 5. Documentation Retrieval: Context7 & DeepWiki

### Core Concept

AI coding assistants often generate **outdated or hallucinated code** because they rely on stale training data. **Context7** and **DeepWiki** solve this by providing **up-to-date, version-specific documentation** directly to your agent's context.

### First Principles

1. **LLM training data ages quickly** — Libraries evolve. Yesterday's best practice is today's deprecated API.

2. **Hallucination stems from knowledge gaps** — When models don't know current APIs, they invent plausible-sounding ones.

3. **Context is the cure** — Feed the model current docs, and it generates current code.

4. **Retrieval should be automatic** — Manual copy-pasting docs defeats the purpose. Integration should be seamless.

---

## Context7

### What It Is

Context7 is a **documentation delivery platform** that pulls up-to-date, version-specific documentation and code examples from source repositories and injects them directly into your LLM's context.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Version-specific docs** | Gets docs for the exact library version you're using |
| **Code examples** | Working code samples, not just API reference |
| **MCP server** | Native tool calling for 30+ AI assistants |
| **CLI + Skills** | Works without MCP via skill-guided CLI commands |
| **Library matching** | Automatically identifies the library from your query |
| **Direct library IDs** | Use `/owner/repo` syntax for precise selection |

### How It Works

**Two modes of operation:**

1. **MCP Server Mode** — Registers `ctx7` tools your agent can call natively
2. **CLI + Skills Mode** — Agent uses `ctx7` CLI commands guided by skills

### Setup

```bash
# One-command setup
npx ctx7 setup

# Target specific agents
npx ctx7 setup --cursor
npx ctx7 setup --claude
npx ctx7 setup --opencode
```

**Manual MCP configuration:**
- Server URL: `https://mcp.context7.com/mcp`
- Header: `CONTEXT7_API_KEY: your-api-key`

### Usage Patterns

#### Natural Language Queries
```
Create a Next.js middleware that checks for a valid JWT in cookies
and redirects unauthenticated users to `/login`. use context7
```

#### Direct Library Specification
```
Implement basic authentication with Supabase.
use library /supabase/supabase for API and docs.
```

The `/owner/repo` syntax skips library matching and goes straight to docs retrieval.

#### Version-Specific Queries
```
How do I set up Next.js 14 middleware? use context7
```

Context7 automatically matches the appropriate version from your query.

### Available Tools

| Tool | Purpose |
|------|---------|
| `ctx7 library` | Search Context7 index by library name, return matching IDs |
| `ctx7 docs` | Retrieve documentation using Context7-compatible library ID |
| `resolve-library-id` | Convert general library name to Context7 ID |
| `query-docs` | Get relevant docs for a specific query |

### Why It Matters for Code Assistants

| Without Context7 | With Context7 |
|------------------|---------------|
| ❌ Outdated code examples from training data | ✅ Current, working code examples |
| ❌ Hallucinated APIs that don't exist | ✅ Verified, documented APIs |
| ❌ Generic answers ignoring version specifics | ✅ Version-appropriate guidance |
| ❌ Constant tab-switching to docs | ✅ Docs retrieved automatically |
| ❌ Broken code requiring fixes | ✅ Working code on first try |

### Supported Libraries

Context7 indexes major frameworks and libraries:
- **Frontend:** Next.js, React, Vue, Svelte, Tailwind CSS
- **Backend:** Node.js, Express, Fastify, Django, Flask
- **Databases:** MongoDB, PostgreSQL, Supabase, Redis
- **Cloud:** AWS SDK, Vercel, Cloudflare, Firebase
- **AI/ML:** LangChain, OpenAI, Anthropic, TensorFlow
- **Languages:** Python, TypeScript, Go, Rust, Ruby

[Full library index at context7.com](https://context7.com)

### Reference Links

- [Context7 Website](https://context7.com)
- [Context7 GitHub](https://github.com/upstash/context7)
- [Context7 MCP Server](https://smithery.ai/server/@upstash/context7-mcp)
- [CLI Reference](https://context7.com/docs/clients/cli)
- [MCP Clients Guide](https://context7.com/docs/resources/all-clients)
- [LangChain Docs on Context7](https://context7.com/langchain-ai/docs)

---

## DeepWiki

### What It Is

DeepWiki provides **AI-powered documentation** for every GitHub repository. It transforms static documentation into interactive, conversational knowledge bases.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Universal coverage** | Documentation for any public GitHub repo |
| **AI chat interface** | Ask questions about the codebase in natural language |
| **Structured summaries** | Auto-generated explanations of architecture, APIs, and usage |
| **Integration-ready** | Works with coding assistants and IDE extensions |

### How It Works

1. DeepWiki indexes public repositories
2. Generates structured documentation and embeddings
3. Provides chat interface for querying
4. Returns source-grounded answers with citations

### Usage

Access DeepWiki at [deepwiki.com](https://deepwiki.com) by navigating to any repository path:

```
https://deepwiki.com/owner/repo
```

Example:
- [deepwiki.com/langchain-ai/langchain](https://deepwiki.com/langchain-ai/langchain)
- [deepwiki.com/upstash/context7](https://deepwiki.com/upstash/context7)

### Context7 vs DeepWiki

| | **Context7** | **DeepWiki** |
|---|--------------|--------------|
| **Focus** | Library documentation & code examples | Repository understanding & code exploration |
| **Source** | Official library docs, package registries | GitHub repositories |
| **Use case** | "How do I use this library?" | "How does this codebase work?" |
| **Delivery** | Injected into LLM context | Chat interface, structured summaries |
| **Versioning** | Version-specific | Latest (or selected) commit |
| **Integration** | MCP server, CLI, skills | Web UI, potential future integrations |

### Why Both Matter

- **Context7** when you're *using* libraries — Get correct, current API usage
- **DeepWiki** when you're *exploring* codebases — Understand unfamiliar projects

### Reference Links

- [DeepWiki Website](https://deepwiki.com)

---

## Summary: Documentation Retrieval Best Practices

1. **Always enable Context7 for library questions** — "use context7" should be automatic
2. **Use explicit library IDs for precision** — `/owner/repo` syntax when you know the target
3. **Include versions in queries** — "Next.js 14" not just "Next.js"
4. **Configure agent rules** — "Always use Context7 for library/API documentation"
5. **Use DeepWiki for codebase exploration** — When you need to understand unfamiliar repos
6. **Combine both** — Context7 for implementation, DeepWiki for architecture understanding

---

## Quick Reference: When to Use What

| Situation | Solution |
|-----------|----------|
| Building long-running agent | → Deep Agents harness |
| Need filesystem/code interaction | → Virtual filesystem + sandbox |
| Multi-step task with planning | → write_todos + subagents |
| Parallel work streams | → Async subagents |
| Managing large context | → Compression + subagent isolation |
| User preferences across sessions | → Long-term memory |
| Reusable domain workflows | → Skills |
| Critical project conventions | → AGENTS.md memory |
| Need current library docs | → Context7 |
| Exploring unfamiliar codebase | → DeepWiki |
| Runtime model flexibility | → Middleware routing |

---

*Document generated: 2026-04-08*
*Sources: LangChain Deep Agents v0.5 blog, Harness docs, Models docs, Context Engineering docs, Context7 GitHub*
