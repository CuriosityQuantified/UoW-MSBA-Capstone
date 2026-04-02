# Weeks 5–10 — Code Development

**Goal:** Build production-capable agentic systems. Move from prototype to evaluated, observable, deployable agent.

---

## Recommended Learning Path

Work through these in order. Each course unlocks the next level.

| Step | Resource | Platform | Time | Why |
|------|----------|----------|------|-----|
| 1 | [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) | DeepLearning.AI | 4–6h | First hands-on with LangGraph — tools, memory, multi-agent |
| 2 | [Introduction to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph) | LangChain Academy | 6–8h | Deeper: state, checkpointing, human-in-the-loop |
| 3 | [HuggingFace Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction) | HuggingFace | 15–20h | Framework-agnostic depth; earns a certificate |

---

## Concept Docs

- [`concepts/code-development.md`](../concepts/code-development.md) — Full learning path, project scaffolding, capstone structure
- [`concepts/progressive-disclosure.md`](../concepts/progressive-disclosure.md) — Keep reading this throughout your build; it becomes more useful as your codebase grows

---

## Videos for This Phase

| Video | Why |
|-------|-----|
| [Build Advanced AI Agent Systems](https://www.youtube.com/watch?v=1w5cCXlh7JQ) | Intermediate builds — tools, routing, memory |
| [LangChain + LangGraph Explained (2025)](https://www.youtube.com/watch?v=1ykcOVCQdkY) | Architecture deep dive for when your graph gets complex |
| [Agentic AI for Beginners](https://www.youtube.com/watch?v=CnXdddeZ4tQ) | Good reference when approaching capstone |
| [How Claude Code's Creator Starts Every Project](https://youtu.be/KWrsLqnB6vA) | Austin Marchese — 6 production workflows: plan mode, minimal claude.md, verification loops, parallel sessions, slash commands, info architecture |
| [MiroFish AI Explained](https://www.youtube.com/watch?v=dbITcA6sRNo) | Art of the possible — swarm intelligence, orchestrator-workers at scale |

---

## Claude Code Workflows (Weeks 5+)

If you're using Claude Code for capstone development, these 6 strategies from Austin Marchese (Claude Code creator) are worth internalizing:

1. **Plan mode first** — `Shift+Tab` twice before every session. Lock in the plan; execution follows automatically. Kickoff prompt: *"Interview me about this. What's the core problem? Who is it for? What does success look like? What should it NOT do?"*

2. **Minimal `claude.md`** — Keep it under a few thousand tokens. When it bloats, delete and rebuild. Models improve over time — rules from 6 months ago may already be baked in. Maintenance prompt: *"Update claude.md to remove anything contradictory, duplicate, or unnecessary."*

3. **Verification loops** — Give Claude a tool to see the output of its own work. Add to `claude.md`: *"Before any work, mention how you'd verify it."* Post-session sweep: *"Go back and verify all your work. Check for best practices, efficiency, and new issues."*

4. **Parallel sessions** — Run multiple Claude sessions on non-overlapping files. Fresh context windows catch what a deep-context session misses. Two sessions that don't know about each other produce better results.

5. **Inner loops → slash commands** — Anything you do more than twice, document it as a reusable slash command or skill. Discovery prompt: *"Based on the project I'm working on, what Claude skills should I create?"*

6. **Build for the future** — Don't over-optimize prompts; the model will outpace them in 6 months. Focus on your **information architecture** — what context you're feeding the model — not micro-prompt tweaks. (The Bitter Lesson applied to prompting.)

---

## Capstone Milestones

| Week | Milestone |
|------|-----------|
| Week 5 | Agent scaffolding complete — tools defined, state shape designed |
| Week 6 | First working end-to-end run with tracing enabled |
| Week 7 | Multi-step or multi-agent flow working |
| Week 8 | Eval loop in place — agent can score its own outputs |
| Week 9 | Cost guards + error handling + retry logic |
| Week 10 | Deployed / demo-ready |
