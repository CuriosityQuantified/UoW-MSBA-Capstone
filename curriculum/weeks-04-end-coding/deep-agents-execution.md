# Deep Agents: Sandboxes & Streaming

> Reference: [LangChain Deep Agents Sandboxes](https://docs.langchain.com/oss/python/deepagents/sandboxes) | [LangChain Deep Agents Streaming](https://docs.langchain.com/oss/python/deepagents/streaming)

---

## Part 1: Sandboxes

### First Principles

Sandboxes create **isolated execution environments** where agents can run arbitrary code without compromising the host system. They are backends that define where the agent operates, providing a secure boundary between agent execution and your infrastructure.

**Core concept**: Agents generate code, interact with filesystems, and run shell commands. Because we cannot predict what an agent might do, its environment must be isolated from credentials, files, and the network.

### What Are Sandboxes and Why They Matter for Security

Sandboxes are **backends** in Deep Agents that expose:
- Standard filesystem tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`)
- The `execute` tool for running shell commands in an isolated environment
- A security boundary protecting the host system

**Key security benefits:**
- **Isolation**: Agent cannot access host filesystem, environment variables, or other processes
- **Containment**: Code execution happens in a controlled environment
- **Predictability**: Resources are bounded and observable

> **Critical Warning**: Sandboxes protect against host system compromise but do NOT protect against context injection attacks. An attacker controlling part of the agent's input can instruct it to run arbitrary commands *inside the sandbox*.

### Types of Sandboxes

| Type | Provider | Best For |
|------|----------|----------|
| **MicroVM** | AWS AgentCore | AWS-native, Code Interpreter, Python workloads |
| **Serverless** | Modal | ML/AI workloads, GPU access, ephemeral compute |
| **Devbox** | Daytona | TypeScript/Python development, fast cold starts |
| **Disposable** | Runloop | Short-lived isolated code execution |

**Isolation boundaries provided:**
- Filesystem isolation
- Process isolation
- Network access control (configurable per provider)

### Configuring Sandbox Permissions

#### Lifecycle Scoping

| Scope | Pattern | Use Case |
|-------|---------|----------|
| **Thread-scoped (default)** | One sandbox per conversation | Data analysis bots, clean environment per user |
| **Assistant-scoped** | Shared sandbox across all threads for an assistant | Coding assistants with persistent workspaces |

**Example: Thread-scoped with TTL**
```python
from daytona import CreateSandboxFromSnapshotParams, Daytona
from langchain_core.utils.uuid import uuid7

client = Daytona()
thread_id = str(uuid7())

# Get or create sandbox by thread_id with auto-cleanup
try:
    sandbox = client.find_one(labels={"thread_id": thread_id})
except Exception:
    params = CreateSandboxFromSnapshotParams(
        labels={"thread_id": thread_id},
        auto_delete_interval=3600,  # 1 hour TTL
    )
    sandbox = client.create(params)
```

#### File Transfer Patterns

**Two planes of file access:**

1. **Agent filesystem tools**: `read_file`, `write_file`, `edit_file`, `execute` — LLM uses these during execution
2. **Application file transfer APIs**: `upload_files()`, `download_files()` — Your code moves files across the host/sandbox boundary

**Seeding the sandbox:**
```python
# Upload files before agent runs
backend.upload_files([
    ("/src/index.py", b"print('Hello')\n"),
    ("/pyproject.toml", b"[project]\nname = 'my-app'\n"),
])
```

**Retrieving artifacts:**
```python
# Download files after agent finishes
results = backend.download_files(["/output.txt", "/generated_code.py"])
```

### When to Use Sandboxes vs Direct Execution

**Use Sandboxes When:**
- Agent runs arbitrary code (coding agents, data analysis)
- Multiple untrusted users interact with the system
- Network access must be controlled
- File system operations need isolation
- Production deployment with security requirements

**Use Direct Execution When:**
- Tool calls are deterministic and limited
- All tools are read-only and safe
- Performance overhead of sandbox is unacceptable
- Agent operates only on pre-validated data

### Security Best Practices

#### ⚠️ NEVER Put Secrets Inside Sandboxes

API keys, tokens, and credentials inside a sandbox can be read and exfiltrated by a context-injected agent.

**Safe patterns for handling secrets:**

1. **Keep secrets in host-side tools** (Recommended)
   ```python
   # Tools run in host environment, agent calls by name
   @tool
   def call_secure_api(query: str) -> str:
       """Makes authenticated API call."""
       api_key = os.environ["API_KEY"]  # Agent never sees this
       return requests.get("https://api.example.com", 
                          headers={"Authorization": api_key}).json()
   ```

2. **Use network proxies with credential injection** (Provider-dependent)
   - Some providers support proxies that intercept requests and attach credentials
   - Agent makes plain HTTP requests, proxy adds auth headers

#### Additional Security Measures

| Risk | Mitigation |
|------|------------|
| Context injection | Human-in-the-loop approval for all tool calls |
| Network exfiltration | Block network access when not needed (`blockNetwork: true` on Modal) |
| Secret exposure | Use host-side tools for authenticated operations |
| Unexpected output | Review sandbox outputs before acting on them |
| Sensitive data leakage | Use middleware to filter/redact sensitive patterns |

### Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| **Assistant-scoped sandbox bloat** | Configure TTL, use snapshots to reset periodically, implement cleanup logic |
| **API keys in sandbox env vars** | Never pass secrets via environment variables to sandboxes |
| **Network access by default** | Explicitly disable network when not needed |
| **Large output handling** | Provider automatically saves large output to file; use `read_file` incrementally |
| **Tool call ID mismatch** | Use `pregel_id` from namespace to track subagent lifecycle accurately |

### Configuration Examples

**Modal Sandbox:**
```python
import modal
from langchain_modal import ModalSandbox
from deepagents import create_deep_agent

app = modal.App.lookup("your-app")
modal_sandbox = modal.Sandbox.create(app=app, blockNetwork=True)
backend = ModalSandbox(sandbox=modal_sandbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-20250514"),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)
```

**Daytona Sandbox:**
```python
from daytona import Daytona
from langchain_daytona import DaytonaSandbox
from deepagents import create_deep_agent

sandbox = Daytona().create()
backend = DaytonaSandbox(sandbox=sandbox)

agent = create_deep_agent(
    backend=backend,
    system_prompt="You are a coding assistant with sandbox access.",
)
```

**Runloop Sandbox:**
```python
from runloop_api_client import RunloopSDK
from langchain_runloop import RunloopSandbox

client = RunloopSDK(bearer_token=os.environ["RUNLOOP_API_KEY"])
devbox = client.devbox.create()
backend = RunloopSandbox(devbox=devbox)
```

---

## Part 2: Streaming

### First Principles

Streaming provides **real-time visibility** into agent execution. Instead of waiting for the entire run to complete, updates flow continuously to the client, enabling responsive UIs and progress tracking.

**Core concept**: Build on LangGraph's streaming infrastructure with first-class support for subagent streams. Each subagent's execution can be tracked independently.

### Why Streaming Matters for UX

**Benefits of streaming:**
- **Perceived performance**: Users see progress immediately, reducing wait anxiety
- **Transparency**: Users understand what the agent is doing (tool calls, subagent delegation)
- **Interactivity**: Real-time progress bars, token display, and status updates
- **Debugging**: Developers observe execution flow for troubleshooting

**When streaming is essential:**
- Multi-step agent workflows with subagents
- Long-running tasks (>5 seconds)
- User-facing applications where responsiveness matters
- Complex tool calling scenarios

### Streaming Patterns

#### 1. Subagent Progress (`stream_mode="updates"`)

Track each subagent's execution as it runs:

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Research quantum computing"}]},
    stream_mode="updates",
    subgraphs=True,
    version="v2",
):
    if chunk["type"] == "updates":
        if not chunk["ns"]:  # Empty namespace = main agent
            print(f"[main agent] {chunk['data']}")
        else:  # Non-empty namespace = subagent
            print(f"[{chunk['ns'][0]}] {chunk['data']}")
```

#### 2. LLM Tokens (`stream_mode="messages"`)

Stream individual tokens from main agent and subagents:

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Research quantum computing"}]},
    stream_mode="messages",
    subgraphs=True,
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        
        # Check if from subagent
        is_subagent = any(s.startswith("tools:") for s in chunk["ns"])
        
        if token.content:
            print(token.content, end="", flush=True)
```

#### 3. Tool Calls

Monitor tool invocations in real-time:

```python
for chunk in agent.stream(..., stream_mode="messages", subgraphs=True, version="v2"):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        
        # Tool call chunks stream incrementally
        if token.tool_call_chunks:
            for tc in token.tool_call_chunks:
                if tc.get("name"):
                    print(f"Tool call: {tc['name']}")
                if tc.get("args"):
                    print(tc["args"], end="", flush=True)
        
        # Tool results
        if token.type == "tool":
            print(f"Result: {token.content}")
```

#### 4. State Updates / Custom Events (`stream_mode="custom"`)

Emit user-defined progress signals from inside tools:

```python
from langgraph.config import get_stream_writer

@tool
def analyze_data(topic: str) -> str:
    writer = get_stream_writer()
    
    writer({"status": "starting", "progress": 0})
    # ... do work ...
    writer({"status": "analyzing", "progress": 50})
    # ... do more work ...
    writer({"status": "complete", "progress": 100})
    
    return "Analysis complete"
```

### Implementation Approaches

#### Namespace-Based Routing

Every streaming event includes a **namespace** identifying its source:

| Namespace | Source |
|-----------|--------|
| `()` (empty) | Main agent |
| `("tools:abc123",)` | Subagent spawned by tool call `abc123` |
| `("tools:abc123", "model_request:def456") | Node inside subagent |

```python
# Route events to correct UI component
for chunk in agent.stream(..., subgraphs=True):
    is_subagent = any(segment.startswith("tools:") 
                      for segment in chunk["ns"])
    
    if is_subagent:
        tool_call_id = next(
            s.split(":")[1] for s in chunk["ns"] 
            if s.startswith("tools:")
        )
        ui.update_subagent(tool_call_id, chunk["data"])
    else:
        ui.update_main_agent(chunk["data"])
```

#### Multi-Mode Streaming

Combine modes for complete execution visibility:

```python
INTERESTING_NODES = {"model_request", "tools"}

for chunk in agent.stream(
    {"messages": [...]},
    stream_mode=["updates", "messages", "custom"],  # Multiple modes
    subgraphs=True,
    version="v2",
):
    if chunk["type"] == "updates":
        # Track step completion
        for node_name in chunk["data"]:
            if node_name in INTERESTING_NODES:
                print(f"Step: {node_name}")
    
    elif chunk["type"] == "messages":
        # Stream tokens
        token, metadata = chunk["data"]
        if token.content:
            print(token.content, end="", flush=True)
    
    elif chunk["type"] == "custom":
        # Custom progress events
        print(f"Progress: {chunk['data']}")
```

### Frontend Integration Considerations

#### v2 Streaming Format

**Always use `version="v2"`** (requires LangGraph >= 1.1):

```python
# v2 format - unified, consistent structure
for chunk in agent.stream(..., version="v2"):
    print(chunk["type"])   # "updates", "messages", "custom"
    print(chunk["ns"])     # Namespace tuple
    print(chunk["data"])   # Payload
```

**Benefits of v2:**
- No nested tuple unpacking
- Consistent shape regardless of modes or subgraphs
- Easier type narrowing and deserialization

#### Subagent Lifecycle Tracking

```python
active_subagents = {}

for chunk in agent.stream(..., stream_mode="updates", subgraphs=True, version="v2"):
    if chunk["type"] == "updates":
        for node_name, data in chunk["data"].items():
            
            # Detect subagent starting
            if not chunk["ns"] and node_name == "model_request":
                for msg in data.get("messages", []):
                    for tc in getattr(msg, "tool_calls", []):
                        if tc["name"] == "task":
                            active_subagents[tc["id"]] = {
                                "type": tc["args"].get("subagent_type"),
                                "status": "pending"
                            }
            
            # Detect subagent running
            if chunk["ns"] and chunk["ns"][0].startswith("tools:"):
                # Mark any pending subagent as running
                for sub_id, sub in active_subagents.items():
                    if sub["status"] == "pending":
                        sub["status"] = "running"
                        break
            
            # Detect subagent completing
            if not chunk["ns"] and node_name == "tools":
                for msg in data.get("messages", []):
                    if msg.type == "tool":
                        sub = active_subagents.get(msg.tool_call_id)
                        if sub:
                            sub["status"] = "complete"
```

### Error Handling During Streams

| Scenario | Pattern |
|----------|---------|
| **Token streaming errors** | Handle in token processing loop; partial content is still valuable |
| **Tool call failures** | Check `token.type == "tool"` for error content |
| **Subagent crashes** | Namespace stops receiving events; implement timeout detection |
| **Network interruptions** | Implement reconnection logic with last-event-id tracking |
| **Large output overflow** | Provider saves to file; agent instructed to use `read_file` incrementally |

**Graceful degradation:**
```python
try:
    for chunk in agent.stream(..., subgraphs=True, version="v2"):
        # Process chunk
        process_chunk(chunk)
except Exception as e:
    # Log error, update UI with failure state
    logger.error(f"Stream failed: {e}")
    ui.show_error("Connection interrupted. Please retry.")
```

### Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| **v1 format confusion** | Always specify `version="v2"` for consistent structure |
| **Namespace parsing errors** | Check `chunk["ns"]` is truthy before accessing elements |
| **Tool call ID vs Pregel ID mismatch** | Use `pregel_id` from namespace for tracking, not `tool_call_id` |
| **Missing `subgraphs=True`** | Required to receive subagent events |
| **UI blocking on stream** | Process stream in background, update UI async |
| **Partial token display** | Use `end="", flush=True` when printing tokens |

### When to Use / When Not to Use

**Use Streaming When:**
- Building user-facing applications
- Running multi-agent workflows with subagents
- Long-running tasks (>5 seconds)
- Need real-time progress visibility
- Debugging complex agent behavior

**Skip Streaming When:**
- Simple, fast tool calls (<1 second)
- Backend-only processing without UI
- Batch jobs where progress doesn't matter
- Resource-constrained environments

---

## Reference Links

### Sandboxes
- [LangChain Sandboxes Documentation](https://docs.langchain.com/oss/python/deepagents/sandboxes)
- [AWS AgentCore Integration](https://docs.langchain.com/oss/python/integrations/providers/aws)
- [Modal Integration](https://docs.langchain.com/oss/python/integrations/providers/modal)
- [Daytona Integration](https://docs.langchain.com/oss/python/integrations/providers/daytona)
- [Runloop Integration](https://docs.langchain.com/oss/python/integrations/providers/runloop)
- [Going to Production Guide](https://docs.langchain.com/oss/python/deepagents/going-to-production)

### Streaming
- [LangChain Streaming Documentation](https://docs.langchain.com/oss/python/deepagents/streaming)
- [Frontend Streaming with useStream](https://docs.langchain.com/oss/python/deepagents/streaming/frontend)
- [LangGraph Streaming Guide](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Subagents Documentation](https://docs.langchain.com/oss/python/deepagents/subagents)

### SDK Reference
- [BaseSandbox Class](https://reference.langchain.com/python/deepagents/backends/sandbox/BaseSandbox)
- [SandboxBackendProtocol](https://reference.langchain.com/python/deepagents/backends/protocol/SandboxBackendProtocol)
- [get_stream_writer](https://reference.langchain.com/python/langgraph/config/get_stream_writer)
