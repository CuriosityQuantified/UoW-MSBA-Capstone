# Agent Memory & Human-in-the-Loop

**Week 3 Architecture Deep Dive | UoW MSBA Capstone**

*Memory architecture and HITL patterns, with [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/) as a reference implementation.*

---

## 1. MEMORY ARCHITECTURE

### 1.1 Memory Types in Agent Systems

Agent frameworks like Deep Agents implement four primary memory types, each serving distinct cognitive functions:

#### Working Memory (Short-Term)
- **What it is**: Conversation history, scratch files, and intermediate reasoning within a single session
- **Scope**: Single conversation/thread
- **Implementation**: Managed automatically as part of the agent's [state](https://docs.langchain.com/oss/python/langgraph/graph-api#state)
- **Lifecycle**: Ephemeral—cleared when the thread ends (unless checkpointer is used)

#### Episodic Memory
- **What it is**: Records of past experiences—what happened, in what order, and what the outcome was
- **Scope**: Cross-conversation; preserves full conversational context
- **Implementation**: Built on [checkpointers](https://docs.langchain.com/oss/python/langgraph/persistence#checkpoints); every conversation persisted as a checkpointed thread
- **Use case**: Recalling *how* a problem was solved, not just *what* was learned
- **Example**: A coding agent looking back at a past debugging session to skip to the likely root cause

#### Semantic Memory
- **What it is**: Facts, preferences, and learned knowledge stored in structured files
- **Scope**: Persistent across all conversations (when properly configured)
- **Implementation**: Filesystem-backed memory via `memory=` parameter and backends
- **Use case**: User preferences, agent persona evolution, accumulated expertise

#### Procedural Memory (Skills)
- **What it is**: Reusable instructions telling the agent *how* to perform a task
- **Scope**: Can be agent-scoped or user-scoped
- **Implementation**: Passed via `skills=` parameter; loaded on-demand
- **Pattern**: Agent reads only skill descriptions at startup, full skill file only when matched

### 1.2 Memory Type Decision Framework

| If you need... | Use | Example |
|---------------|-----|---------|
| Conversation context within one chat | Working memory | Multi-turn reasoning, maintaining context |
| Recall past problem-solving sessions | Episodic memory | "I fixed this bug before—let me check how" |
| User preferences that persist | Semantic memory | "User prefers Python examples" |
| Reusable task instructions | Procedural memory (skills) | "How to fetch LangGraph docs" |
| Cross-user organization policies | Read-only semantic memory | Compliance rules, shared knowledge bases |

### 1.3 Memory Persistence Patterns

#### Hot Path (Default)
- **When**: Agent writes memories during the conversation
- **Pros**: Memories available immediately, transparent to user
- **Cons**: Adds latency; agent must multitask

#### Background Consolidation ("Sleep Time Compute")
- **When**: Separate agent processes memories between conversations via cron job
- **Pros**: No user-facing latency; can synthesize across multiple conversations
- **Cons**: Memories not available until next conversation; requires second agent

**Consolidation Agent Pattern:**
```python
# consolidation_agent.py
from deepagents import create_deep_agent
from langchain.tools import tool, ToolRuntime
from langgraph_sdk import get_client

sdk_client = get_client(url="<DEPLOYMENT_URL>")

@tool
async def search_recent_conversations(query: str, runtime: ToolRuntime) -> str:
    """Search this user's conversations updated in the last 6 hours."""
    user_id = runtime.server_info.user.identity
    since = datetime.now(timezone.utc) - timedelta(hours=6)
    threads = await sdk_client.threads.search(
        metadata={"user_id": user_id},
        updated_after=since.isoformat(),
        limit=20,
    )
    # ... process and return conversations

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    system_prompt="""Review recent conversations and update the user's memory file.
Merge new facts, remove outdated information, and keep it concise.""",
    tools=[search_recent_conversations],
)
```

**Cron Schedule (keep in sync with lookback window):**
```python
cron_job = await client.crons.create(
    assistant_id="consolidation_agent",
    schedule="0 */6 * * *",  # Every 6 hours
    input={"messages": [{"role": "user", "content": "Consolidate recent memories."}]},
)
```

### 1.4 Cross-Session vs Within-Session Memory

#### Within-Session (Working Memory)
- Lives in the thread's state
- Automatically managed by LangGraph
- Cleared at thread end (unless persisted via checkpointer)
- Used for immediate context, multi-turn reasoning

#### Cross-Session (Long-Term Memory)
- Lives in external store (InMemoryStore, PostgresStore, etc.)
- Survives thread termination
- Explicitly configured via `memory=` and backends
- Used for persistent learning and user preferences

### 1.5 Memory Scoping Strategies

| Scope | Namespace | Use Case |
|-------|-----------|----------|
| **User-scoped** | `(user_id,)` | Per-user preferences, isolated memories |
| **Agent-scoped** | `(assistant_id,)` | Shared agent persona, learned skills |
| **Organization-scoped** | `(org_id,)` | Compliance policies, shared knowledge |
| **Combined** | `(assistant_id, user_id)` | Per-agent, per-user isolation |

**User-Scoped Memory Example:**
```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

agent = create_deep_agent(
    memory=["/memories/preferences.md"],
    skills=["/skills/"],
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda ctx: (ctx.runtime.context.user_id,),
            ),
            "/skills/": StoreBackend(
                namespace=lambda ctx: (ctx.runtime.context.user_id,),
            ),
        },
    ),
)
```

### 1.6 Memory Retrieval and Context Injection

#### Load-at-Startup Pattern (Default)
- Memory files loaded into system prompt at agent initialization
- All relevant context available from turn 1
- Trade-off: Larger context window consumption

#### On-Demand Loading Pattern (Skills)
- Only descriptions loaded at startup
- Full content loaded only when skill is matched to task
- Keeps context lean until capability is needed

**Episodic Memory Retrieval (Thread Search):**
```python
from langgraph_sdk import get_client
from langchain.tools import tool, ToolRuntime

client = get_client(url="<DEPLOYMENT_URL>")

@tool
async def search_past_conversations(query: str, runtime: ToolRuntime) -> str:
    """Search past conversations for relevant context."""
    user_id = runtime.server_info.user.identity
    threads = await client.threads.search(
        metadata={"user_id": user_id},
        limit=5,
    )
    results = []
    for thread in threads:
        history = await client.threads.get_history(thread_id=thread["thread_id"])
        results.append(history)
    return str(results)
```

### 1.7 Read-Only vs Writable Memory

| Permission | Use Case | Population Method |
|-----------|----------|-------------------|
| **Read-write** (default) | User preferences, agent self-improvement | Agent uses `edit_file` tool |
| **Read-only** | Organization policies, compliance rules, dev-defined skills | Application code or Store API |

**Security Consideration:** If one user can write memory that another reads, malicious users could inject instructions into shared state. Mitigations:
- Default to user scope unless sharing is required
- Use read-only memory for shared policies
- Add HITL validation before writes to sensitive paths

**Enforcing Read-Only with Policy Hooks:**
```python
# Use policy hooks on backend to reject writes to specific paths
# See: https://docs.langchain.com/oss/python/deepagents/backends#add-policy-hooks
```

### 1.8 Memory Anti-Patterns

| Anti-Pattern | Why It's Bad | Better Approach |
|-------------|--------------|---------------|
| Storing everything in one file | Concurrent write conflicts, hard to manage | Separate files by topic/concern |
| Agent-scoped memory for user PII | Data leakage between users | Always use user-scoped for PII |
| Writable organization policies | Prompt injection vulnerability | Make org memory read-only |
| Loading all episodic memory into context | Context overflow, token waste | Search and retrieve selectively |
| No checkpointer with long-running agents | State loss on interruption | Always configure checkpointer |
| Ignoring namespace conflicts | Race conditions, data corruption | Use proper scoping (assistant_id, user_id) |

### 1.9 Memory First Principles

1. **Context is a scarce resource**: Not all memory belongs in the prompt—load only what's relevant
2. **Privacy is not automatic**: Explicit scoping is required to prevent data leakage
3. **Writes are dangerous**: Any memory the agent can write is a potential injection vector
4. **Persistence is explicit**: Working memory dies with the thread; long-term memory requires configuration
5. **Synthesis beats storage**: Raw episodic memory is expensive; background consolidation extracts value

---

## 2. HUMAN-IN-THE-LOOP (HITL)

### 2.1 When to Use HITL

HITL serves three primary purposes in agent systems:

#### Approval
- **When**: Before irreversible or sensitive operations
- **Examples**: Deleting files, sending emails, financial transactions, deploying to production
- **Why**: Prevents costly mistakes; maintains human accountability

#### Guidance
- **When**: When the agent encounters ambiguity or novel situations
- **Examples**: Clarifying user intent, choosing between valid approaches, requesting missing information
- **Why**: Improves decision quality; keeps agent aligned with user goals

#### Correction
- **When**: When the agent's proposed action is wrong but fixable
- **Examples**: Wrong recipient in email, incorrect file path, suboptimal approach
- **Why**: Reduces error rate; provides learning signal for agent improvement

### 2.2 HITL Decision Framework

| Risk Level | Example Operations | HITL Configuration |
|-----------|-------------------|-------------------|
| **High** | Delete files, send external communications, financial ops, production deploys | `{"allowed_decisions": ["approve", "edit", "reject"]}` |
| **Medium** | Write files, update configurations, modify user data | `{"allowed_decisions": ["approve", "reject"]}` |
| **Low** | Read files, list directories, search operations | `False` (no interrupts) |
| **Critical** (must not reject) | Safety-critical operations where stopping is worse than proceeding | `{"allowed_decisions": ["approve"]}` |

### 2.3 Implementation Patterns

#### Basic Configuration
```python
from langchain.tools import tool
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

@tool
def delete_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted {path}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Sent email to {to}"

# Checkpointer is REQUIRED for HITL
checkpointer = MemorySaver()

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    tools=[delete_file, send_email],
    interrupt_on={
        "delete_file": True,  # Default: approve, edit, reject
        "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
    },
    checkpointer=checkpointer  # Required!
)
```

#### Handling Interrupts
```python
from langchain_core.utils.uuid import uuid7
from langgraph.types import Command

# Create config with thread_id for state persistence
config = {"configurable": {"thread_id": str(uuid7())}}

# Invoke the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Delete the file temp.txt"}]},
    config=config,
    version="v2",  # Required for interrupt handling
)

# Check if execution was interrupted
if result.interrupts:
    interrupt_value = result.interrupts[0].value
    action_requests = interrupt_value["action_requests"]
    review_configs = interrupt_value["review_configs"]

    # Create lookup map from tool name to review config
    config_map = {cfg["action_name"]: cfg for cfg in review_configs}

    # Display pending actions to user
    for action in action_requests:
        review_config = config_map[action["name"]]
        print(f"Tool: {action['name']}")
        print(f"Arguments: {action['args']}")
        print(f"Allowed decisions: {review_config['allowed_decisions']}")

    # Get user decisions (one per action_request, in order)
    decisions = [{"type": "approve"}]  # Or "edit", "reject"

    # Resume execution
    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,  # Must use same config!
        version="v2",
    )
```

#### Editing Tool Arguments
```python
if result.interrupts:
    interrupt_value = result.interrupts[0].value
    action_request = interrupt_value["action_requests"][0]

    # User modifies the proposed action
    decisions = [{
        "type": "edit",
        "edited_action": {
            "name": action_request["name"],  # Must include tool name
            "args": {"to": "team@company.com", "subject": "...", "body": "..."}
        }
    }]

    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,
        version="v2",
    )
```

### 2.4 Interrupt and Resume Mechanics

#### State Persistence Flow
```
Agent invokes tool → Interrupt triggered → State saved to checkpointer
                                    ↓
Human reviews and decides → Resume with Command → State restored → Continue execution
```

#### Key Requirements
1. **Checkpointer is mandatory**: Without it, state is lost on interrupt
2. **Thread ID must persist**: Same `config` with same `thread_id` required for resume
3. **Version must be "v2"**: Interrupt handling requires v2 API
4. **Decisions match action order**: One decision per action request, in same order

#### Multiple Tool Calls
When multiple tools need approval, all interrupts are batched:
```python
if result.interrupts:
    interrupt_value = result.interrupts[0].value
    action_requests = interrupt_value["action_requests"]

    # Two tools need approval
    assert len(action_requests) == 2

    # Provide decisions in same order as action_requests
    decisions = [
        {"type": "approve"},  # First tool
        {"type": "reject"}    # Second tool
    ]

    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,
        version="v2",
    )
```

### 2.5 Subagent Interrupts

#### Interrupts on Tool Calls
Each subagent can have its own `interrupt_on` configuration:
```python
agent = create_deep_agent(
    tools=[delete_file, read_file],
    interrupt_on={
        "delete_file": True,
        "read_file": False,
    },
    subagents=[{
        "name": "file-manager",
        "description": "Manages file operations",
        "system_prompt": "You are a file management assistant.",
        "tools": [delete_file, read_file],
        "interrupt_on": {
            "delete_file": True,
            "read_file": True,  # Different from main agent!
        }
    }],
    checkpointer=checkpointer
)
```

#### Interrupts Within Tool Calls (Direct Interrupt)
Subagent tools can call `interrupt()` directly:
```python
from langgraph.types import interrupt

@tool(description="Request human approval before proceeding.")
def request_approval(action_description: str) -> str:
    """Request human approval using the interrupt() primitive."""
    approval = interrupt({
        "type": "approval_request",
        "action": action_description,
        "message": f"Please approve or reject: {action_description}",
    })

    if approval.get("approved"):
        return f"Action '{action_description}' was APPROVED."
    else:
        return f"Action '{action_description}' was REJECTED. Reason: {approval.get('reason', 'No reason provided')}"
```

### 2.6 UI/UX Considerations

#### Decision Type UX Patterns
| Decision | UI Pattern | User Action |
|----------|-----------|-------------|
| `approve` | Confirmation dialog | Click "Approve" or "Confirm" |
| `edit` | Inline editing | Modify fields, then confirm |
| `reject` | Cancel/Decline button | Click "Reject" with optional reason |

#### Best Practices
1. **Show context**: Display the full tool call with arguments, not just the tool name
2. **Explain stakes**: For high-risk operations, explain what will happen
3. **Batch intelligently**: Group related approvals; don't overwhelm with too many at once
4. **Preserve state**: If user refreshes, they should return to the same decision point
5. **Support async**: Allow users to return later; don't require immediate response

### 2.7 Security and Approval Workflows

#### Security Layers
```
┌─────────────────────────────────────────┐
│  Layer 1: Tool Selection              │
│  Don't give dangerous tools to agents  │
├─────────────────────────────────────────┤
│  Layer 2: interrupt_on configuration  │
│  Require approval for sensitive ops    │
├─────────────────────────────────────────┤
│  Layer 3: Read-only memory            │
│  Prevent injection via shared state    │
├─────────────────────────────────────────┤
│  Layer 4: Audit logging               │
│  Trace all decisions in LangSmith      │
└─────────────────────────────────────────┘
```

#### Approval Workflow Integration
```python
# Example: Multi-stage approval for financial transactions
interrupt_on = {
    "initiate_transfer": {"allowed_decisions": ["approve", "reject"]},
    "confirm_transfer": {"allowed_decisions": ["approve"]},  # Cannot reject at final stage
}
```

#### Audit and Compliance
- Use [LangSmith tracing](https://docs.langchain.com/langsmith/trace-with-langgraph) to audit all HITL decisions
- Every approval/reject/edit appears in the trace
- Maintain decision logs for compliance requirements

### 2.8 HITL Anti-Patterns

| Anti-Pattern | Why It's Bad | Better Approach |
|-------------|--------------|---------------|
| Interrupting on every tool call | User fatigue, slow execution | Only interrupt on high-risk operations |
| Not using checkpointer | State loss on interrupt; broken UX | Always configure checkpointer |
| Changing thread_id on resume | New thread created; state lost | Use identical config for resume |
| Not using version="v2" | Interrupts won't work properly | Always specify version="v2" |
| Async decisions without timeout | Stalled threads, resource leaks | Implement decision timeouts |
| Unclear decision UI | Users confused about what they're approving | Show full context and consequences |
| Missing reject reasons | No learning signal for agent | Require reason on reject |

### 2.9 HITL First Principles

1. **Trust but verify**: Agents get capabilities; humans verify high-stakes usage
2. **Fail closed**: When in doubt, interrupt; better to ask permission than forgiveness
3. **Preserve momentum**: State persistence lets users resume without losing context
4. **Security in layers**: HITL is one layer; combine with memory scoping and tool selection
5. **Human time is expensive**: Don't interrupt for trivial decisions—batch and prioritize

---

## 3. INTEGRATED PATTERNS

### Memory + HITL for Sensitive Writes

When the agent writes to shared memory (organization policies, other users' data), combine patterns:

```python
# Require HITL before agent can edit shared memory
interrupt_on = {
    "edit_file": {
        "allowed_decisions": ["approve", "edit", "reject"],
        # Only require approval for shared memory paths
        "path_filter": ["/policies/", "/org-memory/"]
    }
}

# Make org memory read-only by default
backend = CompositeBackend(
    routes={
        "/memories/": StoreBackend(namespace=lambda ctx: (ctx.runtime.context.user_id,)),
        "/policies/": StoreBackend(
            namespace=lambda ctx: (ctx.runtime.context.org_id,),
            read_only=True,  # Enforce at backend level
        ),
    }
)
```

### Progressive Trust Pattern

```python
# New users: High oversight
interrupt_on_new_user = {
    "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
    "write_file": {"allowed_decisions": ["approve", "reject"]},
}

# Established users: Lower oversight (based on trust score in memory)
interrupt_on_trusted_user = {
    "send_email": {"allowed_decisions": ["approve", "reject"]},  # No edit—trust their judgment
    "write_file": False,  # No interrupt
}
```

---

## 4. REFERENCE LINKS

### Primary Documentation
- [Deep Agents Memory](https://docs.langchain.com/oss/python/deepagents/memory)
- [Deep Agents HITL](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
- [Deep Agents Backends](https://docs.langchain.com/oss/python/deepagents/backends)
- [Deep Agents Skills](https://docs.langchain.com/oss/python/deepagents/skills)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

### Related Concepts
- [LangGraph Checkpoints](https://docs.langchain.com/oss/python/langgraph/persistence#checkpoints)
- [LangSmith Cron Jobs](https://docs.langchain.com/langsmith/cron-jobs)
- [LangSmith Tracing](https://docs.langchain.com/langsmith/trace-with-langgraph)
- [LangGraph Store](https://docs.langchain.com/langsmith/custom-store)

### Advanced Topics
- [Context Engineering](https://docs.langchain.com/oss/python/deepagents/context-engineering)
- [Going to Production](https://docs.langchain.com/oss/python/deepagents/going-to-production)

---

## 5. QUICK DECISION CHEAT SHEET

| Question | Memory Answer | HITL Answer |
|----------|---------------|-------------|
| "User preferences?" | User-scoped semantic memory | Not needed |
| "Org policies?" | Read-only org-scoped memory | Approve writes |
| "Debug similar issue?" | Episodic memory search | Not needed |
| "Delete production data?" | Log to episodic memory | Require approval |
| "Agent learns new skill?" | Agent-scoped procedural memory | Approve if shared |
| "Send email externally?" | Log to episodic memory | Require approval |

---

*Document compiled from LangChain Deep Agents documentation (April 2025)*
