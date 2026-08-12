import pandas as pd
from collections import Counter

from src.classifier import classify_message


df = pd.read_csv("data/messages.csv")

results = []

for _, row in df.iterrows():
    result = classify_message(row["message"])

    results.append({
        "message_id": row["message_id"],
        "category": result.category,
        "confidence": result.confidence,
        "reason": result.reason,
    })


counts = Counter(r["category"] for r in results)

print("\nClassification distribution")
print("---------------------------")

for category, count in counts.items():
    print(f"{category}: {count}")

print("\nLow-confidence messages")
print("-----------------------")

for result in results:
    if result["confidence"] < 0.70:
        print(
            f"{result['message_id']} | "
            f"{result['category']} | "
            f"{result['confidence']} | "
            f"{result['reason']}"
        )
