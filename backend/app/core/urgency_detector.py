import re
from dataclasses import dataclass
from typing import List


@dataclass
class UrgencyResult:
    """
    Result returned by the urgency detector.
    """

    urgency: str
    confidence: float
    reasons: List[str]


HIGH_URGENCY_PATTERNS = [
    "immediate danger",
    "right now",
    "emergency",
    "life threat",
    "threat to life",
    "kill me",
    "murder",
    "rape",
    "sexual assault",
    "assault",
    "beating",
    "beaten",
    "violence",
    "domestic violence",
    "suicide",
    "self harm",
    "child abuse",
    "locked inside",
    "kidnapped",
    "stalking me",
    "threatening me",
    "forced out",
    "eviction today",
    "medical emergency",
    "bleeding",
]


MEDIUM_URGENCY_PATTERNS = [
    "threat",
    "harassment",
    "not paid",
    "salary pending",
    "three months",
    "many months",
    "fraud",
    "blackmail",
    "eviction",
    "termination",
    "denied treatment",
    "application delayed",
    "urgent",
    "deadline",
    "notice",
]


LOW_URGENCY_PATTERNS = [
    "how to",
    "where can i",
    "what documents",
    "process",
    "procedure",
    "status",
    "information",
    "help me understand",
]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_matches(text: str, patterns: List[str]) -> List[str]:
    matches = []

    for pattern in patterns:
        if pattern in text:
            matches.append(pattern)

    return matches


def detect_urgency(user_message: str) -> UrgencyResult:
    """
    Rule-based urgency detector.

    High urgency wins over medium urgency.
    Medium urgency wins over low urgency.
    """

    text = normalize_text(user_message)

    high_matches = find_matches(text, HIGH_URGENCY_PATTERNS)
    if high_matches:
        return UrgencyResult(
            urgency="High",
            confidence=min(len(high_matches) / 3.0, 1.0),
            reasons=high_matches,
        )

    medium_matches = find_matches(text, MEDIUM_URGENCY_PATTERNS)
    if medium_matches:
        return UrgencyResult(
            urgency="Medium",
            confidence=min(len(medium_matches) / 3.0, 1.0),
            reasons=medium_matches,
        )

    low_matches = find_matches(text, LOW_URGENCY_PATTERNS)
    if low_matches:
        return UrgencyResult(
            urgency="Low",
            confidence=min(len(low_matches) / 3.0, 1.0),
            reasons=low_matches,
        )

    return UrgencyResult(
        urgency="Unknown",
        confidence=0.0,
        reasons=[],
    )