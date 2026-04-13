"""
UW MSBA AI Proxy
A simple Modal-hosted proxy for Fireworks AI inference.
Students hit this endpoint with a shared secret - no API keys distributed.

ARCHITECTURE & CODING METHODOLOGY
=================================

This proxy is built following AI-native development principles:
https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle

The Two-Loop System in This Codebase:
--------------------------------------

1. BUILD LOOP (Engineering - this proxy)
   - Fast iteration: Modal serverless for zero-maintenance deployment
   - Quality curated: Rate limiting, auth validation, error handling
   - Build to reveal: Logging middleware captures usage patterns
   
   Key decisions revealing problem understanding:
   - Serverless (Modal) → No uptime burden on instructor
   - Shared secret auth → No key distribution risk
   - Global rate limiting → Fair resource allocation across class
   - Model name mapping → Student-friendly API (kimi-k2.5-fast vs Fireworks path)

2. INSIGHT LOOP (Product/Observability - student-managed)
   - Spec-first: Students write behavior specs before building
   - Eval-driven: Langfuse captures traces for continuous evaluation
   - Synthesis: Students review their Langfuse dashboards to understand usage

   Students bring their own Langfuse projects → Complete observability ownership
   The proxy is "dumb" by design → It just proxies, students instrument client-side

Spec-First Design Decisions:
----------------------------
Before writing this code, the behavior spec was:
- MUST: Authenticate students without distributing API keys
- MUST: Enforce global rate limits (60 req/min)
- MUST: Support streaming for real-time UX
- MUST: Map friendly model names to provider paths
- MUST NOT: Store or log student prompts (privacy)
- MUST NOT: Add latency beyond proxy overhead
- WRONG LOOKS LIKE: Students hitting rate limits, 500 errors exposed

Eval Criteria (Binary Pass/Fail):
-------------------------------
- [ ] Health check responds < 100ms
- [ ] Invalid auth returns 401 with helpful message
- [ ] Valid request forwards to Fireworks < 500ms (cold start excluded)
- [ ] Streaming responses work without buffering
- [ ] Rate limit enforces 60 req/min globally
- [ ] Model name mapping works for all supported models
- [ ] Errors from Fireworks are forwarded (not masked)

Continuous Evaluation:
--------------------
The logging middleware captures:
- Method, path, status code, duration
- Used to evaluate: Are students hitting limits? Is latency acceptable?

Modal dashboard provides:
- Request volume, error rates, cold start patterns
- Used to evaluate: Is the proxy scaling correctly?

This is "spec-as-source" — the spec lives in comments, evals run in production.

HARNESSES & MEMORY OWNERSHIP
=============================

Key insight from LangChain (https://blog.langchain.com/your-harness-your-memory/):

"Asking to plug memory into an agent harness is like asking to plug driving into 
a car. Managing context, and therefore memory, is a core capability and 
responsibility of the agent harness."

Why this proxy is stateless by design:
--------------------------------------
- No student prompts stored in our infrastructure (privacy)
- No conversation state trapped in our system (portability)
- Students bring their own Langfuse → They own their observability/memory
- We provide inference only → No lock-in to our harness

The lock-in risk we avoid:
--------------------------
Closed harnesses behind APIs (Claude Managed Agents, OpenAI Responses API) store 
memory you can't access or transfer. Even "open" harnesses like Codex use encrypted 
compaction that only works in their ecosystem.

This codebase demonstrates open harness principles:
- Code you can read, modify, and deploy yourself
- State that lives in YOUR systems (Langfuse), not ours
- The freedom to swap models, providers, or observability tools

PRODUCTION PATTERNS REFERENCE
=============================

For studying how production agents are built:
- GitHub: https://github.com/alejandrobalderas/claude-code-from-source
- Web: https://claude-code-from-source.com/

Key patterns applicable to this codebase:
- Stateless request handling (no memory trapped in proxy)
- Two-phase configuration (secrets at startup, auth per request)
- Speculative execution potential (could add read-only tool prefetch)
- Context efficiency (minimal proxy overhead, streaming support)

The 4-layer compression concept (snip, microcompact, collapse, autocompact)
doesn't apply here because we're stateless — but students should know it
exists for when they build stateful agents.

CODING PRINCIPLES REFERENCE
===========================

For improving agent behavior:
https://github.com/forrestchang/andrej-karpathy-skills

Four principles from Andrej Karpathy's observations:
- Think Before Coding: State assumptions, surface tradeoffs, stop when confused
- Simplicity First: No speculative features, no premature abstraction
- Surgical Changes: Touch only what you must, clean up only your mess
- Goal-Driven Execution: Transform "add validation" → "write tests, make them pass"

Key insight: "Don't tell it what to do, give it success criteria and watch it go."
Include these in CLAUDE.md or AGENTS.md for better agent behavior.

PRODUCTION SKILL REFERENCE
==========================

For building your own skills:
https://github.com/addyosmani/agent-skills

6-phase lifecycle with 20 production-grade skills:
- /spec → /plan → /build → /test → /review → /ship
- spec-driven-development: PRD before any code
- incremental-implementation: Thin vertical slices, feature flags
- test-driven-development: Red-Green-Refactor, 80/15/5 pyramid
- code-review-and-quality: Five-axis review, ~100 line changes
- debugging-and-error-recovery: Five-step triage, stop-the-line

Reference these patterns when writing SKILL.md files for your projects.

SKILL UTILITY RESEARCH
======================

Recent research on skill effectiveness under realistic conditions:
https://arxiv.org/abs/2604.04323

Key insight: Skill benefits are FRAGILE without proper retrieval.
- Hand-curated skills → High performance (idealized benchmarks)
- Retrieved from 34k real skills → Approaches no-skill baseline
- + Query-specific refinement → Recovers lost performance

Two bottlenecks:
1. Selection: Agents struggle to determine which skills to load
2. Content: Retrieved skills often lack precise task information

What works:
- Agentic hybrid search (iterative query + evaluation)
- Query-specific refinement (adapt skills to task, not generic improvement)

Implication: Don't assume skills automatically help. Design selection logic
and test with realistic retrieval scenarios.
"""

import modal
import os
import time

# Modal app definition
app = modal.App("uw-msba-proxy")

# Secrets containing your actual Fireworks API key
fireworks_secret = modal.Secret.from_name("fireworks-api-key")

# Container image with dependencies
image = modal.Image.debian_slim().pip_install("fastapi", "httpx", "uvicorn")


@app.function(
    image=image,
    secrets=[fireworks_secret],
    timeout=60,  # 60 second timeout for inference
)
@modal.rate_limit(
    60,  # 60 requests per minute global limit
    window=60
)
@modal.asgi_app()
def serve():
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.responses import StreamingResponse, JSONResponse
    import httpx
    import json
    
    web_app = FastAPI(title="UW MSBA AI Proxy")
    
    # Configuration - update this per semester
    STUDENT_AUTH = os.environ.get("STUDENT_AUTH_TOKEN", "fall-2026-secret")
    FIREWORKS_API_KEY = os.environ["FIREWORKS_API_KEY"]
    FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"
    DEFAULT_MODEL = "accounts/fireworks/routers/kimi-k2p5-fast"
    
    @web_app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Simple request logging"""
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        print(f"[{request.method}] {request.url.path} - {response.status_code} - {duration:.2f}s")
        return response
    
    @web_app.get("/health")
    async def health():
        """Health check endpoint"""
        return {"status": "ok", "proxy": "uw-msba-proxy"}
    
    @web_app.post("/v1/chat/completions")
    async def chat_completions(
        request: dict,
        authorization: str = Header(None, alias="Authorization"),
        x_stream: bool = Header(False, alias="X-Stream")
    ):
        """
        Proxy chat completion requests to Fireworks.
        
        Students must provide: Authorization: Bearer <semester-secret>
        """
        # Validate auth
        expected_auth = f"Bearer {STUDENT_AUTH}"
        if not authorization or authorization != expected_auth:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing authorization. Use: Authorization: Bearer <semester-secret>"
            )
        
        # Ensure model is set (default to Kimi K2.5 Fast)
        if "model" not in request or not request["model"]:
            request["model"] = DEFAULT_MODEL
        
        # Map friendly model names to Fireworks paths
        model_mapping = {
            "kimi-k2.5-fast": "accounts/fireworks/routers/kimi-k2p5-fast",
            "kimi-k2.5-turbo": "accounts/fireworks/routers/kimi-k2p5-turbo",
            "kimi": "accounts/fireworks/routers/kimi-k2p5-fast",
        }
        
        if request["model"] in model_mapping:
            request["model"] = model_mapping[request["model"]]
        
        try:
            # Forward to Fireworks
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {FIREWORKS_API_KEY}",
                    "Content-Type": "application/json",
                }
                
                # Handle streaming requests
                if request.get("stream", False):
                    async def stream_response():
                        async with client.stream(
                            "POST",
                            f"{FIREWORKS_BASE_URL}/chat/completions",
                            headers=headers,
                            json=request
                        ) as response:
                            async for chunk in response.aiter_text():
                                yield chunk
                    
                    return StreamingResponse(
                        stream_response(),
                        media_type="text/event-stream"
                    )
                
                # Non-streaming
                response = await client.post(
                    f"{FIREWORKS_BASE_URL}/chat/completions",
                    headers=headers,
                    json=request
                )
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            # Forward Fireworks errors
            error_body = e.response.text if e.response else str(e)
            print(f"Fireworks error: {error_body}")
            raise HTTPException(
                status_code=e.response.status_code if e.response else 502,
                detail=f"Upstream error: {error_body}"
            )
        except Exception as e:
            print(f"Proxy error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")
    
    @web_app.get("/v1/models")
    async def list_models(authorization: str = Header(None, alias="Authorization")):
        """List available models (filtered to what we support)"""
        expected_auth = f"Bearer {STUDENT_AUTH}"
        if not authorization or authorization != expected_auth:
            raise HTTPException(status_code=401, detail="Invalid authorization")
        
        return {
            "object": "list",
            "data": [
                {
                    "id": "kimi-k2.5-fast",
                    "object": "model",
                    "owned_by": "fireworks",
                    "description": "Kimi K2.5 Fast - General purpose reasoning"
                },
                {
                    "id": "kimi-k2.5-turbo", 
                    "object": "model",
                    "owned_by": "fireworks",
                    "description": "Kimi K2.5 Turbo - Higher quality, slower"
                }
            ]
        }
    
    return web_app


# For local testing (not used in Modal deployment)
if __name__ == "__main__":
    print("Run with: modal deploy proxy.py")
