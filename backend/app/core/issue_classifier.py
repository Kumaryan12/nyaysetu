import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ClassificationResult:
    """
    Result returned by the issue classifier.

    category:
        The detected issue category.

    confidence:
        Rough confidence score from 0 to 1.

    matched_keywords:
        Keywords or phrases that triggered the classification.
    """

    category: str
    confidence: float
    matched_keywords: List[str]


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Labour Dispute": [
        "salary",
        "wages",
        "unpaid",
        "not paid",
        "employer",
        "employee",
        "job",
        "workplace",
        "termination",
        "fired",
        "minimum wage",
        "overtime",
        "pf",
        "esi",
        "company not paying",
        "boss not paying",
    ],

    "Consumer Complaint": [
        "refund",
        "defective",
        "damaged product",
        "warranty",
        "guarantee",
        "seller",
        "online order",
        "order id",
        "delivery",
        "fake product",
        "wrong product",
        "consumer",
        "bill",
        "invoice",
        "service issue",
        "not delivered",
        "replacement",
    ],

    "Legal Aid": [
        "cannot afford lawyer",
        "free lawyer",
        "legal aid",
        "lawyer help",
        "advocate",
        "court help",
        "poor",
        "weaker section",
        "free legal service",
        "district legal services",
        "nalsa",
        "slsa",
        "dlsa",
    ],

    "Police Complaint": [
        "police",
        "fir",
        "complaint",
        "stolen",
        "theft",
        "fraud",
        "threat",
        "threatening",
        "assault",
        "crime",
        "missing",
        "harassment",
        "cyber crime",
        "blackmail",
        "fir copy",
        "police station",
    ],

    "Domestic Violence / Safety": [
        "domestic violence",
        "husband",
        "wife beating",
        "beating me",
        "abuse",
        "abusing",
        "violence",
        "threatening me",
        "unsafe",
        "scared",
        "stalking",
        "sexual harassment",
        "dowry",
        "in-laws",
        "forced",
        "afraid",
    ],

    "Municipal Issue": [
        "garbage",
        "drainage",
        "sewage",
        "water supply",
        "streetlight",
        "road",
        "pothole",
        "sanitation",
        "municipal",
        "ward",
        "encroachment",
        "waste",
        "dirty water",
        "mosquito",
        "public toilet",
    ],

    "Healthcare Access": [
        "hospital",
        "doctor",
        "medicine",
        "treatment",
        "ambulance",
        "healthcare",
        "medical",
        "clinic",
        "ayushman",
        "health card",
        "denied treatment",
        "patient",
        "emergency ward",
    ],

    "Government Scheme": [
        "scheme",
        "pension",
        "ration",
        "aadhaar",
        "subsidy",
        "scholarship",
        "certificate",
        "income certificate",
        "caste certificate",
        "domicile",
        "application pending",
        "government office",
        "department",
        "benefit",
    ],

    "Property Issue": [
        "land",
        "property",
        "tenant",
        "landlord",
        "rent",
        "eviction",
        "lease",
        "house",
        "flat",
        "possession",
        "registry",
        "property dispute",
        "illegal occupation",
    ],

    "Public Grievance": [
        "government department",
        "public authority",
        "application delayed",
        "delay",
        "not responding",
        "grievance",
        "cpgrams",
        "service delivery",
        "complaint portal",
        "public service",
    ],
}


def normalize_text(text: str) -> str:
    """
    Lowercases and normalizes whitespace.
    """

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def keyword_matches(text: str, keywords: List[str]) -> List[str]:
    """
    Finds which keywords appear in the query.

    Uses simple substring matching for now.
    Later we can replace this with ML classification.
    """

    matches = []

    for keyword in keywords:
        keyword_lower = keyword.lower()

        if keyword_lower in text:
            matches.append(keyword)

    return matches


def score_category(text: str, keywords: List[str]) -> Tuple[float, List[str]]:
    """
    Computes a rough score for one category.

    Score is based on:
    - number of matched keywords
    - longer phrase matches receiving slightly more weight
    """

    matches = keyword_matches(text, keywords)

    if not matches:
        return 0.0, []

    score = 0.0

    for match in matches:
        words = match.split()

        if len(words) >= 2:
            score += 2.0
        else:
            score += 1.0

    # Normalize roughly so score stays between 0 and 1.
    normalized_score = min(score / 5.0, 1.0)

    return normalized_score, matches


def classify_issue(user_message: str) -> ClassificationResult:
    """
    Rule-based issue classification.

    This is intentionally transparent and easy to debug.

    If no category crosses threshold, return Unknown.
    """

    text = normalize_text(user_message)

    best_category = "Unknown"
    best_score = 0.0
    best_matches: List[str] = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        score, matches = score_category(text, keywords)

        if score > best_score:
            best_category = category
            best_score = score
            best_matches = matches

    if best_score < 0.20:
        return ClassificationResult(
            category="Unknown",
            confidence=0.0,
            matched_keywords=[],
        )

    return ClassificationResult(
        category=best_category,
        confidence=best_score,
        matched_keywords=best_matches,
    )