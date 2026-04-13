# 04_structured_output.py
# Structured data extraction using Pydantic + the Anthropic SDK.
#
# extract(text, schema) parses unstructured text into a typed Python object.
# Common patterns: extracting entities from documents, parsing reports,
# normalizing survey responses, building structured datasets from text.
#
# No framework needed — uses the Anthropic tool-calling API with Pydantic
# to guarantee the model returns valid, typed data.
#
# Prerequisites:
#   pip install anthropic pydantic langfuse python-dotenv
#
# Environment variables required (.env):
#   PROXY_AUTH_TOKEN        — semester token from instructor
#   LANGFUSE_PUBLIC_KEY     — from your Langfuse project
#   LANGFUSE_SECRET_KEY
#   LANGFUSE_HOST=https://us.cloud.langfuse.com

import json
import os
from typing import TypeVar
from dotenv import load_dotenv

import anthropic
from pydantic import BaseModel
from langfuse.anthropic import anthropic as langfuse_anthropic

load_dotenv()

PROXY_URL = "https://model-proxy.curiosityquantified.com"
MODEL = "accounts/fireworks/routers/kimi-k2p5-turbo"

T = TypeVar("T", bound=BaseModel)


def get_client() -> anthropic.Anthropic:
    """Return a Langfuse-traced Anthropic client via the course proxy."""
    return langfuse_anthropic.Anthropic(
        api_key=os.environ["PROXY_AUTH_TOKEN"],
        base_url=PROXY_URL,
    )


# ---------------------------------------------------------------------------
# Core extraction function
# ---------------------------------------------------------------------------

def extract(text: str, schema: type[T], instructions: str = "") -> T:
    """
    Extract structured data from text according to a Pydantic schema.

    Uses Anthropic's tool-calling API to force the model to return data
    that matches your schema exactly — no string parsing, no regex.

    Args:
        text:         The unstructured text to extract from.
        schema:       A Pydantic BaseModel class defining the output shape.
        instructions: Optional additional extraction instructions.

    Returns:
        An instance of your Pydantic schema, validated and typed.

    Example:
        class Company(BaseModel):
            name: str
            revenue: float
            employees: int

        result = extract("Apple had $383B in revenue with 161k employees.", Company)
        print(result.name, result.revenue)
    """
    client = get_client()

    # Build a tool definition from the Pydantic schema
    tool_def = {
        "name": "extract",
        "description": f"Extract {schema.__name__} from the provided text.",
        "input_schema": schema.model_json_schema(),
    }

    system = (
        "You are a precise data extraction assistant. "
        "Extract exactly the fields requested from the provided text. "
        "If a field is not present in the text, use null or a sensible default. "
        + instructions
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        tools=[tool_def],
        tool_choice={"type": "tool", "name": "extract"},  # force tool use
        messages=[{"role": "user", "content": f"Extract from this text:\n\n{text}"}],
    )

    # The model must have called the extract tool
    tool_block = next(b for b in response.content if b.type == "tool_use")
    return schema.model_validate(tool_block.input)


# ---------------------------------------------------------------------------
# Example schemas — replace with schemas for your use case
# ---------------------------------------------------------------------------

class CompanyProfile(BaseModel):
    name: str
    ticker: str | None
    sector: str
    annual_revenue_usd_billions: float | None
    employee_count: int | None
    headquarters_city: str | None
    key_products: list[str]
    sentiment: str  # "positive", "neutral", or "negative"


class CustomerFeedback(BaseModel):
    overall_sentiment: str          # "positive", "neutral", "negative"
    satisfaction_score: int | None  # 1–10 if mentioned
    main_complaint: str | None
    main_praise: str | None
    requested_features: list[str]
    would_recommend: bool | None


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example 1: Extract a company profile from a news snippet
    print("=== Company extraction ===")
    news = """
    Microsoft Corporation (NASDAQ: MSFT), headquartered in Redmond, Washington,
    reported record annual revenue of $211.9 billion for fiscal year 2023.
    The technology giant employs over 221,000 people worldwide. Its flagship
    products include Azure cloud services, Microsoft 365, and the Windows
    operating system. Analysts remain bullish on the company's AI integration
    strategy, citing strong growth in the cloud segment.
    """
    company = extract(news, CompanyProfile)
    print(f"Name: {company.name} ({company.ticker})")
    print(f"Revenue: ${company.annual_revenue_usd_billions}B")
    print(f"Products: {', '.join(company.key_products)}")
    print(f"Sentiment: {company.sentiment}")

    # Example 2: Parse customer feedback
    print("\n=== Feedback extraction ===")
    feedback = """
    I've been using your platform for 6 months and give it a 7/10 overall.
    The dashboard is clean and reports export quickly — love that. But the
    mobile app crashes constantly and there's no dark mode, which is frustrating
    for late-night work sessions. I'd also really love API access and a bulk
    export feature. Would I recommend it? Probably, if they fix the mobile app.
    """
    parsed = extract(feedback, CustomerFeedback)
    print(f"Sentiment: {parsed.overall_sentiment} (score: {parsed.satisfaction_score}/10)")
    print(f"Complaint: {parsed.main_complaint}")
    print(f"Requested: {', '.join(parsed.requested_features)}")
    print(f"Would recommend: {parsed.would_recommend}")

    # The raw extracted objects are fully typed — use them in pipelines:
    # df = pd.DataFrame([extract(text, CompanyProfile).model_dump() for text in corpus])
