from src.extractor import extract_task_or_event


def test_task_with_deadline():

    result = extract_task_or_event(
        "MSG_0010",
        "Can you help? Don't forget to pay the electricity bill; deadline is 2026-09-09.",
        1,
    )

    assert result is not None
    assert result.type == "task"
    assert result.deadline == "2026-09-09"


def test_join_event():

    result = extract_task_or_event(
        "MSG_0011",
        "Please join the internship orientation on 2026-09-18, 13:00 at Conference Room 2.",
        2,
    )

    assert result is not None
    assert result.type == "event"
    assert result.date == "2026-09-18"
    assert result.time == "13:00"


def test_scheduled_event():

    result = extract_task_or_event(
        "MSG_0042",
        "The client discussion is scheduled for 2026-09-12 at 11:00 in Meeting Room A.",
        3,
    )

    assert result is not None
    assert result.type == "event"
    assert result.date == "2026-09-12"
    assert result.time == "11:00"


def test_personal_meeting_preference_is_not_event():

    result = extract_task_or_event(
        "MSG_0024",
        "I might prefer evening meetings now.",
        4,
    )

    assert result is None


def test_missing_information():

    result = extract_task_or_event(
        "MSG_0041",
        "If possible, review the file before the meeting.",
        5,
    )

    assert result is not None
    assert result.type == "task"
    assert result.deadline is None
    assert result.time is None


def test_task_without_deadline():

    result = extract_task_or_event(
        "MSG_TEST",
        "If possible, review the file before the meeting.",
        6,
    )

    assert result is not None
    assert result.type == "task"
    assert result.title == "Review the file before the meeting"
    assert result.deadline is None
    assert result.time is None



def test_person_extraction():
    result = extract_task_or_event(
        "MSG_PERSON",
        "Can you call Maya when you are free?",
        7,
    )

    assert result is not None
    assert result.type == "task"
    assert result.person == "Maya"


def test_person_missing():
    result = extract_task_or_event(
        "MSG_NO_PERSON",
        "Please review the privacy checklist by 2026-09-09.",
        8,
    )

    assert result is not None
    assert result.person is None