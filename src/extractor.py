import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractedItem:
    item_id: str
    type: str
    title: str
    description: str
    date: Optional[str]
    deadline: Optional[str]
    time: Optional[str]
    person: Optional[str]
    priority: str
    source_message_id: str


DATE_PATTERN = r"\b\d{4}-\d{2}-\d{2}\b"
TIME_PATTERN = r"\b\d{1,2}:\d{2}\b"


# --------------------------------------------------
# Event signals
# --------------------------------------------------

EVENT_KEYWORDS = [
    "calendar update",
    "happens on",
    "scheduled for",
    "please join",
    "join the",
    "available for the",
]


# --------------------------------------------------
# Actual task/action verbs
# --------------------------------------------------

ACTION_VERBS = [
    "submit",
    "review",
    "reply",
    "confirm",
    "renew",
    "pay",
    "upload",
    "update",
    "complete",
    "send",
    "email",
    "call",
    "share",
    "check",
    "prepare",
    "fill",
]


def extract_date(text: str) -> Optional[str]:
    match = re.search(DATE_PATTERN, text)

    if match:
        return match.group(0)

    return None


def extract_time(text: str) -> Optional[str]:
    match = re.search(TIME_PATTERN, text)

    if match:
        return match.group(0)

    return None

def extract_person(text: str) -> Optional[str]:
    """
    Extract a person only when the message explicitly names one.

    We intentionally keep this conservative to avoid guessing.
    """

    patterns = [
        r"\bcall\s+([A-Z][a-z]+)\b",
        r"\bemail\s+([A-Z][a-z]+)\b",
        r"\bsend\s+(?:it|this)\s+to\s+([A-Z][a-z]+)\b",
        r"\bmeet\s+([A-Z][a-z]+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(1)

    return None


def extract_priority(text: str, item_type: str) -> str:
    text = text.lower()

    if any(
        word in text
        for word in [
            "urgent",
            "asap",
            "immediately",
        ]
    ):
        return "high"

    if "important" in text:
        return "high"

    if item_type == "task":
        return "medium"

    return "medium"


# --------------------------------------------------
# TASK EXTRACTION
# --------------------------------------------------

def extract_task(
    message_id: str,
    message: str,
    item_number: int,
) -> Optional[ExtractedItem]:

    text = message.lower()

    patterns = [
        r"don't forget to (?P<action>.+?)(?:;|$)",
        r"please (?P<action>.+?)(?:\.|$)",
        r"need you to (?P<action>.+?)(?:\.|$)",
        r"can you (?P<action>.+?)(?:\?|$)",
        r"could you (?P<action>.+?)(?:\?|$)",
        r"if possible, (?P<action>.+?)(?:\.|$)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        action = match.group("action").strip()
        action_lower = action.lower()

        # Remove common message prefixes that are not part
        # of the actual task.
        action = re.sub(
            r"^(?:note|fyi|important|quick update|one more thing|"
            r"just checking|for today|please note)\s*:\s*",
            "",
            action,
            flags=re.IGNORECASE,
        ).strip()

        action_lower = action.lower()

        # --------------------------------------------------
        # Reject conversational/non-action phrases
        # --------------------------------------------------

        if action_lower in {
            "help",
            "assist",
            "let me know",
        }:
            continue

        # "I will send..." is a statement, not a task
        # assigned to the recipient.
        if action_lower.startswith(
            (
                "i will ",
                "i'll ",
                "i can ",
                "i am ",
                "i'm ",
            )
        ):
            continue

        # Reject uncertainty/preferences.
        if any(
            phrase in action_lower
            for phrase in [
                "could be",
                "might be",
                "could happen",
                "might happen",
                "could be friday",
                "might be friday",
            ]
        ):
            continue

        # --------------------------------------------------
        # Make sure there is an actual action
        # --------------------------------------------------

        has_real_action = any(
            re.search(
                rf"\b{re.escape(verb)}\b",
                action_lower,
            )
            for verb in ACTION_VERBS
        )

        if not has_real_action:
            continue

        # --------------------------------------------------
        # Remove deadline from title/description
        # --------------------------------------------------

        action = re.sub(
            r"\s*(?:by|before|deadline is|due on)\s+"
            + DATE_PATTERN,
            "",
            action,
            flags=re.IGNORECASE,
        ).strip()

        if not action:
            continue

        deadline = extract_date(message)

        title = action.rstrip(".?!").strip()

        title = re.sub(
            r"^(?:please|could you|can you|if possible)\s+",
            "",
            title,
            flags=re.IGNORECASE,
        )

        title = title.capitalize()

        return ExtractedItem(
            item_id=f"TASK_{item_number:03d}",
            type="task",
            title=title,
            description=action,
            date=None,
            deadline=deadline,
            time=None,
            person=extract_person(message),
            priority=extract_priority(
                message,
                "task",
            ),
            source_message_id=message_id,
        )

    return None


# --------------------------------------------------
# EVENT EXTRACTION
# --------------------------------------------------

def extract_event(
    message_id: str,
    message: str,
    item_number: int,
) -> Optional[ExtractedItem]:

    text = message.lower()

    # --------------------------------------------------
    # Check whether this is actually an event
    # --------------------------------------------------

    if not any(
        keyword in text
        for keyword in EVENT_KEYWORDS
    ):
        return None

    date = extract_date(message)
    time = extract_time(message)

    # --------------------------------------------------
    # Identify event title
    # --------------------------------------------------

    title = None

    patterns = [
        # Calendar update: family dinner, 2026-09-19...
        r"calendar update:\s*(.+?),\s*"
        + DATE_PATTERN,

        # Reminder: mentor catch-up happens on...
        r"reminder:\s*(.+?)\s+"
        r"(?:happens on|scheduled for)",

        # The client discussion is scheduled for...
        r"the\s+(.+?)\s+is scheduled for",

        # Please join the internship orientation on...
        r"join the\s+(.+?)\s+on",

        # Are you available for the technical interview at...
        r"available for the\s+(.+?)\s+at",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            flags=re.IGNORECASE,
        )

        if match:
            title = match.group(1).strip()
            break

    if title is None:
        title = "Unresolved event"

    # --------------------------------------------------
    # Clean title
    # --------------------------------------------------

    title = title.rstrip(".,?!").strip()

    description = message.strip()

    return ExtractedItem(
        item_id=f"EVENT_{item_number:03d}",
        type="event",
        title=title,
        description=description,
        date=date,
        deadline=None,
        time=time,
        person=extract_person(message),
        priority=extract_priority(
            message,
            "event",
        ),
        source_message_id=message_id,
    )


# --------------------------------------------------
# Combined extraction
# --------------------------------------------------

def extract_task_or_event(
    message_id: str,
    message: str,
    item_number: int,
) -> Optional[ExtractedItem]:

    # Events first.
    #
    # Example:
    # "Please join the AI workshop..."
    #
    # contains "please", which could otherwise
    # be interpreted as a task.

    event = extract_event(
        message_id,
        message,
        item_number,
    )

    if event:
        return event

    task = extract_task(
        message_id,
        message,
        item_number,
    )

    return task