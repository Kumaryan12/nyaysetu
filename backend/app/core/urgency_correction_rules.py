import re
from typing import List, Tuple


URGENCY_ORDER = {
    "Unknown": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
}


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_any(text: str, phrases: List[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def max_urgency(a: str, b: str) -> str:
    if URGENCY_ORDER.get(b, 0) > URGENCY_ORDER.get(a, 0):
        return b
    return a


def apply_urgency_correction(
    user_message: str,
    predicted_urgency: str,
) -> Tuple[str, List[str]]:
    """
    Applies high-precision urgency overrides.

    Safety principle:
    Missing a High urgency case is worse than over-escalating.
    """

    text = normalize(user_message)
    reasons: List[str] = []

    high_risk_terms = [
        "immediate danger",
        "right now",
        "emergency",
        "kill me",
        "threatening to kill",
        "break the door",
        "locked inside",
        "locked me",
        "not let me leave",
        "took my phone",
        "phone le liya",
        "missing child",
        "child has not returned",
        "daughter has not returned",
        "son is missing",
        "wife is missing",
        "husband is missing",
        "phone is off",
        "ambulance is not coming",
        "patient is unconscious",
        "bleeding",
        "acid attack",
        "private photos",
        "leak my photos",
        "morphed my photo",
        "sending my photos",
        "threatening my contacts",
        "loan app is sending",
        "stalking",
        "following me",
        "waiting outside",
        "domestic violence",
        "beating",
        "maar raha",
        "maar peet",
        "rape",
        "sexual assault",
    ]

    if contains_any(text, high_risk_terms):
        reasons.append("high_risk_safety_pattern")
        return "High", reasons

    medium_terms = [
        "salary pending",
        "not paid",
        "delayed salary",
        "refund",
        "not refunded",
        "pending for months",
        "eviction notice",
        "ration benefit stopped",
        "passport pending",
        "verification pending",
        "security deposit",
        "grievance closed",
        "complaint ignored",
        "fraud happened",
        "money is gone",
    ]

    if contains_any(text, medium_terms):
        corrected = max_urgency(predicted_urgency, "Medium")
        if corrected != predicted_urgency:
            reasons.append("medium_grievance_pattern")
        return corrected, reasons

    return predicted_urgency, reasons