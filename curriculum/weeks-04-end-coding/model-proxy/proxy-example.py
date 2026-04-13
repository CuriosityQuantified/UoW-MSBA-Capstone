# Example student usage

from langfuse.openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize with proxy endpoint
client = OpenAI(
    api_key=os.environ["PROXY_AUTH_TOKEN"],
    base_url="https://nap1320--uw-msba-proxy-serve.modal.run/v1"
)

# Simple completion
response = client.chat.completions.create(
    model="kimi-k2.5-fast",
    messages=[{"role": "user", "content": "Say hello"}],
    temperature=0.7
)

print(response.choices[0].message.content)

# With system prompt and multiple messages
response = client.chat.completions.create(
    model="kimi-k2.5-fast",
    messages=[
        {"role": "system", "content": "You are a data science tutor."},
        {"role": "user", "content": "Explain overfitting in simple terms."},
        {"role": "assistant", "content": "Overfitting is when..."},
        {"role": "user", "content": "Give me an example with decision trees."}
    ]
)

# Streaming
stream = client.chat.completions.create(
    model="kimi-k2.5-fast",
    messages=[{"role": "user", "content": "Write a short poem about AI."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
