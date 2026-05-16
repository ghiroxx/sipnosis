import re

HARD_RED_PATTERNS = [
    r"\\b(kill|murder|rape|lynch|gas|exterminate)\\b",
    r"\\b(doxx|address|phone|ssn)\\b",
    r"\\b(slur1|slur2|slur3)\\b",
]

MILD_YELLOW_PATTERNS = [
    r"[A-Z]{5,}",
    r"[!?.]{3,}",
    r"\\b(damn|hell|crap)\\b",
]


def meter_color(text: str) -> str:
    normalized = text.strip().lower()

    if not normalized:
        return "red"

    for pattern in HARD_RED_PATTERNS:
        if re.search(pattern, normalized):
            return "red"

    for pattern in MILD_YELLOW_PATTERNS:
        if re.search(pattern, normalized):
            return "yellow"

    if len(text) > 110:
        return "yellow"

    return "green"
