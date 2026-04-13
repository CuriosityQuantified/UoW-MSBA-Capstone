"""
UW MSBA AI Proxy — Example Usage

Uses the Anthropic SDK pointing at the course proxy.
For Claude Code setup, see proxy-README.md instead.

Setup:
    pip install anthropic langfuse python-dotenv

.env:
    PROXY_AUTH_TOKEN=<your-semester-token>
    LANGFUSE_PUBLIC_KEY=pk-lf-...
    LANGFUSE_SECRET_KEY=sk-lf-...
    LANGFUSE_HOST=https://us.cloud.langfuse.com
"""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

PROXY_URL = "https://model-proxy.curiosityquantified.com"
AUTH_TOKEN = os.environ["PROXY_AUTH_TOKEN"]

# The proxy forces kimi-k2p5-turbo regardless of what model you pass
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"

# Initialize Anthropic client pointing at the proxy
client = anthropic.Anthropic(
    api_key=AUTH_TOKEN,
    base_url=PROXY_URL,
)


# --- Example 1: Simple completion ---

response = client.messages.create(
    model=MODEL,
    max_tokens=256,
    messages=[
        {"role": "user", "content": "Explain the difference between precision and recall in one paragraph."}
    ]
)

print(response.content[0].text)


# --- Example 2: System prompt + multi-turn ---

response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    system="You are a data science tutor. Be concise and use examples.",
    messages=[
        {"role": "user", "content": "What is overfitting?"},
        {"role": "assistant", "content": "Overfitting is when a model learns the training data too well..."},
        {"role": "user", "content": "Give me a concrete example with decision trees."}
    ]
)

print(response.content[0].text)


# --- Example 3: Streaming ---

with client.messages.stream(
    model=MODEL,
    max_tokens=256,
    messages=[{"role": "user", "content": "Write a haiku about machine learning."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()  # newline after stream


# --- Example 4: With Langfuse observability ---
# Langfuse wraps the Anthropic client to capture traces automatically.
# Every call below is traced to YOUR Langfuse project.

try:
    from langfuse.anthropic import anthropic as langfuse_anthropic

    traced_client = langfuse_anthropic.Anthropic(
        api_key=AUTH_TOKEN,
        base_url=PROXY_URL,
    )

    response = traced_client.messages.create(
        model=MODEL,
        max_tokens=128,
        messages=[{"role": "user", "content": "Hello from the traced client!"}]
    )

    print(response.content[0].text)
    print("(Check your Langfuse dashboard for the trace)")

except ImportError:
    print("Langfuse not installed. Run: pip install langfuse")
