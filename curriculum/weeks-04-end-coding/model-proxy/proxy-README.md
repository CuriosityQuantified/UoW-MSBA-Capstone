# UW MSBA AI Proxy

Secure access to Kimi K2.5 Turbo (via Fireworks AI) for your capstone projects. The proxy runs on Cloudflare's global edge — always available, no server to maintain.

## Quick Start: Claude Code Setup

This is the recommended setup. Claude Code uses the proxy as its model backend, so every `claude` session automatically uses Kimi K2.5 Turbo with no API key required.

### 1. Get your semester token from the instructor

You'll receive a token like: `msba2026-xxxxxxxxxxxxxxxx`

### 2. Create `~/.claude/settings.json`

```json
{
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "apiKeyHelper": "bash -c 'echo <YOUR_SEMESTER_TOKEN>'",
    "env": {
        "ANTHROPIC_BASE_URL": "https://model-proxy.curiosityquantified.com",
        "ANTHROPIC_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_SMALL_FAST_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo"
    },
    "model": "accounts/fireworks/routers/kimi-k2p5-turbo"
}
```

Replace `<YOUR_SEMESTER_TOKEN>` with the token from your instructor.

### 3. Launch Claude Code

```bash
claude
```

All Claude Code sessions — including subagents (Explore, Web Search, etc.) — use Kimi K2.5 Turbo through the proxy.

---

## Python Script Usage

For use outside Claude Code (evaluation scripts, notebooks, agent harnesses), use the Anthropic SDK:

```bash
pip install anthropic langfuse python-dotenv
```

Add to your `.env`:
```bash
PROXY_AUTH_TOKEN=<your-semester-token>
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com
```

See `proxy-example.py` for usage examples.

---

## Architecture

```
Claude Code / Python script
    ↓  Bearer <semester-token>
https://model-proxy.curiosityquantified.com  (Cloudflare Worker, global edge)
    ↓  Bearer <fireworks-api-key>
https://api.fireworks.ai/inference  →  kimi-k2p5-turbo
```

The instructor holds the Fireworks API key. Students authenticate with a semester token that can be rotated independently. No API keys are ever distributed to students.

---

## Rate Limits

- **180 requests per minute** (global across all students)
- No individual quotas — be considerate of classmates
- The proxy forces `kimi-k2p5-turbo` regardless of what model name you pass

---

## Troubleshooting

**401 Unauthorized**: Your semester token is wrong or missing. Check `~/.claude/settings.json` or your `PROXY_AUTH_TOKEN` env var.

**502/504**: Fireworks upstream issue. Retry with exponential backoff.

**No traces in Langfuse**: Verify your `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` and that the project exists at `us.cloud.langfuse.com`.

---

## AI-Native Development Methodology

This proxy is intentionally stateless — it only proxies inference. You own your observability:

- **Your Langfuse project** → your traces, token usage, latency
- **Your code** → your context, your memory, your harness
- **No lock-in** → swap models or observability tools without touching the proxy

### The Two Loops

**1. The Build Loop (Engineering)**
- Build fast with AI — prototype to answer questions, not just ship features
- Each build reveals something about the problem space
- Curate the output and own its quality

**2. The Insight Loop (Product/PM)**
- Define what winning looks like *before* the build starts
- Write behavior specifications that become the logic layer
- Run continuous evaluation against real scenarios
- Synthesize what each build reveals and feed into the next cycle

> "The person who communicates best will be the most valuable programmer in the future. Specifications, not prompts or code, are becoming the fundamental unit of programming." — Sean Grove, OpenAI

### Spec-First Development

- **The spec is the primary artifact; code is the output**
- A precise behavior specification written before any build determines whether AI-generated code solves the right problem

### Eval-Driven Quality

- Write **binary eval criteria** (pass/fail) before the build starts
- Run evals continuously against AI output as it's produced

### Why This Matters for Your Project

Your coursework should demonstrate both loops:
- **Build Loop**: Rapid prototyping and iteration with AI
- **Insight Loop**: Clear specifications, eval criteria, and synthesis of learnings
- **Quality**: Binary evals that run automatically, not manual review of AI output

---

## Further Reading

- [The SDLC for Building with AI](https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle) — Two-loop system for AI-native development
- [Your Harness, Your Memory](https://blog.langchain.com/your-harness-your-memory/) — Why owning your harness matters
- [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — LLM coding principles for CLAUDE.md
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — Production-grade skill library
- [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) — Apr 2026 research on skill utility under realistic conditions

### Key Concepts from "Your Harness, Your Memory"

**Memory IS the harness, not a plugin.** The harness decides:
- How context loads (AGENTS.md, skills, system prompts)
- What survives compaction vs. what's lost
- How interactions are stored and made queryable

**Ownership matters.** If you don't own your harness, you don't own your memory:
- Closed harnesses (APIs) store state you can't transfer
- Open harnesses let you swap models and resume threads
- This proxy is open — you own the code, you own the memory

### Studying Production Agent Architecture

[Claude Code from Source](https://github.com/alejandrobalderas/claude-code-from-source) — Reverse-engineered architecture of Anthropic's AI coding agent (~400 pages, 18 chapters).

### LLM Coding Pitfalls & Principles

[andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — Four principles from Andrej Karpathy's observations:

| Principle | Addresses |
|-----------|-----------|
| **Think Before Coding** | Wrong assumptions, hidden confusion, missing tradeoffs |
| **Simplicity First** | Overcomplication, bloated abstractions |
| **Surgical Changes** | Orthogonal edits, touching code you shouldn't |
| **Goal-Driven Execution** | Vague instructions → verifiable success criteria |

> "Don't tell it what to do, give it success criteria and watch it go."

### Production-Grade Skill Library

[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — 20 structured skills, 6-phase lifecycle (`/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`).

### Research: Skill Utility in Realistic Settings

[How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) (Apr 2026)

**Key finding:** Skill benefits are **fragile** without proper retrieval and refinement.

| Scenario | Performance |
|----------|-------------|
| Hand-curated skills (idealized) | High |
| Retrieved from 34k real skills | Approaches no-skill baseline |
| + Query-specific refinement | Recovers lost performance |

**Implication:** Don't assume skills automatically help. Design selection logic and test with realistic retrieval scenarios.
