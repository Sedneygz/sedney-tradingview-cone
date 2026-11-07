import json
import os

from dotenv import load_dotenv

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover
    Anthropic = None


load_dotenv()


def analyze_market_with_claude(brief):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or Anthropic is None:
        return (
            "Claude is not configured. Jarvis is using local technical analysis. "
            "Add ANTHROPIC_API_KEY in .env to enable AI summaries."
        )

    client = Anthropic(api_key=api_key)
    prompt = f"""
You are Jarvis, a calm and disciplined forex market analyst.

Your job is to summarize the market for the user in plain English.
Focus on: trend, risk, support/resistance, and what to watch today.
Do not promise trades. Keep the tone practical and professional.

Market data:
{json.dumps(brief, indent=2, default=str)}

Response format:
- Summary
- Key levels
- Risk notes
- Day bias
"""
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=500,
            system="You are Jarvis, a careful forex market analyst.",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as exc:  # pragma: no cover
        return f"Claude summary failed: {exc}. Local analysis is still available."
