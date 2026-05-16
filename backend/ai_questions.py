from datetime import datetime, timezone
from typing import Optional

from openai import OpenAI

from backend.config import OPENAI_API_KEY, OPENAI_MODEL

SYSTEM_PROMPT = (
    "You are AgorHour's Question Master. Generate ONE concise, open-ended debate question.\n"
    "Rules:\n"
    "- Max 120 characters.\n"
    "- Plain English, neutral→mildly provocative.\n"
    "- Safe-for-work; no NSFW/hate/personal data.\n"
    "- Rotate themes: life, love, food, work, ethics, society, culture, politics (soft), tech, future.\n"
    "- Output ONLY the question."
)

THEMES = [
    "life",
    "love",
    "food",
    "work",
    "ethics",
    "society",
    "culture",
    "politics",
    "tech",
    "future",
]

FALLBACK_QUESTIONS = {
    "life": "Is happiness more comfort or challenge?",
    "love": "Can long-distance love really last?",
    "food": "Is fast food killing tradition or saving time?",
    "work": "Should employers track digital productivity?",
    "ethics": "Is lying ever the right choice?",
    "society": "Does anonymity make discourse better?",
    "culture": "Do memes count as modern art?",
    "politics": "Do term limits make democracy stronger?",
    "tech": "Is AI more tool or threat?",
    "future": "Will humans settle Mars in your lifetime?",
}

ai_client: Optional[OpenAI] = None

if OPENAI_API_KEY:
    ai_client = OpenAI(api_key=OPENAI_API_KEY)


def current_theme_for_hour(dt: datetime) -> str:
    base = int(dt.astimezone(timezone.utc).strftime("%s")) // 3600
    return THEMES[base % len(THEMES)]


def ai_generate_question(last_headline: str, next_theme: str) -> str:
    if not ai_client:
        return FALLBACK_QUESTIONS.get(next_theme, "Is disagreement a sign of progress?")

    user_prompt = (
        f"Generate one question (<120 chars) for this hour.\n"
        f"Recent headline: {last_headline[:180]}\n"
        f"Theme: {next_theme}"
    )

    try:
        response = ai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=60,
        )

        question = response.choices[0].message.content.strip().strip('"')
        return question[:120]

    except Exception:
        return "Is disagreement a sign of progress?"
