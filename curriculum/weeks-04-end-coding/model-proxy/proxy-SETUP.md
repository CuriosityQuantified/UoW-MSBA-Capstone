# Setup Instructions for Instructor

The proxy is a Cloudflare Worker — globally distributed, always available, no server to manage. Source lives at `~/Projects/model-proxy/`.

## Prerequisites

- Cloudflare account with `curiosityquantified.com` zone
- Fireworks AI API key
- Node.js + wrangler CLI (`npm install -g wrangler`)

## First-Time Deployment

### 1. Authenticate wrangler

```bash
wrangler login
```

### 2. Set secrets

```bash
cd ~/Projects/model-proxy

# Your Fireworks API key (never shared with students)
echo "fw_..." | wrangler secret put FIREWORKS_API_KEY

# Semester token (share this with students in class, never in the repo)
echo "msba2026-<random>" | wrangler secret put STUDENT_TOKEN
```

Generate a random token:
```bash
python3 -c "import secrets; print('msba2026-' + secrets.token_hex(8))"
```

### 3. Deploy

```bash
cd ~/Projects/model-proxy
wrangler deploy
```

The Worker deploys to `model-proxy.curiosityquantified.com`.

### 4. Test

```bash
# Health check
curl https://model-proxy.curiosityquantified.com/health

# Full completion test (replace token)
curl -X POST https://model-proxy.curiosityquantified.com/v1/messages \
  -H "Authorization: Bearer <semester-token>" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"anything","max_tokens":20,"messages":[{"role":"user","content":"Say: proxy works"}]}'

# Verify 401 on bad token
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer wrongtoken" \
  https://model-proxy.curiosityquantified.com/health
```

### 5. Configure Rate Limiting (Cloudflare Dashboard)

In the Cloudflare dashboard for `curiosityquantified.com`:
1. Go to **Security → WAF → Rate Limiting Rules**
2. Create a rule:
   - **Name**: MSBA Proxy Rate Limit
   - **Field**: URI Path / `starts with` / `/v1/`
   - **Rate**: 180 requests per 10 seconds per IP
   - **Action**: Block (429)

### 6. Distribute to Students

Share with class (in person or private channel — **not in the repo**):
- **Endpoint**: `https://model-proxy.curiosityquantified.com`
- **Semester token**: the value you set in step 2
- Point them to `proxy-README.md` for the `~/.claude/settings.json` snippet

---

## Rotating the Fireworks API Key

Students are unaffected — they use the semester token, not the Fireworks key:

```bash
cd ~/Projects/model-proxy
echo "fw_NewKeyHere" | wrangler secret put FIREWORKS_API_KEY
```

No redeploy needed for secret rotation.

## Rotating the Student Token (new semester)

```bash
cd ~/Projects/model-proxy
echo "msba2027-$(python3 -c 'import secrets; print(secrets.token_hex(8))')" | wrangler secret put STUDENT_TOKEN
```

Students update their `~/.claude/settings.json` with the new token.

## Monitoring

View real-time logs:
```bash
cd ~/Projects/model-proxy
wrangler tail
```

Cloudflare dashboard shows:
- Request volume and error rates by route
- Geographic distribution
- Rate limiting events

## Cost Estimates

Based on Fireworks pricing for Kimi K2.5 Turbo:
- ~$0.90/1M input tokens, ~$3.00/1M output tokens
- Cloudflare Workers free tier: 100k requests/day

For a class of 30 students doing moderate prototyping:
- **Expected**: $30–80/month
- **Worst case**: $150–300/month (heavy usage)

Set up billing alerts in the Fireworks dashboard.

---

## Teaching AI-Native Development

This course follows the [two-loop methodology](https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle) for AI-native development.

### How to Evaluate Student Work

| Traditional | AI-Native |
|-------------|-----------|
| Code correctness | Spec precision |
| Test coverage | Eval coverage (binary criteria) |
| Documentation | Living specs that evolve with prototypes |
| Sprint velocity | Learning velocity (assumptions tested/build) |

**Look for in student submissions:**
1. Behavior specifications written before AI generation
2. Binary eval criteria (pass/fail, not subjective)
3. Continuous evals running against AI output
4. Synthesis documentation: What was revealed? What changed?
5. Iteration evidence: Multiple prototypes with learnings

**Red flags:**
- No spec, just prompts and code
- Manual review of AI-generated code
- One-shot builds without iteration
- No evidence of customer/problem understanding

### The Accountability Checkpoint

Before any student build starts, they should answer:
- What does winning look like for this iteration?
- What will this build answer that we don't know?
- What does a wrong answer look like?
- How will we evaluate success (binary criteria)?

### Course Structure Suggestion

| Weeks | Focus |
|-------|-------|
| 1–2 | Spec Engineering: behavior specs, binary eval criteria |
| 3–4 | Build Loop: rapid prototyping, continuous evals |
| 5–6 | Insight Loop: synthesize learnings, iterate spec |
| 7–8 | Final Delivery: living docs, working prototype, evidence of both loops |

---

## Further Reading for Instructors

- [The SDLC for Building with AI](https://aibarraiser.substack.com/p/whats-the-new-software-dev-cycle) — Core methodology
- [Your Harness, Your Memory](https://blog.langchain.com/your-harness-your-memory/) — Why harness ownership matters
- [Claude Code from Source](https://github.com/alejandrobalderas/claude-code-from-source) — Production agent architecture reference
- [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) — Apr 2026 research on skill utility

### Why We Teach Open Harnesses

From LangChain's analysis: **Memory is not a plugin — it's the harness.** Managing context is the harness's core job.

**The lock-in risk:** Closed harnesses (Claude Managed Agents, OpenAI Responses API) store memory you can't access or transfer.

**What we teach:**
- Open harnesses (this Cloudflare proxy, LangGraph, local-first patterns)
- Student-owned observability (their Langfuse, not ours)
- Stateless inference endpoints (no memory trapped in our infrastructure)
