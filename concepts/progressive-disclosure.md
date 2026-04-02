# 06 — Development Methodology: Progressive Disclosure

## Origin

Progressive Disclosure comes from 1990s UX research (Nielsen Norman Group): *show users only what they need right now, and defer advanced features until requested.* Thirty years later, it's the defining architectural pattern for managing context and capability in AI agents.

---

## The Core Problem It Solves

The instinct when building agents is to front-load everything: all tools, all docs, all skill instructions stuffed into the system prompt. This causes **context rot**.

> As irrelevant information accumulates, the agent's effective intelligence degrades. It struggles to identify what matters. It hallucinates connections between unrelated concepts. It loses track of the actual task.

Large language models process context through attention mechanisms that weigh every token against every other token. When you fill the context window with marginally relevant information, you're not just wasting tokens — you're actively introducing noise into the reasoning process.

**More tokens ≠ better outputs. Right tokens at the right time = better outputs.**

---

## The 3-Layer Architecture

### Layer 1 — Discovery (always loaded)
Lightweight metadata only: skill/tool name + one-line description.

The agent knows what capabilities exist and can make routing decisions. Minimal token cost. This is the index, not the content.

```markdown
# Available Skills
- web-search: Search the web for current information
- code-executor: Run Python code and return output
- file-reader: Read files from the local filesystem
- email-sender: Compose and send emails via SMTP
```

### Layer 2 — Activation (loaded when relevant)
Full instructions for the capability the agent has selected.

Context expands only when a capability is actually needed. The agent reads the full SKILL.md (or tool docs) for the tool it's about to use.

```markdown
# web-search — Full Instructions
Trigger: user needs current information, news, or facts beyond training data
Usage: call with a specific search query, not a vague topic
Output: returns title, URL, snippet for top 5 results
Error handling: if no results, broaden query; if rate limited, wait 2s and retry
```

### Layer 3 — Deep Dive (loaded on demand)
Examples, reference documentation, extended edge cases. Only when the agent explicitly needs more depth.

---

## The Key Insight

> **Provide the map, let the agent choose the path.**

Context becomes something the agent navigates, not something pre-loaded by the developer.

### Benefits
- **Lower token cost** — only relevant instructions enter context
- **Better tool selection** — agent isn't distracted by irrelevant tool docs
- **Faster reasoning** — attention focuses on what matters
- **Easier to extend** — add new skills without bloating every prompt

---

## Applied to the Build Process

The same principle applies to *how you build* agents, not just how you architect them:

### Rule: Earn each layer of complexity

**Step 1 — Minimum viable agent**
One tool. One clear task. No memory, no subagents, no routing.
Goal: does it do the thing at all?

**Step 2 — Add the second most important capability**
Only add the next layer when the current version demonstrably fails.
If the simple version works, stop there.

**Step 3 — Layer in infrastructure**
Memory when the agent needs to remember things across steps.
Routing when input types diverge significantly.
Subagents when a subtask is genuinely independent.
Evaluation when you need to measure reliability.

**Never add complexity speculatively.** Every layer you add before you need it is technical debt you'll pay when debugging.

---

## Practical Checklist

Before adding any new capability to your agent:

- [ ] Does the current version fail at something specific because this is missing?
- [ ] Is the failure repeatable and documented?
- [ ] Is this the simplest fix, or am I over-engineering?
- [ ] Can I add this without touching working code?

If you can't check all four boxes, don't add it yet.

---

## Further Reading

- [Why AI Agents Need Progressive Disclosure, Not More Data](https://www.honra.io/articles/progressive-disclosure-for-ai-agents) — honra.io, Feb 2026
- [Progressive Disclosure: the technique that helps control context and tokens in AI agents](https://medium.com/@martia_es/progressive-disclosure-the-technique-that-helps-control-context-and-tokens-in-ai-agents-8d6108b09289) — Medium, Feb 2026
- [S01-MCP03: Progressive Disclosure for Knowledge Discovery in Agentic Workflows](https://medium.com/@prakashkop054/s01-mcp03-progressive-disclosure-for-knowledge-discovery-in-agentic-workflows-8fc0b2840d01) — Medium, Dec 2025
