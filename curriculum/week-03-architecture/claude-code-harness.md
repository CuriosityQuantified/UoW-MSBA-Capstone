# Claude Code Harness: Comprehensive Architecture Guide (April 2026)

> A deep dive into the production-grade agent infrastructure that powers Claude Code — from the harness concept to MCP integration, skills, subagents, and first principles for builders.

---

## 1. Claude Code Overview

### What It Is

Claude Code is Anthropic's agentic coding tool that transforms Claude from a conversational AI into an autonomous executor capable of reading codebases, editing files, running commands, and integrating with external systems. As the [official documentation states](https://code.claude.com/docs/en/overview), it "provides the tools, context management, and execution environment that turn a language model into a capable coding agent."

**Key insight:** Claude Code is not "Claude plus bash." It is a governed execution environment with a model at the center. The model reasons; the harness acts.

### Core Philosophy (April 2026)

| Principle | Implementation |
|-----------|----------------|
| **Separation of concerns** | Model generates intentions; harness validates and executes |
| **Explicit boundaries** | Every tool call flows through permission gates |
| **Stateful sessions** | Context accumulates across turns with intelligent compaction |
| **Extensible architecture** | Skills, MCP, hooks, and subagents compose cleanly |
| **Production safety** | Deny-first permission system prevents bypass even from jailbroken models |

### April 2026 Status

- **Agent SDK** (formerly Claude Code SDK) provides programmatic access to the same harness
- **Skills system** unified — commands and skills merged into one extensibility model
- **Deferred MCP loading** — tool schemas fetched on-demand, not at startup
- **Auto mode** — background classifier (Sonnet 4.6) evaluates tier-2 permissions without human intervention
- **Worktree isolation** — subagents can work on parallel git worktrees without conflicts
- **Remote MCP** — HTTP transport with OAuth 2.1 support for cloud-hosted MCP servers

---

## 2. The Harness Concept

### Definition

An **agent harness** is everything between the language model and the real world. As described in community analysis following the March 2026 source map incident:

> "The model generates text. The harness decides what that text can touch."

### Why Harness Design Matters for Production

Most agent demos skip the harness layer. You see a model calling functions in a clean loop. Then you run it for 45 minutes on a real codebase:

| Problem | Harness Solution |
|---------|------------------|
| Context overflows | Intelligent compaction at 98%, CLAUDE.md as persistent anchor |
| Permissions too loose or annoying | Three-tier permission model with auto-mode classifier |
| Tool results truncated | Configurable limits (25K default, 500K disk fallback) |
| Session state lost | Checkpoints, snapshots, resumable sessions |
| Silent failures | Hooks for audit logging and validation |

[Anthropic's engineering team has noted](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) that even frontier models running in loops across multiple context windows underperform without well-designed harnesses.

### Harness vs Model

| Component | Responsibility | Failure Mode |
|-----------|----------------|--------------|
| **Model** | Reasoning, planning, generating tool intentions | Hallucinates, drifts, tries to bypass rules |
| **Harness** | Permission enforcement, context management, tool dispatch, audit logging | Context overflow, misconfiguration, performance |

**Critical insight:** A compromised model cannot bypass safety checks by being persuasive. The harness evaluates deny/ask/allow rules in a separate code path. Deny always wins.

---

## 3. Core Architecture Components

### 3.1 Agent Loop and Tool Dispatch

The agent loop is Claude Code's beating heart:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Prompt    │───▶│ Model Decides│───▶│  Tool Call  │
│  + Context  │    │ Next Action  │    │  Requested  │
└─────────────┘    └──────────────┘    └──────┬──────┘
                                              │
                       ┌──────────────────────┘
                       ▼
              ┌─────────────────┐
              │ Permission Gate │
              │ (Deny/Ask/Allow)│
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐   ┌──────────┐   ┌──────────┐
    │  Deny  │   │ Ask User │   │ Execute  │
    │(Block) │   │(Confirm) │   │  Tool    │
    └────────┘   └──────────┘   └────┬─────┘
                                     │
                       ┌─────────────┘
                       ▼
              ┌─────────────────┐
              │  Return Result  │────▶ (Loop continues)
              │  to Context     │
              └─────────────────┘
```

### 3.2 Built-in Tools

Claude Code exposes approximately 19-40 permission-gated tools depending on configuration (file ops, search, execution, web, LSP, MCP, subagent coordination).

| Tool | Purpose | Permission Tier |
|------|---------|-----------------|
| **Read** | Read any file in working directory | Tier 1 (Auto-approved) |
| **Write** | Create new files | Tier 2 (Prompt/Auto) |
| **Edit** | Precise edits to existing files | Tier 2 (Prompt/Auto) |
| **Bash** | Run shell commands, scripts, git | Tier 2-3 (Context-dependent) |
| **Glob** | Find files by pattern (`**/*.ts`) | Tier 1 |
| **Grep** | Search file contents with regex | Tier 1 |
| **WebSearch** | Search the web for current info | Tier 1 |
| **WebFetch** | Fetch and parse web page content | Tier 1 |
| **LSP** | Code intelligence (definitions, references) | Tier 1 |
| **AskUserQuestion** | Ask clarifying questions with options | Tier 1 |
| **Agent** | Spawn subagents | Tier 2-3 |

**Key detail:** Tools are independently sandboxed. "The agent has filesystem access" is wrong — it's "the agent can use the Read tool, and Read has its own permission gate."

### 3.3 Permission System

#### Permission Modes (SDK/CLI)

| Mode | Behavior | Use Case |
|------|----------|----------|
| `default` | Ask for edits, bash, agent spawn | Interactive development |
| `acceptEdits` | Auto-accept file edits, ask for bash | Fast iteration |
| `plan` | Read-only, creates plan without executing | Review before action |
| `auto` | Background classifier approves tier-2 | Unattended sessions |
| `dontAsk` | Approve all within allowed_tools | CI/automation |
| `bypassPermissions` | No permission checks (dangerous) | Emergency only |

#### Three-Tier Mental Model

| Tier | Actions | Behavior |
|------|---------|----------|
| **Tier 1** | Read-only, safe navigation | Auto-approved |
| **Tier 2** | Controlled state changes (Edit, certain Bash) | Prompt in default; auto-mode classifier evaluates |
| **Tier 3** | High-risk (system modification, outside workdir) | Require explicit approval or blocked |

**Auto-mode classifier detail:** Running on Sonnet 4.6, it sees the user's request and tool call but **not the model's prose** — preventing the model from "sweet-talking" past the gate.

### 3.4 Context Management

#### Compaction at 98%

When token usage hits ~98% of the context window:
- Older tool outputs cleared first
- Conversation summarized if needed
- Critical metadata preserved
- Images and PDFs stripped

**Practical fix:** Put critical instructions in CLAUDE.md — the harness re-reads it on every turn.

#### Truncation Limits

| Type | Default | Maximum | Strategy |
|------|---------|---------|----------|
| MCP output | 25K tokens | 500K chars | Persist to disk, return reference |
| Tool results | Configurable | Varies | Warning at 10K tokens |

---

## 4. Context Engineering

### 4.1 CLAUDE.md Hierarchy

CLAUDE.md files merge hierarchically — enterprise → user → project → directory:

```
~/.claude/CLAUDE.md          # Personal preferences (user)
~/.claude/rules/*.md         # Split global instructions
./CLAUDE.md                  # Project-wide info
./src/components/CLAUDE.md   # Component-specific patterns
./CLAUDE.local.md            # Gitignored personal additions
```

**Loading behavior:** When working on `src/components/Button.vue`, Claude loads:
1. Enterprise CLAUDE.md (if configured)
2. User `~/.claude/CLAUDE.md`
3. Project root `CLAUDE.md`
4. `src/components/CLAUDE.md` (path-scoped rules)

**2026 additions:**
- `CLAUDE.local.md` — personal preferences without affecting team
- `~/.claude/rules/` — split global instructions into separate files

### 4.2 Progressive Context Loading

Before you type anything, Claude Code loads:
- CLAUDE.md files per hierarchy
- Auto memory
- MCP tool **names only** (not full schemas)
- Skill descriptions

As Claude works:
- File reads add content
- Path-scoped rules load automatically on file access
- Hooks fire after edits
- Subagents keep their own context windows

### 4.3 MCP Deferred Tool Loading (2026 Feature)

**Problem:** 50+ MCP tools = massive context overhead from tool schemas.

**Solution:** Tool names load at startup; full schemas fetched on-demand via ToolSearch.

**Result:** Orders of magnitude reduction in context overhead for MCP-heavy sessions.

Monitor remaining context with `/context` command.

---

## 5. Skills System (2026 Unified Model)

### 5.1 Skills as Unified Extensibility

**Before 2026:** Separate concepts for slash commands and skills.

**2026 Unified Model:** Commands and skills merged. Every skill gets a `/slash-command` interface.

```
.claude/skills/
├── deploy/
│   └── SKILL.md
├── security-audit/
│   └── SKILL.md
└── deep-research/
    └── SKILL.md
```

### 5.2 SKILL.md Structure and Frontmatter

```markdown
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(npm:*), Bash(git:*)
context: fork
agent: Explore
model: sonnet
argument-hint: environment name
paths: src/**/*.ts
---

Deploy to production:
1. Run tests
2. Build
3. Push to deployment target
```

**Key frontmatter fields:**

| Field | Purpose |
|-------|---------|
| `name` | Becomes `/slash-command` (lowercase, hyphens, max 64 chars) |
| `description` | Used for auto-invocation decisions |
| `disable-model-invocation` | `true` = user only (for deploy, commit) |
| `user-invocable` | `false` = hide from `/` menu (background knowledge) |
| `allowed-tools` | Tools Claude can use without asking |
| `context: fork` | Run in isolated subagent context |
| `agent` | Subagent type: Explore, Plan, or general-purpose |
| `model` | Override: haiku, sonnet, opus |
| `paths` | Glob patterns limiting auto-load scope |

### 5.3 Auto-invocation vs Manual Invocation

| Trigger | Behavior | Example |
|---------|----------|---------|
| **Auto** | Claude detects task match from description | Research task → auto-invokes `deep-research` |
| **Manual** | User types `/skill-name` | `/deploy production` |
| **Disabled** | `disable-model-invocation: true` | Deployment requires explicit human trigger |

### 5.4 Subagent Context Forking

Setting `context: fork` spawns a separate context window:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
allowed-tools: Read, Grep, Glob
---

Research $ARGUMENTS thoroughly...
```

**Benefits:**
- Main conversation stays clean
- Deep work doesn't pollute primary context
- Can run multiple subagents in parallel

**Argument substitution:**
- `$ARGUMENTS` — all args
- `$0`, `$1`, `$2` — positional
- `${CLAUDE_SKILL_DIR}` — skill's directory

---

## 6. Subagents

### 6.1 Parent-Child Relationships

Subagents are specialized AI personalities with:
- Specific system prompts
- Restricted tool sets
- Separate context windows
- Messages include `parent_tool_use_id` for tracking

```
Parent Agent (main context)
    │
    ├──▶ Subagent: security-auditor
    │    (security focus, limited tools)
    │
    ├──▶ Subagent: code-reviewer  
    │    (read-only analysis)
    │
    └──▶ Subagent: test-writer
         (generates tests, isolated context)
```

### 6.2 Context Isolation Benefits

| Problem | Solution |
|---------|----------|
| Context pollution | Deep implementation work stays in subagent |
| Token bloat | Main conversation retains only summaries |
| Parallel work | Multiple subagents operate simultaneously |
| Focus drift | System prompt enforces single expertise area |

### 6.3 When to Spawn vs Inline Execution

| Spawn Subagent | Execute Inline |
|----------------|----------------|
| Deep specialized work (security audit, test generation) | Simple, quick tasks |
| Parallelizable analysis | Sequential work |
| Risk of context pollution | Low context impact |
| Different tool needs | Same tool set |
| Needs isolation from main conversation | Part of main flow |

**Worktree isolation (2026):** Set `isolation: worktree` to give subagents their own git worktree — multiple subagents can edit files in parallel without conflicts.

### 6.4 Built-in Subagent Types

| Type | Model | Purpose |
|------|-------|---------|
| **Explore** | Haiku | Fast, read-only exploration |
| **Plan** | Sonnet | Research and architecture |
| **General-purpose** | Inherit | Full tool access |

---

## 7. Hooks System

### 7.1 Lifecycle Hooks

Hooks are JSON-configured handlers in `.claude/settings.json` that trigger on lifecycle events:

**Available hooks (expanded 2026):**

| Category | Hooks |
|----------|-------|
| **Tool lifecycle** | `PreToolUse`, `PostToolUse` |
| **Session lifecycle** | `SessionStart`, `Stop`, `SubagentStart`, `SubagentStop` |
| **Task lifecycle** | `TaskCreated`, `TaskCompleted` |
| **Environment** | `CwdChanged`, `FileChanged` |
| **Permissions** | `PermissionDenied` |
| **Context** | `PreCompact`, `PostCompact` |
| **User input** | `UserPromptSubmit`, `Notification` |

### 7.2 Permission Enforcement

Every tool call flows through `PreToolUse` hooks before execution:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./validate-command.sh"
          }
        ]
      }
    ]
  }
}
```

**Return `updatedInput` to modify tool arguments before execution.**

### 7.3 Audit Logging Example

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "./.claude/hooks/log-change.sh",
            "async": true
          }
        ]
      }
    ]
  }
}
```

```bash
#!/usr/bin/env bash
# log-change.sh
file_path="$(jq -r '.tool_input.file_path // ""')"
echo "$(date -Iseconds): modified $file_path" >> ./audit.log
```

### 7.4 Handler Types

| Type | Use Case |
|------|----------|
| **Command** | Fast, predictable shell execution |
| **Prompt** | Flexible, LLM-based decision |
| **HTTP** | POST JSON to external service with auth headers |
| **Async** | Background execution without blocking (add `"async": true`) |

---

## 8. MCP Integration

### 8.1 MCP as Universal Adapter

[MCP (Model Context Protocol)](https://code.claude.com/docs/en/mcp) is an open standard for connecting AI agents to external systems — databases, browsers, APIs, and [hundreds of servers](https://github.com/modelcontextprotocol/servers).

```bash
# Add an MCP server
claude mcp add playwright --transport http "npx @playwright/mcp@latest"

# Use it
/mcp__playwright__navigate [args]
```

### 8.2 Transport Modes

| Mode | Use Case | 2026 Status |
|------|----------|-------------|
| **HTTP** | Remote servers, cloud deployment | Recommended; OAuth 2.1 support |
| **stdio** | Local processes | Stable |
| **SSE** | Legacy streaming | Deprecated, replaced by HTTP |

### 8.3 Tool Discovery and Deferred Loading

**Traditional (pre-2026):** All tool schemas loaded at startup.

**Deferred Loading (2026):**
1. Tool names load at session start
2. Schemas fetched on-demand via ToolSearch
3. Only used tools enter context

**Impact:** 50+ MCP tools become viable without context bloat.

### 8.4 Security Considerations

| Risk | Mitigation |
|------|------------|
| Prompt injection via MCP servers | Permission system gates all MCP tool calls |
| Third-party server trust | Explicit user approval required |
| Server count overhead | Recommended cap: 5-6 active servers |
| Large responses | 25K token default, 500K disk fallback |
| Auth flows | OAuth 2.1 with PKCE for remote servers |

**Warning:** Third-party MCP servers can be prompt injection vectors. The permission system helps, but trust verification is still the user's responsibility.

---

## 9. First Principles

### 9.1 Separation of Reasoning from Permission Enforcement

**Principle:** The model decides what it wants to do; a different system decides whether it's allowed.

**Why it matters:** Even a jailbroken model cannot override safety checks — they run in a literally different code path.

```
Model: "I want to delete /etc/passwd"
        ↓
Permission Gate: "Bash delete pattern detected → DENY"
        ↓
Result: Blocked (model never touches filesystem)
```

### 9.2 Explicit Context Management

Context is not a bottomless bag. Claude Code treats it as a managed resource:

| Mechanism | Purpose |
|-----------|---------|
| Compaction at 98% | Emergency context reduction |
| CLAUDE.md re-read | Persistent instructions survive compression |
| Tool output limits | Prevent single result from overwhelming context |
| Disk persistence | Large results stored, referenced in context |
| Subagent forking | Isolate heavy work from main conversation |

### 9.3 Delegation Over Monolithic Design

| Anti-pattern | Pattern |
|--------------|---------|
| One agent doing everything | Parent delegates to specialized subagents |
| All tools available always | Per-task tool restrictions |
| Giant system prompt | Hierarchical CLAUDE.md loading |
| Single context window | Parallel subagent execution |

### 9.4 Composability Through Skills/MCP

**Skills:** Reusable, versionable, shareable behavior bundles.
**MCP:** Universal adapter for external systems.

Together they create an ecosystem where:
- Capabilities are modular
- Security boundaries are explicit
- Teams can share and reuse agent behaviors
- External integrations follow a standard protocol

---

## 10. Comparison with Deep Agents

### 10.1 When to Use Claude Code Harness

| Scenario | Best Fit |
|----------|----------|
| Long-running coding sessions | ✓ Native support |
| Production safety requirements | ✓ Deny-first permissions, hooks |
| Multi-turn context accumulation | ✓ Compaction, CLAUDE.md persistence |
| Tool-heavy workflows | ✓ 19+ built-in tools, MCP ecosystem |
| Audit/compliance needs | ✓ Built-in audit hooks |
| Non-programmers using agents | ✓ Interactive permission prompts |

### 10.2 When to Use LangGraph/Deep Agents

| Scenario | Best Fit |
|----------|----------|
| Explicit state machine control | ✓ Graph-based orchestration |
| Custom node logic | ✓ Arbitrary Python/JS in nodes |
| Multi-agent teams (peer collaboration) | ✓ Native agent-to-agent messaging |
| Complex conditional flows | ✓ Visual graph construction |
| Integration with LangChain ecosystem | ✓ Native compatibility |
| Needs custom checkpointing logic | ✓ Configurable persistence |

### 10.3 Key Architectural Differences

| Aspect | Claude Code Harness | LangGraph Deep Agents |
|--------|---------------------|----------------------|
| **Control model** | Permission gates + hooks | Explicit graph nodes |
| **Context management** | Automatic compaction, CLAUDE.md | Manual state/thread configuration |
| **Tool system** | Built-in + MCP | LangChain tools + custom |
| **Safety model** | Deny-first, unbypassable | User-implemented |
| **Extensibility** | Skills, plugins, MCP | Custom nodes, edges |
| **Subagent model** | Parent-child, context fork | Peer-to-peer agent teams |
| **Audit trail** | Built-in hooks | User-implemented |
| **Session continuity** | Native checkpoints | Configurable checkpointer |
| **Best for** | Coding, research, file manipulation | Complex workflows, custom logic |

### 10.4 Decision Framework

```
Need production safety guarantees with minimal implementation?
  → Claude Code Harness

Need custom orchestration logic and state machines?
  → LangGraph

Need both? 
  → Claude Code for execution + LangGraph for orchestration
  → Or use Agent SDK programmatically within LangGraph nodes
```

---

## 11. Reference Links

### Official Documentation

| Resource | URL |
|----------|-----|
| Claude Code Overview | https://code.claude.com/docs/en/overview |
| How Claude Code Works | https://code.claude.com/docs/en/how-claude-code-works |
| Agent SDK Overview | https://platform.claude.com/docs/en/agent-sdk/overview |
| Agent SDK Quickstart | https://platform.claude.com/docs/en/agent-sdk/quickstart |
| Tools Reference | https://code.claude.com/docs/en/tools-reference |
| Permissions | https://code.claude.com/docs/en/permissions |
| MCP Documentation | https://code.claude.com/docs/en/mcp |
| Context Window | https://code.claude.com/docs/en/context-window |
| Memory | https://docs.anthropic.com/en/docs/claude-code/memory |
| Hooks | https://docs.anthropic.com/en/docs/claude-code/hooks |
| Headless/CLI | https://code.claude.com/docs/en/headless |
| Checkpoints | https://code.claude.com/docs/en/checkpointing |
| Commands | https://code.claude.com/docs/en/commands |

### Architecture Deep Dives

| Resource | URL |
|----------|-----|
| Architecture Breakdown (WaveSpeed) | https://wavespeed.ai/blog/posts/claude-code-agent-harness-architecture/ |
| Full Stack Guide (Alex Opalic) | https://alexop.dev/posts/understanding-claude-code-full-stack/ |
| Architecture Deep Dive (Penligent) | https://www.penligent.ai/hackinglabs/inside-claude-code-the-architecture-behind-tools-memory-hooks-and-mcp/ |

### Engineering Blog Posts

| Resource | URL |
|----------|-----|
| Effective Harnesses for Long-Running Agents | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents |
| Auto-Mode Classifier | https://www.anthropic.com/engineering/claude-code-auto-mode |
| Harness Design Research | https://www.anthropic.com/engineering/harness-design-long-running-apps |

### Ecosystem Resources

| Resource | URL |
|----------|-----|
| MCP Servers Registry | https://github.com/modelcontextprotocol/servers |
| Agent SDK Demos | https://github.com/anthropics/claude-agent-sdk-demos |
| Best MCP Servers (EvoMap) | https://evomap.ai/blog/best-mcp-servers-for-claude-code-2026 |

---

## Key Takeaways for Builders

1. **The harness is the hard part.** Everyone assumes the model is the competitive advantage — until they try making it do things reliably for more than five minutes.

2. **Separate reasoning from permission enforcement.** The model proposes; the harness disposes. This prevents bypass even from persuasive jailbroken models.

3. **Context management is explicit, not automatic.** Compaction, truncation limits, disk persistence — these are active mechanisms, not passive defaults.

4. **Design for session continuity.** Snapshots, CLAUDE.md as anchor, subagent isolation — long-running agents need memory that survives compression.

5. **Permission granularity pays off.** Per-tool, per-pattern, per-directory rules with deny-first evaluation separate demos from deployable systems.

6. **Skills + MCP = composable ecosystem.** Reusable behaviors meet universal adapters. That's the foundation for scalable agent architectures.

---

*Document version: April 2026 | Compiled from official Anthropic documentation and community architecture analyses*
