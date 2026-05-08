import base64
import os
from pathlib import Path

from openai import OpenAI

VISION_PROMPT = """
You are SipnoSis, a symbolic oracle that interprets coffee or tea stains.

Analyze the uploaded stain image and extract:
- dominant symbolic shape
- emotional atmosphere
- movement direction
- ritual interpretation

Respond ONLY in JSON with this structure:
{
  "symbol": "...",
  "mood": "...",
  "interpretation": "..."
}
"""


def analyze_stain_image(image_path: Path, intent: str, question: str = ""):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "enabled": False,
            "reason": "OPENAI_API_KEY missing"
        }

    client = OpenAI(api_key=api_key)

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": VISION_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Intent: {intent}\nQuestion: {question}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}"
                        },
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
    )

    return {
        "enabled": True,
        "content": response.choices[0].message.content,
    }
