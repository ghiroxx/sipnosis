from backend.moderation import meter_color


def test_empty_text_is_red():
    assert meter_color("") == "red"


def test_safe_text_is_green():
    assert meter_color("I think we should discuss this calmly") == "green"


def test_caps_spam_is_yellow():
    assert meter_color("THIS IS TOO MUCH") == "yellow"


def test_hard_red_content():
    assert meter_color("kill them all") == "red"
