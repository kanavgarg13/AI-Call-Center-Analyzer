
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

Analyze the following conversation.

Return ONLY a valid JSON object with these fields:

- summary: a concise summary of the call
- sentiment: one of Positive, Neutral, or Negative
- customer_intent: the main reason the customer contacted support
- key_issues: a list of important issues discussed
- speaker_roles: a dictionary mapping each speaker ID to either
  Agent, Customer, or Unknown

Speaker identification rules:
1. Identify the Agent by looking for customer-service behaviour,
   such as greeting callers, offering assistance, asking questions,
   and providing support.
2. Identify the Customer by looking for requests, complaints,
   questions, or responses seeking assistance.
3. Do not assume SPEAKER_00 is always the Agent.
4. If the speaker's role cannot be determined confidently,
   assign Unknown.
5. Include every speaker ID present in the transcript.

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
            "key_issues",
            "speaker_roles"
        }

        if not required_fields.issubset(result):
            raise ValueError(
                "Gemini response is missing required fields"
            )

        if result["sentiment"] not in {
            "Positive", "Neutral", "Negative"
        }:
            raise ValueError("Gemini returned an invalid sentiment")

        if not isinstance(result["key_issues"], list):
            raise ValueError("key_issues must be a list")

        if not isinstance(result["speaker_roles"], dict):
            raise ValueError("speaker_roles must be a dictionary")

        allowed_roles = {"Agent", "Customer", "Unknown"}

        if not all(
            role in allowed_roles
            for role in result["speaker_roles"].values()
        ):
            raise ValueError("Gemini returned an invalid speaker role")

        return result

    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(
            "Gemini returned an invalid JSON response"
        ) from exc
