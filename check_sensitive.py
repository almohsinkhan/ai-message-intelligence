import pandas as pd

from src.sensitive_detector import detect_sensitive_information


df = pd.read_csv("data/messages.csv")

print(f"Total messages: {len(df)}")

sensitive_count = 0

for _, row in df.iterrows():
    findings = detect_sensitive_information(row["message"])

    if findings:
        sensitive_count += 1

        print(f"\n{row['message_id']}")

        for finding in findings:
            print(f"  Type: {finding.sensitivity_type}")
            print(f"  Risk: {finding.risk}")
            print(f"  Masked: {finding.masked_text}")
            print(f"  Action: {finding.recommended_action}")


print("\n----------------------------")
print(f"Sensitive messages: {sensitive_count}")
print(f"Non-sensitive messages: {len(df) - sensitive_count}")

