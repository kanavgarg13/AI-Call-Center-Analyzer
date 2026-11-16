
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# Load environment variables
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
You are a professional quality analyst for a human-operated call center.

Analyze the following conversation between a customer and a human agent.

Return ONLY a valid JSON object with these fields:

1. summary: A concise summary of the call.

2. sentiment: One of Positive, Neutral, or Negative.
   This represents the customer's overall sentiment.

3. customer_intent: The main reason the customer contacted support.

4. key_issues: A list of important issues discussed.

5. speaker_roles: A dictionary mapping every speaker ID to
   Agent, Customer, or Unknown.

6. call_outcome: One of:
   - Resolved
   - Partially Resolved
   - Unresolved
   - Unknown

7. unresolved_issues: A list of customer problems or requests
   that remain unresolved at the end of the conversation.

8. escalation: An object containing:
   - required: A boolean indicating whether escalation is needed.
   - reason: A concise explanation, or null if escalation
     is not required.

9. agent_performance: An object containing:

   - overall_score: Integer from 0 to 100, or null.
   - criteria: An object containing these five criteria:
       greeting: Score from 0 to 100, or null.
       communication: Score from 0 to 100, or null.
       customer_understanding: Score from 0 to 100, or null.
       professionalism: Score from 0 to 100, or null.
       resolution: Score from 0 to 100, or null.
   - strengths: A list of positive observations about the agent.
   - improvements: A list of areas where the agent could improve.
   - feedback: A concise overall evaluation of the agent.

Agent evaluation rules:

1. Evaluate only speakers identified as Agent.
2. Base every score on evidence from the transcript.
3. Do not assume actions occurred if they are not mentioned.
4. Do not penalize an agent for something that cannot be
   evaluated from the available conversation.
5. If a criterion cannot be evaluated, use null for its score.
6. Do not treat an incomplete conversation as automatically
   indicating poor resolution.
7. Scores must be integers from 0 to 100 when evaluable.

8. Resolution evaluation rules:
   - Evaluate whether the customer's issue or request was
     successfully addressed.
   - If the conversation ends before the outcome is known,
     assign null.
   - If the agent clearly fails to address the customer's
     request, assign an appropriate low score.
   - If the agent successfully resolves the request,
     assign an appropriate score based on the evidence.
   - Do not confuse collecting information with completing
     the customer's request.

9. If no agent can be confidently identified, set all criteria
   and overall_score to null and explain why in feedback.

Speaker identification rules:

1. Identify the Agent through customer-service behaviour,
   such as greeting callers, offering assistance, asking
   questions, and providing support.
2. Identify the Customer through requests, complaints,
   questions, and responses seeking assistance.
3. Do not assume SPEAKER_00 is always the Agent.
4. Assign Unknown when the role cannot be determined confidently.
5. Include every speaker ID present in the transcript.

Call outcome rules:

1. Resolved: The customer's main issue was successfully addressed.
2. Partially Resolved: Some parts were addressed, but others remain.
3. Unresolved: The main issue was not addressed or remains unresolved.
4. Unknown: The conversation ends before the outcome can be determined.
5. Base the outcome only on evidence in the conversation.
6. Do not assume that an issue was resolved just because the
   agent says they will look into it or take further action.

Unresolved issue rules:

1. Include only customer issues or requests that remain unresolved.
2. Return an empty list if no unresolved issues remain.
3. Do not invent unresolved problems.
4. If the outcome is Unknown, include only issues that are
   clearly still unresolved based on the available evidence.

Escalation rules:

1. Set required to true when the conversation clearly indicates
   that escalation is necessary.
2. Examples include an explicit request for a supervisor or
   an issue requiring another support level.
3. Do not recommend escalation without supporting evidence.
4. If escalation is not required, set reason to null.
5. Do not treat every unresolved issue as automatically requiring
   escalation.

Use only information supported by the transcript.
Do not invent events or claim that an issue was resolved
unless explicitly supported by the conversation.

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

        # Validate main analysis fields
        required_fields = {
            "summary",
            "sentiment",
            "customer_intent",
            "key_issues",
            "speaker_roles",
            "call_outcome",
            "unresolved_issues",
            "escalation",
            "agent_performance"
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

        # Validate call outcome
        allowed_outcomes = {
            "Resolved",
            "Partially Resolved",
            "Unresolved",
            "Unknown"
        }

        if result["call_outcome"] not in allowed_outcomes:
            raise ValueError("Invalid call outcome")

        # Validate unresolved issues
        if not isinstance(result["unresolved_issues"], list):
            raise ValueError("unresolved_issues must be a list")

        # Validate escalation
        escalation = result["escalation"]

        if not isinstance(escalation, dict):
            raise ValueError("escalation must be an object")

        if not isinstance(escalation.get("required"), bool):
            raise ValueError("escalation.required must be a boolean")

        if escalation["required"]:
            if not isinstance(escalation.get("reason"), str):
                raise ValueError("Escalation reason must be a string")
        else:
            if escalation.get("reason") is not None:
                raise ValueError("Escalation reason must be null")

        # Validate agent performance
        performance = result["agent_performance"]

        if not isinstance(performance, dict):
            raise ValueError("agent_performance must be an object")

        required_performance_fields = {
            "overall_score",
            "criteria",
            "strengths",
            "improvements",
            "feedback"
        }

        if not required_performance_fields.issubset(performance):
            raise ValueError(
                "Agent performance response is incomplete"
            )

        criteria = performance["criteria"]

        required_criteria = {
            "greeting",
            "communication",
            "customer_understanding",
            "professionalism",
            "resolution"
        }

        if not isinstance(criteria, dict):
            raise ValueError("criteria must be an object")

        if not required_criteria.issubset(criteria):
            raise ValueError("Agent evaluation criteria are incomplete")

        # Validate individual criterion scores
        for name in required_criteria:
            score = criteria[name]

            if score is not None and (
                not isinstance(score, int)
                or isinstance(score, bool)
                or not 0 <= score <= 100
            ):
                raise ValueError(
                    f"Invalid evaluation score for {name}"
                )

        # Validate overall score format
        overall_score = performance["overall_score"]

        if overall_score is not None and (
            not isinstance(overall_score, int)
            or isinstance(overall_score, bool)
            or not 0 <= overall_score <= 100
        ):
            raise ValueError("Invalid overall performance score")

        if not isinstance(performance["strengths"], list):
            raise ValueError("strengths must be a list")

        if not isinstance(performance["improvements"], list):
            raise ValueError("improvements must be a list")

        if not isinstance(performance["feedback"], str):
            raise ValueError("feedback must be a string")

        # Calculate overall score using Python
        # Ignore criteria that have a null score
        evaluated_scores = [
            criteria[name]
            for name in required_criteria
            if criteria[name] is not None
        ]

        if evaluated_scores:
            performance["overall_score"] = int(
                sum(evaluated_scores) / len(evaluated_scores) + 0.5
            )
        else:
            performance["overall_score"] = None

        return result

    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(
            "Gemini returned an invalid JSON response"
        ) from exc
