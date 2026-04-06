# Week 5 — Advanced Coding: Multi-Agent, Memory, Eval

**Goal:** Build more capable agentic systems. Move from single-agent prototypes to multi-agent flows, persistent memory, and evaluation loops.

---

## Recommended Learning Path

| Step | Resource | Platform | Time | Why |
|------|----------|----------|------|-----|
| 1 | [Introduction to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph) | LangChain Academy | 6–8h | Deeper: state, checkpointing, human-in-the-loop, multi-agent |
| 2 | [HuggingFace Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction) | HuggingFace | 15–20h | Framework-agnostic depth; earns a certificate |

---

## Concept Docs

- [`concepts/code-development.md`](../concepts/code-development.md) — Full learning path, project scaffolding, capstone structure
- [`concepts/progressive-disclosure.md`](../concepts/progressive-disclosure.md) — Keep reading this throughout your build; it becomes more useful as your codebase grows
- [`concepts/continual-learning.md`](../concepts/continual-learning.md) — How agents improve over time

---

## Videos for This Phase

| Video | Why |
|-------|-----|
| [Build Advanced AI Agent Systems](https://www.youtube.com/watch?v=1w5cCXlh7JQ) | Intermediate builds — tools, routing, memory |
| [LangChain + LangGraph Explained (2025)](https://www.youtube.com/watch?v=1ykcOVCQdkY) | Architecture deep dive for when your graph gets complex |
| [Long-Term Memory in LangGraph](https://www.youtube.com/watch?v=R0OdB-p-ns4) | Harrison Chase — cross-session memory patterns |
| [How Claude Code's Creator Starts Every Project](https://youtu.be/KWrsLqnB6vA) | Austin Marchese — 6 production workflows |
| [MiroFish AI Explained](https://www.youtube.com/watch?v=dbITcA6sRNo) | Art of the possible — swarm intelligence, orchestrator-workers |

---

## Claude Code Workflows

If you're using Claude Code for capstone development, these 6 strategies from Austin Marchese (Claude Code creator) are worth internalizing:

1. **Plan mode first** — `Shift+Tab` twice before every session. Lock in the plan; execution follows automatically. Kickoff prompt: *"Interview me about this. What's the core problem? Who is it for? What does success look like? What should it NOT do?"*

2. **Minimal `claude.md`** — Keep it under a few thousand tokens. When it bloats, delete and rebuild. Models improve over time — rules from 6 months ago may already be baked in.

3. **Verification loops** — Give Claude a tool to see the output of its own work. Add to `claude.md`: *"Before any work, mention how you'd verify it."*

4. **Parallel sessions** — Run multiple Claude sessions on non-overlapping files. Fresh context windows catch what a deep-context session misses.

5. **Inner loops → slash commands** — Anything you do more than twice, document it as a reusable slash command or skill.

6. **Build for the future** — Focus on **information architecture** (what context you feed the model) not micro-prompt tweaks. The Bitter Lesson applies to prompting too.

---

## Capstone Milestones (Weeks 5–10)

| Week | Milestone |
|------|-----------|
| Week 5 | Multi-step flow with memory working |
| Week 6 | Multi-agent or routing layer implemented |
| Week 7 | Eval loop in place — agent can score its own outputs |
| Week 8 | Cost guards + error handling + retry logic hardened |
| Week 9 | Performance optimization, edge cases handled |
| Week 10 | Deployed / demo-ready |

---

## Next Steps

Continue building through Week 10. Use the concept docs and FAQ as reference:
- [`faq/README.md`](../faq/README.md) — Common questions
- [`faq/framework-choices.md`](../faq/framework-choices.md) — When to use what
- [`faq/common-errors.md`](../faq/common-errors.md) — Debugging guide
