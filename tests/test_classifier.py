from src.classifier import classify_message


def test_action_required():
    result = classify_message(
        "Please submit the report by 2026-09-09."
    )

    assert result.category == "action_required"


def test_meeting():
    result = classify_message(
        "Team stand-up, 2026-09-04 at 15:00, the college auditorium."
    )

    assert result.category == "meeting_or_event"


def test_promotional():
    result = classify_message(
        "Flash sale on laptops. Use code SAVE23."
    )

    assert result.category == "promotional"


def test_personal():
    result = classify_message(
        "I prefer receiving updates by email."
    )

    assert result.category == "personal_information"


def test_general():
    result = classify_message(
        "The training material is on the portal."
    )

    assert result.category == "general_information"


def test_sensitive():
    result = classify_message(
        "My card number is ****************."
    )

    assert result.category == "sensitive_information"


def test_personal_meeting_preference():
    result = classify_message(
        "I might prefer evening meetings now."
    )

    assert result.category == "personal_information"
