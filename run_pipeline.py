from src.pipeline import process_dataset


INPUT = "data/messages.csv"
OUTPUT = "outputs/message_classification.csv"


df = process_dataset(INPUT)

df.to_csv(OUTPUT, index=False)

print(f"Processed {len(df)} messages.")
print(f"Saved results to: {OUTPUT}")

print("\nCategory distribution:")
print(df["category"].value_counts())
