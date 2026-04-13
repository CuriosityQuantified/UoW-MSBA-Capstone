"""
UW MSBA AI Proxy — Client

Import get_client() into your project to get a pre-configured Anthropic client
that routes through the course proxy. Build your agent on top of it.

Setup:
    pip install -r proxy-requirements.txt

.env (in your project root):
    PROXY_AUTH_TOKEN=<your-semester-token>      # from instructor
    LANGFUSE_PUBLIC_KEY=pk-lf-...               # from your Langfuse project
    LANGFUSE_SECRET_KEY=sk-lf-...
    LANGFUSE_HOST=https://us.cloud.langfuse.com

Usage:
    from client import get_client, MODEL

    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}]
    )
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

PROXY_URL = "https://model-proxy.curiosityquantified.com"
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"


def get_client(trace: bool = True) -> anthropic.Anthropic:
    """
    Return an Anthropic client pointed at the course proxy.

    Args:
        trace: If True (default), wraps the client with Langfuse so every call
               is traced to your Langfuse project automatically. Set to False
               for quick local testing without tracing.

    Returns:
        anthropic.Anthropic — use exactly like the standard Anthropic SDK.

    Requires env vars:
        PROXY_AUTH_TOKEN      — semester token from instructor
        LANGFUSE_PUBLIC_KEY   — only needed when trace=True
        LANGFUSE_SECRET_KEY   — only needed when trace=True
        LANGFUSE_HOST         — only needed when trace=True
    """
    token = os.environ.get("PROXY_AUTH_TOKEN")
    if not token:
        raise EnvironmentError(
            "PROXY_AUTH_TOKEN is not set. "
            "Add it to your .env file or export it in your shell."
        )

    if trace:
        try:
            from langfuse.anthropic import anthropic as langfuse_anthropic
            return langfuse_anthropic.Anthropic(
                api_key=token,
                base_url=PROXY_URL,
            )
        except ImportError:
            print(
                "Warning: langfuse not installed — returning untraced client. "
                "Run: pip install langfuse"
            )

    return anthropic.Anthropic(
        api_key=token,
        base_url=PROXY_URL,
    )


# ---------------------------------------------------------------------------
# Run this file directly to verify your setup works:
#   python client.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    client = get_client()

    # Basic completion
    print("=== Basic completion ===")
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {"role": "user", "content": "In one sentence, what is a language model?"}
        ],
    )
    print(response.content[0].text)

    # System prompt
    print("\n=== With system prompt ===")
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system="You are a concise data science tutor.",
        messages=[
            {"role": "user", "content": "What is overfitting? One sentence."}
        ],
    )
    print(response.content[0].text)

    # Streaming
    print("\n=== Streaming ===")
    with client.messages.stream(
        model=MODEL,
        max_tokens=128,
        messages=[{"role": "user", "content": "Count from 1 to 5, one per line."}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()
