"""
Classifies whether a document is related to medicine/health before ingesting into Neo4j.
Only samples the first 600 words — enough to decide without wasting tokens.
"""

import json
from openai import OpenAI
from config import settings

_PROMPT = """You are a medical content classifier.

Read the document excerpt below and decide if it is related to any of these fields:
medicine, clinical research, healthcare, pharmacology, biology, public health,
medical devices, diagnostics, surgery, or any health-related topic.

Respond ONLY with a valid JSON object in this exact format — no extra text:
{{
  "is_medical": true or false,
  "confidence": "high" or "medium" or "low",
  "reason": "one sentence explaining your decision"
}}

Document excerpt:
{sample}"""


def classify_document(text: str) -> dict:
    sample = " ".join(text.split()[:600])

    client = OpenAI(
        base_url=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_KEY,
    )

    completion = client.chat.completions.create(
        model=settings.AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "user", "content": _PROMPT.format(sample=sample)}
        ],
        max_tokens=150,
        temperature=0,
    )

    raw = completion.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if model wraps in markdown code block
        cleaned = raw.strip("```json").strip("```").strip()
        result = json.loads(cleaned)

    return {
        "is_medical": bool(result.get("is_medical", False)),
        "confidence": result.get("confidence", "low"),
        "reason": result.get("reason", "No reason provided."),
    }
