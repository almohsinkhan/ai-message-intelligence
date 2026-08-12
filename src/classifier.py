import re
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    reason: str


CATEGORIES = [
    "action_required",
    "meeting_or_event",
    "personal_information",
    "general_information",
    "promotional",
    "sensitive_information",
]


# Strong signals for each category.
KEYWORDS = {
    "action_required": {
    "submit": 4,
    "complete": 4,
    "reply": 3,
    "confirm": 3,
    "renew": 3,
    "pay": 4,
    "upload": 4,
    "respond": 3,
    "deadline": 4,
    "need you to": 4,
    "don't forget": 3,
    },

    "meeting_or_event": {
        "meeting": 3,
        "orientation": 5,
        "seminar": 5,
        "stand-up": 5,
        "catch-up": 4,
        "appointment": 5,
        "webinar": 4,
        "interview": 3,
        "session": 3,
        "scheduled": 3,
        "join": 2,
    },

    "promotional": {
        "sale": 5,
        "discount": 5,
        "offer": 4,
        "coupon": 5,
        "premium plan": 5,
        "exclusive benefits": 4,
        "promo": 4,
        "code save": 4,
    },

    "personal_information": {
        "i prefer": 5,
        "my favourite": 5,
        "my favorite": 5,
        "i am vegetarian": 5,
        "i drink": 4,
        "my emergency contact": 5,
        "for my profile": 3,
        "personal note": 3,
    },

    "general_information": {
        "fyi": 2,
        "available": 2,
        "now available": 3,
        "will be under maintenance": 3,
        "leaves every": 3,
        "is on the portal": 3,
        "was reorganized": 3,
        "is fully charged": 3,
    },
}


def contains_date(text: str) -> bool:
    return bool(
        re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
    )


def contains_time(text: str) -> bool:
    return bool(
        re.search(
            r"\b\d{1,2}:\d{2}\b",
            text
        )
    )

REQUEST_PATTERNS = [
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bplease\b",
    r"\bi need you to\b",
    r"\bdon't forget\b",
    r"\bplease make sure\b",
]

ACTION_VERBS = [
    "submit",
    "complete",
    "review",
    "reply",
    "confirm",
    "renew",
    "pay",
    "upload",
    "respond",
    "update",
    "send",
]

def classify_message(message: str) -> ClassificationResult:
    """
    Classify a message using weighted semantic signals.

    This is deliberately deterministic and explainable.
    """

    text = message.lower()

    
    scores = {
        category: 0
        for category in CATEGORIES
    }

    reasons = {
        category: []
        for category in CATEGORIES
    }

    # --------------------------------------------------
    # Explicit request detection
    # --------------------------------------------------

    has_request = any(
        re.search(pattern, text)
        for pattern in REQUEST_PATTERNS
    )

    requested_action = any(
        re.search(rf"\b{re.escape(verb)}\b", text)
        for verb in ACTION_VERBS
    )

    if has_request and requested_action:
        scores["action_required"] += 4
        reasons["action_required"].append(
            "contains an explicit request to perform an action"
        )

        
    # --------------------------------------------------
    # Sensitive information
    # --------------------------------------------------

    sensitive_terms = [
        "password",
        "otp",
        "card number",
        "bank account",
        "recovery code",
        "identification number",
        "home address",
        "access token",
        "contact me on",
    ]

    for term in sensitive_terms:
        if term in text:
            scores["sensitive_information"] += 10
            reasons["sensitive_information"].append(
                f"contains sensitive indicator '{term}'"
            )

    # --------------------------------------------------
    # Keyword scoring
    # --------------------------------------------------

    for category, keywords in KEYWORDS.items():

        for keyword, weight in keywords.items():

            if keyword in text:
                scores[category] += weight
                reasons[category].append(
                    f"contains '{keyword}'"
                )

    # --------------------------------------------------
    # Date/time context
    # --------------------------------------------------

    has_date = contains_date(text)
    has_time = contains_time(text)

    # A date/time strengthens event classification,
    # but does NOT automatically make something an event.

    event_terms = [
    "meeting",
    "orientation",
    "seminar",
    "stand-up",
    "catch-up",
    "appointment",
    "webinar",
    "interview",
    "calendar update",
    "scheduled",
    ]

    if has_date and has_time:
        if any(term in text for term in event_terms):
            scores["meeting_or_event"] += 4
            reasons["meeting_or_event"].append(
                "contains an event-related date and time"
            )

    # handling join 
    event_attendance_terms = [
        "join the",
        "attend the",
        "calendar update",
        "scheduled for",
    ]

    if any(term in text for term in event_attendance_terms):
        scores["meeting_or_event"] += 3
        reasons["meeting_or_event"].append(
            "contains an event attendance or scheduling signal"
        )

    # --------------------------------------------------
    # Action + deadline
    # --------------------------------------------------

    action_terms = [
        "submit",
        "complete",
        "review",
        "reply",
        "confirm",
        "renew",
        "pay",
        "upload",
        "send",
        "respond",
        "don't forget",
        "need you to",
    ]

    if has_date and any(term in text for term in action_terms):
        scores["action_required"] += 3
        reasons["action_required"].append(
            "contains an action with a date/deadline"
        )

    # --------------------------------------------------
    # Personal preference overrides
    # --------------------------------------------------

    personal_preference_patterns = [
        "i prefer",
        "i might prefer",
        "my favourite",
        "my favorite",
        "i am vegetarian",
        "i drink",
    ]

    if any(pattern in text for pattern in personal_preference_patterns):
        scores["personal_information"] += 6
        reasons["personal_information"].append(
            "expresses a personal preference or characteristic"
        )

    # --------------------------------------------------
    # Determine result
    # --------------------------------------------------

    max_score = max(scores.values())

    if max_score == 0:
        return ClassificationResult(
            category="general_information",
            confidence=0.50,
            reason="No strong action, event, personal, promotional, or sensitive signal was detected."
        )

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    category = ranked[0][0]

    # Convert score into a bounded confidence.
    second_score = ranked[1][1]

    if max_score == second_score:
        confidence = 0.55
    else:
        confidence = min(
            0.99,
            0.60 + (
                (max_score - second_score) /
                max(max_score, 10)
            ) * 0.35
        )

    reason_parts = reasons[category]

    if reason_parts:
        reason = "; ".join(reason_parts)
    else:
        reason = "classified using available message signals"

    return ClassificationResult(
        category=category,
        confidence=round(confidence, 2),
        reason=reason,
    )