# Claude Code Setup — Course Model Proxy

This guide connects Claude Code (and your Python scripts) to the course model proxy so you can use Kimi K2.5 Turbo without needing your own API key.

**You will need your semester token from the instructor before you start.**  
It looks like: `msba2026-xxxxxxxxxxxxxxxx`

---

## Part 1 — Claude Code

Claude Code is the AI coding assistant you'll use throughout the course. Once configured, every `claude` session — including all sub-agents — routes through the proxy automatically.

### Step 1 — Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Verify the install:

```bash
claude --version
```

> **Requires Node.js 18+.** Check with `node --version`. Install from [nodejs.org](https://nodejs.org) if needed.

---

### Step 2 — Create the settings file

Create `~/.claude/settings.json` (your home directory, not your project):

```bash
mkdir -p ~/.claude
```

Open `~/.claude/settings.json` in any editor and paste the following, replacing `<YOUR_SEMESTER_TOKEN>` with the token from your instructor:

```json
{
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "apiKeyHelper": "bash -c 'echo <YOUR_SEMESTER_TOKEN>'",
    "env": {
        "ANTHROPIC_BASE_URL": "https://model-proxy.curiosityquantified.com",
        "ANTHROPIC_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_SMALL_FAST_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "accounts/fireworks/routers/kimi-k2p5-turbo"
    },
    "model": "accounts/fireworks/routers/kimi-k2p5-turbo"
}
```

> **Do not commit this file.** It contains your token. Add `~/.claude/settings.json` to your global `.gitignore` if you haven't already.

---

### Step 3 — Launch Claude Code

```bash
claude
```

You should see the Claude Code prompt. Type a quick test:

```
> What model are you running on?
```

The model will identify itself (it may say Claude — that's the interface; the backend is Kimi K2.5 Turbo via the proxy).

If you see `401 Unauthorized`, double-check your token in `settings.json`.

---

### Step 4 — Test the proxy directly (optional)

You can verify the endpoint is live before launching Claude Code:

```bash
# Health check
curl https://model-proxy.curiosityquantified.com/health

# Live completion (replace token)
curl -X POST https://model-proxy.curiosityquantified.com/v1/messages \
  -H "x-api-key: <YOUR_SEMESTER_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"anything","max_tokens":20,"messages":[{"role":"user","content":"Reply: proxy works"}]}'
```

Expected: `{"content":[{"text":"proxy works","type":"text"}],...}`

---

## Part 2 — Python Scripts

The Python examples in `model-proxy/examples/` all read from a `.env` file. Set this up once and all examples will work.

### Step 5 — Install dependencies

```bash
pip install anthropic langchain langchain-anthropic langgraph deepagents langfuse pydantic python-dotenv
```

---

### Step 6 — Create your `.env` file

In your project root (or wherever you run your scripts), create a `.env` file:

```bash
# Course model proxy
PROXY_AUTH_TOKEN=<YOUR_SEMESTER_TOKEN>

# Langfuse observability (get keys from your Langfuse project)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com
```

> **Do not commit `.env`.** It should already be in `.gitignore`. If not, add it.

---

### Step 7 — Set up Langfuse

Every example traces to Langfuse so you can inspect token usage, latency, and agent step-by-step traces.

1. Go to [cloud.langfuse.com](https://cloud.langfuse.com) and create a free account
2. Create a new project (name it anything — e.g., `msba-capstone`)
3. Open **Settings → API Keys** and create a key pair
4. Copy the public and secret keys into your `.env` from Step 6

---

### Step 8 — Run a test script

```bash
cd curriculum/weeks-04-end-coding/model-proxy
python client.py
```

You should see a response printed and a new trace appear in your Langfuse dashboard within a few seconds.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `401 Unauthorized` in Claude Code | Check `apiKeyHelper` value in `~/.claude/settings.json` — no extra spaces or newlines |
| `401 Unauthorized` in Python | Check `PROXY_AUTH_TOKEN` in `.env` matches your semester token exactly |
| `No module named 'langfuse'` | Run `pip install langfuse` |
| No traces in Langfuse | Verify `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set and the project exists at `us.cloud.langfuse.com` |
| `502` / `504` errors | Upstream issue — wait a moment and retry |
| Claude Code hangs on start | Try `claude --dangerously-skip-permissions` once to reset; then relaunch normally |

---

## What the proxy does

```
Your machine
  └─ Claude Code / Python script
       └─ Bearer <semester-token>
            ↓
  https://model-proxy.curiosityquantified.com   (Cloudflare, global edge)
            ↓ swaps token for Fireworks API key
  https://api.fireworks.ai  →  Kimi K2.5 Turbo
```

- The instructor holds the Fireworks API key — you never see it
- Your semester token can be rotated without touching the Fireworks key
- Rate limit: **180 requests/minute** across all students — be considerate

---

## Rate limit etiquette

- Don't run tight loops that hammer the API (add `time.sleep(1)` between calls if you're iterating)
- If you hit a `429`, wait a few seconds and retry
- Avoid leaving agentic loops running unattended — they consume quota for everyone
