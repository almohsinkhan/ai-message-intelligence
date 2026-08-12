import pandas as pd

from src.extractor import extract_event, extract_task
from src.classifier import classify_message


df = pd.read_csv("data/messages.csv")

tasks = []
events = []

for i, row in df.iterrows():

    classification = classify_message(row["message"])

    if classification.category == "action_required":

        item = extract_task(
            row["message_id"],
            row["message"],
            i + 1,
        )

    elif classification.category == "meeting_or_event":

        item = extract_event(
            row["message_id"],
            row["message"],
            i + 1,
        )

    else:
        item = None

    if item is None:
        continue

    data = {
        "item_id": item.item_id,
        "type": item.type,
        "title": item.title,
        "description": item.description,
        "date": item.date,
        "deadline": item.deadline,
        "time": item.time,
        "person": item.person,
        "priority": item.priority,
        "source_message_id": item.source_message_id,
    }

    if item.type == "task":
        tasks.append(data)
    else:
        events.append(data)


print("Tasks:", len(tasks))
print("Events:", len(events))

print("\n--- TASKS ---")

for task in tasks[:20]:
    print(task)

print("\n--- EVENTS ---")

for event in events[:20]:
    print(event)

print("\n--- TASKS WITH UNRESOLVED DEADLINE ---")

for task in tasks:
    if task["deadline"] is None:
        print(task)

print("\n--- EVENTS WITH UNRESOLVED DATE/TIME ---")

for event in events:
    if event["date"] is None or event["time"] is None:
        print(event)