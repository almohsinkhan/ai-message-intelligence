import pandas as pd

from src.pipeline import process_message


MESSAGES = "data/messages.csv"
MANDATORY = "data/mandatory_demo_ids.csv"


messages_df = pd.read_csv(MESSAGES)
mandatory_df = pd.read_csv(MANDATORY)

message_lookup = {
    row["message_id"]: row
    for _, row in messages_df.iterrows()
}


print("=" * 70)
print("MANDATORY DEMONSTRATION MESSAGE VERIFICATION")
print("=" * 70)

for index, row in mandatory_df.iterrows():

    message_id = row["message_id"]

    message = message_lookup.get(message_id)

    if message is None:
        print(f"\n{message_id}: NOT FOUND")
        continue

    result = process_message(
        message_id=message_id,
        message=message["message"],
        item_number=int(index) + 1,
    )

    print(f"\n{message_id}")
    print("-" * 50)

    print(
        f"Category: {result['message']['category']}"
    )

    print(
        f"Confidence: {result['message']['confidence']}"
    )

    print(
        f"Reason: {result['message']['reason']}"
    )

    if result["task_event"]:

        item = result["task_event"]

        print(f"Type: {item['type']}")
        print(f"Title: {item['title']}")
        print(f"Date: {item['date']}")
        print(f"Deadline: {item['deadline']}")
        print(f"Time: {item['time']}")
        print(f"Person: {item['person']}")
        print(f"Priority: {item['priority']}")

    if result["sensitive"]:

        sensitive = result["sensitive"]

        print(
            f"Sensitivity type: "
            f"{sensitive['sensitivity_type']}"
        )

        print(
            f"Risk: {sensitive['risk']}"
        )

        print(
            f"Masked: {sensitive['masked_text']}"
        )

        print(
            f"Action: "
            f"{sensitive['recommended_action']}"
        )
