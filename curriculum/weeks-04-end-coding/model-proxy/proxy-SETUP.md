# Setup Instructions for Instructor

## Prerequisites

- Modal account (modal.com)
- Fireworks AI account with API key
- Kimi K2.5 Fast access enabled

## 1. Configure Modal Secrets

```bash
# Set your actual Fireworks API key
modal secret create fireworks-api-key \
    FIREWORKS_API_KEY=fw_...

# Set the semester auth token (share this with students)
modal secret create student-auth \
    STUDENT_AUTH_TOKEN=fall-2026-secret
```

## 2. Deploy

```bash
cd ~/Projects/uw-msba-proxy
modal deploy proxy.py
```

Modal will output the endpoint URL:
```
https://nap1320--uw-msba-proxy-serve.modal.run
```

## 3. Test

```bash
curl https://nap1320--uw-msba-proxy-serve.modal.run/health

curl -X POST https://nap1320--uw-msba-proxy-serve.modal.run/v1/chat/completions \
  -H "Authorization: Bearer fall-2026-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-k2.5-fast",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 4. Distribute to Students

Share with class:
- **Endpoint**: `https://nap1320--uw-msba-proxy-serve.modal.run/v1`
- **Auth Token**: `fall-2026-secret` (or your configured token)
- **README**: The student README.md

## Teaching AI-Native Development

This course follows the [two-loop methodology](https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle) for AI-native development. Students must demonstrate both loops in their coursework:

### What to Teach

**The Build Loop (Engineering)**
- Students build fast with AI to answer questions, not just ship features
- Each prototype should reveal something about the problem
- Quality is curated, not reviewed line-by-line

**The Insight Loop (Product)**
- Spec-first: Behavior specifications before code
- Eval-driven: Binary pass/fail criteria before building
- Synthesis: What did we learn? What assumptions failed?

### How to Evaluate Student Work

Traditional software engineering coursework evaluates code quality. AI-native development requires evaluating:

| Traditional | AI-Native |
|-------------|-----------|
| Code correctness | Spec precision (what must it do/not do) |
| Test coverage | Eval coverage (binary criteria for real scenarios) |
| Documentation | Living specs that evolve with prototypes |
| Sprint velocity | Learning velocity (assumptions tested/build) |

**Look for in student submissions:**
1. **Behavior specifications** written before AI generation
2. **Binary eval criteria** (pass/fail, not subjective)
3. **Continuous evals** running against AI output
4. **Synthesis documentation**: What was revealed? What changed?
5. **Iteration evidence**: Multiple prototypes with learnings

**Red flags:**
- No spec, just prompts and code
- Manual review of AI-generated code
- One-shot builds without iteration
- No evidence of customer/problem understanding

### The Accountability Checkpoint

Before any student build starts, they should be able to answer:
- What does winning look like for this iteration?
- What will this build answer that we don't know?
- What does a wrong answer look like?
- How will we evaluate success (binary criteria)?

If they can't answer these, the build shouldn't start.

### Course Structure Suggestion

**Week 1-2: Spec Engineering**
- Write behavior specifications
- Define binary eval criteria
- Calibrate with "engineering" (AI) on constraints

**Week 3-4: Build Loop**
- Rapid prototyping with AI
- Run evals continuously
- Feed results back immediately

**Week 5-6: Insight Loop**
- Synthesize learnings
- Measure assumptions
- Iterate spec based on reveals

**Week 7-8: Final Delivery**
- Living documentation (spec + evals + synthesis)
- Working prototype
- Evidence of both loops in version history

## Monitoring

View logs:
```bash
modal logs uw-msba-proxy
```

Modal dashboard shows:
- Request volume
- Error rates
- Cold start latency

## Updating

Change the auth token mid-semester if needed:
```bash
modal secret create student-auth STUDENT_AUTH_TOKEN=spring-2027-secret
modal deploy proxy.py  # Restart to pick up new secret
```

Students will need the new token.

## Cost Estimates

Based on Fireworks pricing for Kimi K2.5 Fast:
- ~$0.50-1.00 per 1M input tokens
- ~$1.00-2.00 per 1M output tokens

For a class of 30 students doing moderate prototyping:
- Expected: $20-50/month
- Worst case: $100-200/month (heavy usage)

Set up billing alerts in Fireworks dashboard.

## Further Reading for Instructors

- [The SDLC for Building with AI](https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle) — Core methodology reference
- [Your Harness, Your Memory](https://blog.langchain.com/your-harness-your-memory/) — Why harness ownership matters
- GitHub Spec Kit — GitHub's spec-first development framework
- Amazon Kiro — Amazon's spec-driven AI workflow
- Thoughtworks: Three levels of spec adoption (spec-first, spec-anchored, spec-as-source)

### Why We Teach Open Harnesses

From [LangChain's analysis](https://blog.langchain.com/your-harness-your-memory/):

**Memory is not a plugin — it's the harness.** Managing context (short-term messages, long-term memory, skill loading) is the harness's core job.

**The lock-in risk:** Closed harnesses behind APIs (Claude Managed Agents, OpenAI Responses API) store memory you can't access or transfer. Even "open" harnesses like Codex use encrypted compaction summaries that only work in their ecosystem.

**What we teach:**
- Open harnesses (this Modal proxy, LangGraph, local-first patterns)
- Student-owned observability (their Langfuse, not ours)
- Stateless inference endpoints (no memory trapped in our infrastructure)

This prepares students to build systems they own, not systems that own them.

### Production Agent Architecture Reference

[Claude Code from Source](https://github.com/alejandrobalderas/claude-code-from-source) — Educational reverse-engineering of Claude Code's architecture (18 chapters, ~400 pages of patterns).  
[claude-code-from-source.com](https://claude-code-from-source.com/) — Web version for easier navigation.

[andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — Single CLAUDE.md with four principles from Andrej Karpathy's LLM coding observations: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution. Good foundation for student CLAUDE.md files.

[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — Production-grade engineering skills with 6-phase lifecycle (/spec, /plan, /build, /test, /review, /ship). 20 structured skills covering spec-driven development, incremental implementation, TDD, code review, debugging. Students should reference these patterns when writing their own SKILL.md files.

[How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) (Apr 2026) — UCSB/MIT study on skill utility under realistic conditions (34k real-world skills, multiple models including Kimi K2.5).

**Teaching implications:**
- Skills don't automatically improve performance — retrieval and selection matter
- Students should design skill selection logic, not just skill content
- Query-specific refinement (adapting skills to tasks) outperforms generic skill improvement
- Test with realistic skill collections, not hand-curated overfits

**Chapters most relevant for teaching:**
- **Ch 5-6** — Agent loop, tool execution, permission systems
- **Ch 8-10** — Sub-agents, fork agents, coordination/swarm patterns
- **Ch 11-12** — Memory taxonomy, skill loading, extensibility hooks
- **Ch 17** — Performance: context compression, prompt cache, token budgets

**Patterns to emphasize:**
- Speculative execution (start safe tools while streaming)
- Tool safety partitioning (concurrent reads, serialized writes)
- Two-phase skill loading (metadata early, content on demand)
- Context compression hierarchy (snip → microcompact → collapse → autocompact)

This is original pseudocode for educational purposes — no proprietary code, just architectural patterns distilled from studying a production system.
