import json
import pandas as pd

from src.classifier import classify_message
from src.extractor import extract_task, extract_event
from src.sensitive_detector import detect_sensitive_information


def process_message(message_id: str, message: str, item_number: int):
    """
    Privacy-first processing of one message.

    1. Detect sensitive information first.
    2. If sensitive, never send the raw message to downstream processing.
    3. Otherwise classify the message.
    4. Extract a task/event when appropriate.
    """

    # --------------------------------------------------
    # STEP 1: Sensitive detection
    # --------------------------------------------------

    findings = detect_sensitive_information(message)

    if findings:

        finding = findings[0]

        return {
            "message": {
                "message_id": message_id,
                "category": "sensitive_information",
                "confidence": 0.99,
                "reason": (
                    f"Detected {finding.sensitivity_type} "
                    "using a sensitive-information pattern."
                ),
            },
            "task_event": None,
            "sensitive": {
                "message_id": message_id,
                "sensitivity_type": finding.sensitivity_type,
                "risk": finding.risk,
                "masked_text": finding.masked_text,
                "recommended_action": finding.recommended_action,
            },
        }

    # --------------------------------------------------
    # STEP 2: Classification
    # --------------------------------------------------

    classification = classify_message(message)

    message_result = {
        "message_id": message_id,
        "category": classification.category,
        "confidence": classification.confidence,
        "reason": classification.reason,
    }

    # --------------------------------------------------
    # STEP 3: Task/Event extraction
    # --------------------------------------------------

    extracted = None

    if classification.category == "action_required":

        extracted = extract_task(
            message_id,
            message,
            item_number,
        )

    elif classification.category == "meeting_or_event":

        extracted = extract_event(
            message_id,
            message,
            item_number,
        )

    task_event = None

    if extracted:

        task_event = {
            "item_id": extracted.item_id,
            "type": extracted.type,
            "title": extracted.title,
            "description": extracted.description,
            "date": extracted.date,
            "deadline": extracted.deadline,
            "time": extracted.time,
            "person": extracted.person,
            "priority": extracted.priority,
            "source_message_id": extracted.source_message_id,
        }

    return {
        "message": message_result,
        "task_event": task_event,
        "sensitive": None,
    }


def process_dataset(input_path: str):
    df = pd.read_csv(input_path)

    classifications = []
    task_events = []
    sensitive_records = []

    # Dataset is already chronological.
    for index, row in df.iterrows():

        result = process_message(
            message_id=row["message_id"],
            message=row["message"],
            item_number=index + 1,
        )

        classifications.append(result["message"])

        if result["task_event"] is not None:
            task_events.append(result["task_event"])

        if result["sensitive"] is not None:
            sensitive_records.append(result["sensitive"])

    return (
        classifications,
        task_events,
        sensitive_records,
    )


def save_outputs(input_path: str):

    (
        classifications,
        task_events,
        sensitive_records,
    ) = process_dataset(input_path)

    # --------------------------------------------------
    # Classification output
    # --------------------------------------------------

    pd.DataFrame(classifications).to_csv(
        "outputs/message_classification.csv",
        index=False,
    )

    # --------------------------------------------------
    # Task/Event output
    # --------------------------------------------------

    with open(
        "outputs/extracted_tasks_events.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            task_events,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------
    # Sensitive output
    # --------------------------------------------------

    pd.DataFrame(sensitive_records).to_csv(
        "outputs/sensitive_information.csv",
        index=False,
    )

    print(f"Processed messages: {len(classifications)}")
    print(f"Tasks/events: {len(task_events)}")
    print(f"Sensitive messages: {len(sensitive_records)}")

    print("\nCategory distribution:")

    print(
        pd.DataFrame(classifications)[
            "category"
        ].value_counts()
    )


if __name__ == "__main__":

    save_outputs(
        "data/messages.csv"
    )