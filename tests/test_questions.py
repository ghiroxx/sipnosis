from datetime import datetime, timezone

from backend.ai_questions import ai_generate_question, current_theme_for_hour


def test_theme_rotation_returns_valid_theme():
    theme = current_theme_for_hour(datetime.now(timezone.utc))
    assert isinstance(theme, str)
    assert len(theme) > 0


def test_fallback_question_generation():
    question = ai_generate_question("headline", "tech")
    assert isinstance(question, str)
    assert len(question) > 0
    assert len(question) <= 120
