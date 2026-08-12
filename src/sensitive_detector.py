from dataclasses import dataclass
from typing import List
import re


@dataclass
class SensitiveFinding:
    sensitivity_type: str
    risk: str
    masked_text: str
    recommended_action: str



# patterns are intentionally focused on the dataset
PATTERNS = {
    "one_time_password": [
        r"\bOTP\b\s*(?:is|:)?\s*[\w-]+",
    ],

    "password": [
        r"\bpassword\b\s*(?:is|:)?\s*\S+",
    ],

    "bank_account": [
        r"\bbank account\b(?:\s*(?:number|no\.?))?\s*(?:is|:)?\s*\S+",
    ],

    "account_recovery_code": [
        r"\baccount recovery code\b\s*(?:is|:)?\s*[\w-]+",
    ],

    "identification_number": [
        r"\bidentification number\b\s*(?:is|:)?\s*[\w-]+",
    ],

    "card_number": [
        r"\b(?:card number|credit card|debit card)\b\s*(?:is|:)?\s*[\d\s-]+",
    ],

    "home_address": [
        r"\bhome address\b\s*(?:is|:)?\s*.+?(?=\.|$)",
    ],

    "authentication_token": [
    r"\btemporary access token\b\s*(?:is|:)?\s*[\w-]+",
    ],

    "phone_number": [
        r"\b(?:contact me on|phone(?: number)?(?: is|:)?|mobile(?: number)?(?: is|:)?)\s*[\d\s-]+",
    ],

    "health_information": [
    r"\b(?:medical|health|test result|diagnosis|condition)\b.*",
    ],
}


RISK_LEVELS = {
    "one_time_password": "high",
    "password": "high",
    "bank_account": "high",
    "account_recovery_code": "high",
    "identification_number": "high",
    "card_number": "high",
    "home_address": "medium",
    "phone_number": "medium",
    "authentication_token": "high",
    "health_information": "high",
}

RECOMMENDED_ACTIONS = {
    "one_time_password": "do_not_store",
    "password": "do_not_store",
    "bank_account": "do_not_send_to_external_service",
    "account_recovery_code": "do_not_store",
    "identification_number": "ask_for_confirmation",
    "card_number": "do_not_store",
    "home_address": "ask_for_confirmation",
    "phone_number": "ask_for_confirmation",
    "authentication_token": "do_not_store",
    "health_information": "do_not_store",
}

def detect_sensitive_information(message: str) -> List[SensitiveFinding]:
    """
    Detect sensitive information and return only masked findings.

    Raw sensitive values should never be returned by this function.
    """

    findings = []

    for sensitivity_type, patterns in PATTERNS.items():

        for pattern in patterns:
            matches = re.finditer(
                pattern,
                message,
                flags=re.IGNORECASE
            )

            for match in matches:
                original = match.group(0)

                masked = mask_match(
                    original,
                    sensitivity_type
                )

                findings.append(
                    SensitiveFinding(
                        sensitivity_type=sensitivity_type,
                        risk=RISK_LEVELS[sensitivity_type],
                        masked_text=masked,
                        recommended_action=(
                            RECOMMENDED_ACTIONS[sensitivity_type]
                        ),
                    )
                )

    return findings

def mask_match(text: str, sensitivity_type: str) -> str:
    """
    Replace the sensitive value while preserving useful context.
    """

    if sensitivity_type == "one_time_password":
        return re.sub(
            r"(\bOTP\b\s*(?:is|:)?\s*)[\w-]+",
            r"\1******",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "password":
        return re.sub(
            r"(\bpassword\b\s*(?:is|:)?\s*)\S+",
            r"\1******",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "bank_account":
        return re.sub(
            r"(\bbank account\b(?:\s*(?:number|no\.?))?\s*(?:is|:)?\s*)\S+",
            r"\1******",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "account_recovery_code":
        return re.sub(
            r"(\baccount recovery code\b\s*(?:is|:)?\s*)[\w-]+",
            r"\1********",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "identification_number":
        return re.sub(
            r"(\bidentification number\b\s*(?:is|:)?\s*)[\w-]+",
            r"\1********",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "card_number":
        return re.sub(
            r"(\b(?:card number|credit card|debit card)\b\s*(?:is|:)?\s*)[\d\s-]+",
            r"\1****************",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "home_address":
        return re.sub(
            r"(\bhome address\b\s*(?:is|:)?\s*).+",
            r"\1[REDACTED]",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "authentication_token":
        return re.sub(
            r"(\btemporary access token\b\s*(?:is|:)?\s*)[\w-]+",
            r"\1********",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "phone_number":
        return re.sub(
            r"(\b(?:contact me on|phone(?: number)?(?: is|:)?|mobile(?: number)?(?: is|:)?)\s*)[\d\s-]+",
            r"\1[REDACTED]",
            text,
            flags=re.IGNORECASE
        )

    if sensitivity_type == "health_information":
        return "[REDACTED HEALTH INFORMATION]"
    
    return "[REDACTED]"


