# Agent Skills: A Comprehensive Guide

> **Key Insight**: Skills are **declarative, composable, and agent-discoverable** — they shift control from developer-defined workflows to agent-selected capabilities.
>
> *Reference implementation: [LangChain Deep Agents Skills](https://docs.langchain.com/oss/python/deepagents/skills)*

---

## Table of Contents

1. [What Are Skills?](#1-what-are-skills--definition-and-mental-model)
2. [Skills vs Traditional Workflows](#2-skills-vs-traditional-workflows)
3. [Benefits of Skills](#3-benefits-of-skills)
4. [Skill Design Best Practices](#4-skill-design-best-practices)
5. [Implementation Examples](#5-implementation-examples)
6. [When to Use Skills](#6-when-to-use-skills--decision-framework)
7. [Reference Links](#7-reference-links)

---

## 1. What Are Skills? — Definition and Mental Model

### Definition

A **Skill** is a self-contained, declarative capability package that teaches an agent how to perform a specialized task. In Deep Agents (LangChain's implementation), skills are directory-based modules containing:

```
skill-name/
├── SKILL.md          # Required: Metadata + instructions
├── scripts/          # Optional: Executable code
├── references/       # Optional: Documentation
├── assets/           # Optional: Templates, resources
└── ...               # Any additional files
```

### The Mental Model: Progressive Disclosure

Skills follow a **progressive disclosure** pattern that mimics how humans learn:

```
Level 1 (Startup): Agent sees only skill NAME + DESCRIPTION (~100 tokens)
         ↓
Level 2 (Matching): User asks about "PDFs" → Agent checks descriptions → Match found
         ↓
Level 3 (Activation): Agent reads full SKILL.md body (~500-5000 tokens)
         ↓
Level 4 (Resources): Agent loads scripts/references as needed
```

**Analogy**: Think of skills like a library card catalog:
- The **description** is the card (tells you if the book might help)
- The **SKILL.md body** is the table of contents (shows you how to use it)
- The **scripts/references** are the book chapters (loaded only when needed)

### SKILL.md Structure

```markdown
---
name: pdf-processing                    # Required: Skill identifier
description: >                         # Required: When to use this skill
  Extracts text and tables from PDF files, fills PDF forms, and merges 
  multiple PDFs. Use when working with PDF documents or when the user 
  mentions PDFs, forms, or document extraction.
license: MIT                           # Optional: License info
compatibility: Requires PyPDF2, pikepdf # Optional: Environment needs
metadata:                              # Optional: Arbitrary metadata
  author: example-org
  version: "1.0"
allowed-tools: Read Write Bash         # Optional: Pre-approved tools
---

# PDF Processing Skill

## Overview
Brief description of what this skill enables.

## Instructions
1. Step-by-step guidance
2. Tool usage patterns
3. Expected outputs

## Examples
Input → Output patterns for the agent to learn from
```

---

## 2. Skills vs Traditional Workflows

### Traditional LangChain Approach (Hardcoded)

```python
# Traditional: Developer defines every step
def build_research_agent():
    # 1. Define all tools upfront
    tools = [web_search, summarize, save_to_file]
    
    # 2. Bind tools to model
    model = ChatOpenAI().bind_tools(tools)
    
    # 3. Define explicit workflow graph
    workflow = StateGraph(AgentState)
    workflow.add_node("search", search_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("save", save_node)
    workflow.add_edge(START, "search")
    workflow.add_conditional_edges("search", should_summarize)
    
    # 4. Compile and run
    return workflow.compile()

# Problem: To add "code-review" capability, you must:
# - Modify the graph
# - Add new nodes
# - Rewire edges
# - Redeploy
```

### Skills-Based Approach (Declarative)

```python
# Skills: Agent discovers capabilities at runtime
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=model,
    skills=["./skills/"],  # ← Agent scans and discovers
    tools=[generic_search]  # Minimal shared tools
)

# To add "code-review" capability:
# 1. Create skills/code-reviewer/SKILL.md
# 2. Restart agent
# Done. No code changes.
```

### When Traditional Workflows Are Still Required

Skills replace **many** use cases that previously required strict agentic orchestration, but traditional LangGraph workflows remain essential for:

| Scenario | Why Traditional Workflow |
|----------|--------------------------|
| **Compliance workflows** | Specific steps must be taken in order; audit trail required |
| **Safety-critical processes** | High stakes where deviation from process has severe consequences |
| **Regulatory requirements** | Industry mandates (healthcare, finance) require deterministic paths |
| **Human-in-the-loop checkpoints** | Explicit approval gates at known decision points |
| **Forensic auditability** | Every decision point must be inspectable and reproducible |

**The Nuanced View**: Skills excel at *open-ended reasoning tasks* where the agent should adapt to context. Traditional workflows excel at *procedural compliance* where deviation is dangerous or illegal.

### Comparison Matrix

| Aspect | Traditional Workflow | Skills-Based |
|--------|---------------------|--------------|
| **Control** | Developer defines paths | Agent selects capabilities |
| **Extensibility** | Code changes required | Drop-in directories |
| **Routing** | Hardcoded edges/classifiers | LLM-driven description matching |
| **Context Loading** | All tools always loaded | Progressive disclosure |
| **Modularity** | Tightly coupled nodes | Self-contained skill packages |
| **Testing** | Test the whole graph | Test skills in isolation |
| **Sharing** | Copy/paste code | Share skill directories |
| **Compliance** | Explicit, auditable paths | Agent-driven, less predictable |

---

## 3. Benefits of Skills

### 3.1 Token Efficiency via Progressive Disclosure

**Problem**: Traditional agents load all tool descriptions into context.

```
Traditional agent with 20 tools:
- Each tool: ~200 tokens (name + description + args)
- Total: 4,000 tokens before the user even speaks
- Remaining context: 4,000 tokens for actual work

Skills-based agent with 20 skills:
- Each skill (L1): ~50 tokens (name + brief description)
- Total: 1,000 tokens at startup
- When skill activates: +500 tokens
- Effective capacity: 7,000+ tokens for actual work
```

### 3.2 Composability Without Code Changes

**Scenario**: Your agent needs a new capability.

```
Traditional approach:
1. Write code-reviewer node
2. Add to graph
3. Rewire conditional edges
4. Test integration
5. Deploy

Skills approach:
1. Create skills/code-reviewer/SKILL.md
2. Restart agent
3. Done
```

### 3.3 Agent-Driven Discovery

The LLM itself decides which skill to use:

```
System Prompt (excerpt):
---
You have access to skills in the skills/ directory.
You ONLY see names and descriptions initially.
For any specialized task, look for matching skills and use 
`read_file` to load the SKILL.md before executing.

Available skills:
- research: "Conducts comprehensive web research..."
- writer: "Specialized in writing high-quality content..."
- code-reviewer: "Reviews code for bugs and security issues..."
---

User: "Check this Python file for bugs"
Agent: 
  1. Reads skill descriptions
  2. "code-reviewer" matches (mentions "bugs", "Python")
  3. Calls read_file("skills/code-reviewer/SKILL.md")
  4. Follows instructions
```

### 3.4 Separation of Concerns

| Component | Responsibility |
|-----------|---------------|
| **Orchestrator** | Planning, delegation, context management |
| **Skill** | Domain expertise, specialized workflows |
| **Tools** | Low-level capabilities (search, file I/O) |
| **AGENTS.md** | Shared conventions, project context |

### 3.5 Reusability Across Projects

```bash
# Share skills between projects
cp -r ~/projects/agent-a/skills/research ~/projects/agent-b/skills/

# Or maintain a shared skill library
ln -s ~/shared-skills/pdf-processing ./skills/
```

---

## 4. Skill Design Best Practices

### 4.1 The Description is Your Router

**Critical**: The `description` field determines when the skill activates.

**Good Description**:
```yaml
description: >
  Reviews code for bugs, security issues, performance problems, and best 
  practices. Use when the user asks for code review, security audit, or 
  wants feedback on code quality. Do NOT use for writing new code or 
  debugging runtime errors.
```

**Why it works**:
- Clear trigger words: "code review", "security audit", "feedback"
- Explicit boundaries: "Do NOT use for..."
- Specific domain: code quality, not code generation

**Poor Description**:
```yaml
description: "Helps with code stuff."
```

**Why it fails**:
- No trigger words
- Vague scope
- Won't match specific queries

### 4.2 Progressive Disclosure Structure

```markdown
---
# Level 1: ~100 tokens loaded at startup
name: data-analysis
description: Analyzes datasets using pandas, generates visualizations 
  with matplotlib/seaborn. Use when working with CSV, Excel, or JSON data.
---

# Level 2: ~500 tokens loaded on activation
## Overview
This skill enables data analysis workflows including cleaning, 
exploration, visualization, and summary statistics.

## Instructions
1. Load data with pandas
2. Explore with df.head(), df.describe()
3. Clean missing values
4. Generate visualizations
5. Save results

# Level 3: Loaded only when referenced
See [advanced techniques](references/ADVANCED.md) for time series analysis.
```

### 4.3 Skill Granularity Guidelines

| Granularity | When to Use | Example |
|-------------|-------------|---------|
| **Broad** | General domain expertise | `data-analysis`, `web-research` |
| **Medium** | Specific workflow patterns | `csv-cleaning`, `competitor-analysis` |
| **Narrow** | Highly specialized tasks | `pivot-table-creation`, `sentiment-scoring` |

**Rule of thumb**: Start broad, split when the skill exceeds 500 lines or handles multiple distinct use cases.

### 4.4 Anti-Patterns to Avoid

❌ **The Kitchen Sink Skill**:
```yaml
# BAD: One skill for everything
description: "Does research, writing, coding, and data analysis."
```

❌ **The Vague Trigger**:
```yaml
# BAD: Description that matches everything
description: "Helps with tasks."
```

❌ **Deep Nesting**:
```
skills/
└── data/
    └── analysis/
        └── pandas/
            └── advanced/
                └── SKILL.md  # Too deep!
```

✅ **Best Practice**: Flat structure, specific descriptions
```
skills/
├── data-analysis/
├── pandas-advanced/
└── visualization/
```

### 4.5 Include Examples in Instructions

```markdown
## Instructions

### Input Format
Expect: {"csv_path": "./data.csv", "analysis_type": "summary"}

### Output Format
Produce: {"summary_stats": {...}, "output_file": "./workspace/analysis.md"}

### Example Workflow
Input: "Analyze sales.csv for Q4 trends"
Steps:
1. df = pd.read_csv("./sales.csv")
2. q4_data = df[df['quarter'] == 'Q4']
3. trends = q4_data.groupby('product').sum()
4. Save visualization to ./workspace/q4_trends.png
```

---

## 5. Implementation Examples

### Example 1: Minimal Viable Skill

```markdown
# File: skills/hello-world/SKILL.md
---
name: hello-world
description: A simple greeting skill for testing skill loading. 
  Use when the user wants a greeting or says "hello".
---

# Hello World Skill

Say "Hello, World!" and confirm the skill system is working.
```

### Example 2: Research Skill with Scripts

```markdown
# File: skills/web-research/SKILL.md
---
name: web-research
description: >
  Conducts comprehensive web research on any topic using search APIs.
  Use when the user asks for research, information gathering, 
  competitive analysis, or needs current data from the web.
license: MIT
compatibility: Requires internet access and Tavily API key
allowed-tools: internet_search Read Write
---

# Web Research Skill

## Overview
This skill enables systematic web research with source tracking and synthesis.

## Instructions

### 1. Parse the Query
Break the user's request into 2-4 specific search queries.

### 2. Execute Searches
Use the `internet_search` tool for each query:
```python
results = internet_search(query="...", max_results=5)
```

### 3. Synthesize Findings
Combine results into a structured summary with:
- Key findings (3-5 bullet points)
- Sources cited with URLs
- Confidence level (high/medium/low)

### 4. Save Results
Write detailed findings to `./workspace/research-[topic].md`

## Quality Checklist
- [ ] Multiple sources consulted
- [] Conflicting information noted
- [ ] Sources dated within 2 years (if applicable)
```

```python
# File: skills/web-research/scripts/search_helper.py
def deduplicate_results(results):
    """Remove duplicate URLs from search results."""
    seen = set()
    unique = []
    for r in results:
        if r['url'] not in seen:
            seen.add(r['url'])
            unique.append(r)
    return unique
```

### Example 3: Multi-Skill Agent Configuration

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_anthropic import ChatAnthropic

# Configure model
model = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

# Create agent with multiple skills
agent = create_deep_agent(
    model=model,
    
    # Skills: Agent discovers these at runtime
    skills=[
        "./skills/research/",      # Web research capabilities
        "./skills/writer/",        # Content creation
        "./skills/code-reviewer/", # Code quality checks
        "./skills/data-analysis/", # Data processing
    ],
    
    # Memory: Always loaded for shared context
    memory=["./AGENTS.md"],
    
    # Tools: Generic capabilities available to all skills
    tools=[internet_search, execute_code],
    
    # Backend: File system access
    backend=FilesystemBackend(root_dir="."),
    
    # Human-in-the-loop for safety
    interrupt_on={"write_file": True, "execute": True},
)

# Usage
result = agent.invoke({
    "messages": [{"role": "user", "content": "Research AI agents and write a summary"}]
})
```

### Example 4: AGENTS.md (Shared Context)

```markdown
# File: AGENTS.md
---
# Project: Multi-Skill Research Agent

## Conventions
- All skills are stored under `skills/` as directories
- Every skill must have a `SKILL.md` file
- Subagents should be used for complex, multi-step tasks
- All intermediate work goes to `./workspace/`
- Never overwrite existing files without confirmation

## Skill Overview
- **research**: Web search and information synthesis
- **writer**: Content formatting and editing  
- **code-reviewer**: Code quality assessment
- **data-analysis**: Data processing and visualization

## Output Standards
- Research reports: Save to `./workspace/research-[topic].md`
- Code reviews: Save to `./workspace/reviews/[filename].md`
- Data outputs: CSV to `./workspace/data/`, plots to `./workspace/plots/`

## Safety Guidelines
- Confirm before overwriting files
- Never execute arbitrary shell commands
- Flag sensitive data in outputs
```

### Example 5: Subagent with Isolated Skills

```python
# Main agent has broad skills
general_agent = create_deep_agent(
    skills=["./skills/general/"],
    subagents=[
        {
            "name": "security-auditor",
            "description": "Security specialist with focused skills",
            "system_prompt": "You are a security auditor. Be thorough.",
            # Subagent has DIFFERENT, isolated skills
            "skills": ["./skills/security/"],
            "tools": [read_file, static_analysis],
        }
    ]
)

# Security skills are NOT visible to main agent
# Main agent skills are NOT visible to security subagent
```

---

## 6. When to Use Skills — Decision Framework

### Decision Tree

```
Are you building an agent that will:
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
 Handle 3+         Need new         Work with
 distinct          capabilities     multiple
 domains?          monthly?         users/projects?
    │               │               │
    ▼               ▼               ▼
   YES             YES             YES
    │               │               │
    └───────────────┴───────────────┘
                    │
                    ▼
            USE SKILLS
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   Simple task              Complex domain
   (1-2 tools)             expertise
        │                       │
        ▼                       ▼
   SKILL.md with           SKILL.md + scripts/
   instructions            + references/
```

### Quick Reference: Skills vs Tools vs Memory

| Use Case | Choose | Why |
|----------|--------|-----|
| PDF processing workflow | **Skill** | Complex, multi-step, domain-specific |
| Simple web search | **Tool** | Single function, always needed |
| Project conventions | **Memory (AGENTS.md)** | Always relevant, small |
| Code review expertise | **Skill** | Large context, specific triggers |
| User preferences | **Memory** | Persistent, always loaded |

### Skills are Ideal For:

✅ **Multi-domain agents** — Research + Writing + Analysis + Coding
✅ **Evolving capabilities** — Adding new expertise without code changes
✅ **Large context workflows** — Complex instructions that would bloat system prompts
✅ **Team development** — Different team members own different skills
✅ **Reusable expertise** — Same skill across multiple projects

### Skills are Overkill For:

❌ **Single-purpose agents** — A calculator doesn't need skill discovery
❌ **Very simple workflows** — One tool with clear inputs/outputs
❌ **Always-needed capabilities** — Core tools should stay in system prompt

---

## 7. Reference Links

### Official Documentation

| Resource | URL | Description |
|----------|-----|-------------|
| Deep Agents Skills | <https://docs.langchain.com/oss/python/deepagents/skills> | Official skills documentation |
| Agent Skills Specification | <https://agentskills.io/specification> | SKILL.md format specification |
| Deep Agents Overview | <https://docs.langchain.com/oss/python/deepagents/overview> | Core concepts and architecture |
| Subagents | <https://docs.langchain.com/oss/python/deepagents/subagents> | Delegation with isolated skills |
| Memory & AGENTS.md | <https://docs.langchain.com/oss/python/deepagents/customization#memory> | Persistent context patterns |

### Repositories

| Resource | URL | Description |
|----------|-----|-------------|
| Deep Agents | <https://github.com/langchain-ai/deepagents> | Main SDK and CLI |
| LangChain Skills | <https://github.com/langchain-ai/langchain-skills> | Ready-to-use skills |
| Example Skills | <https://github.com/langchain-ai/deepagents/tree/main/libs/cli/examples/skills> | Deep Agent example skills |
| Skills Validator | <https://github.com/agentskills/agentskills/tree/main/skills-ref> | Validation tools |

### Related Concepts

| Resource | URL | Description |
|----------|-----|-------------|
| LangGraph | <https://docs.langchain.com/oss/python/langgraph/overview> | Runtime for agent orchestration |
| LangSmith | <https://docs.langchain.com/langsmith/> | Observability and evaluation |
| MCP Adapters | <https://github.com/langchain-ai/langchain-mcp-adapters> | Model Context Protocol support |

### Community Resources

| Resource | URL | Description |
|----------|-----|-------------|
| Skills Ecosystem | <https://skills.sh> | Community skill registry |
| Vercel Skills CLI | <https://github.com/vercel-labs/skills> | `npx skills` installer |
| DeepWiki Overview | <https://deepwiki.com/langchain-ai/docs/2.3-deep-agents-sdk-documentation> | Community documentation |

---

## Key Takeaways

1. **Skills shift control**: From developer-defined workflows → agent-selected capabilities
2. **Progressive disclosure**: Only load context when needed, save tokens
3. **Description-driven routing**: The `description` field IS your router — invest time in it
4. **Zero-code extensibility**: Add capabilities by dropping in skill directories
5. **Skills ≠ Tools**: Skills are high-level workflows; tools are low-level capabilities
6. **Skills ≠ Memory**: Skills load on-demand; memory loads always

---

*Last Updated: April 2026*
*Target Audience: MSBA Capstone Students studying Agentic AI Architecture*
