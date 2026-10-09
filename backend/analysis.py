
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def analyze_transcript(transcript: str) -> dict:
    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty")

    prompt = f"""
You are a quality analyst for a human-operated call center.
Analyze the following conversation between a customer and a human agent.

Return ONLY a valid JSON object with these fields:
- summary: a concise summary of the call
- sentiment: one of Positive, Neutral, or Negative
- customer_intent: the main reason the customer contacted support
- key_issues: a list of important issues discussed

Use only information supported by the transcript.
Do not invent events or claim that an issue was resolved unless stated.

Transcript:
{transcript}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    try:
        result = json.loads(response.text)

        required_fields = {
            "summary",
            "sentiment",
            "customer_intent",
            "key_issues"
        }

        if not required_fields.issubset(result):
            raise ValueError("Gemini response is missing required fields")

        if result["sentiment"] not in {"Positive", "Neutral", "Negative"}:
            raise ValueError("Gemini returned an invalid sentiment")

        if not isinstance(result["key_issues"], list):
            raise ValueError("key_issues must be a list")

        return result

    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("Gemini returned an invalid JSON response") from exc
