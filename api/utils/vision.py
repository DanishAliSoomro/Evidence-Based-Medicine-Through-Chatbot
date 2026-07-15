"""
Converts an image (base64 dataUrl) into a text description using GPT-4o mini vision.
The returned text is plain English — ready to be injected as context into any LLM prompt.
"""

from openai import OpenAI
from config import settings


def describe_image(image_data_url: str) -> str:
    client = OpenAI(
        base_url=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_KEY,
    )

    completion = client.chat.completions.create(
        model=settings.AZURE_DEPLOYMENT_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url},
                    },
                    {
                        "type": "text",
                        "text": (
                            "You are a medical document analyst. "
                            "Extract and describe everything visible in this image. "
                            "If it contains text, transcribe it exactly. "
                            "If it contains charts, tables, or diagrams, describe what they show. "
                            "If it is a medical image (X-ray, scan, ECG), describe the findings. "
                            "Be thorough and precise. Return plain text only."
                        ),
                    },
                ],
            }
        ],
        max_tokens=1000,
    )

    return completion.choices[0].message.content
