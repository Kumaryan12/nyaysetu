import re
from typing import Any, Dict, List, Tuple

from app.config import settings
from app.models.schemas import SourceSnippet


ALLOWED_URGENCY_VALUES = {"Low", "Medium", "High", "Unknown"}

ALLOWED_CATEGORIES = {
    "Labour Dispute",
    "Consumer Complaint",
    "Legal Aid",
    "Police Complaint",
    "Municipal Issue",
    "Healthcare Access",
    "Government Scheme",
    "Property Issue",
    "Domestic Violence / Safety",
    "Unknown",
}


HIGH_RISK_TERMS = [
    "violence",
    "threat",
    "threatened",
    "beat",
    "beaten",
    "assault",
    "abuse",
    "domestic violence",
    "harassment",
    "stalking",
    "suicide",
    "self harm",
    "kill",
    "murder",
    "rape",
    "child abuse",
    "eviction today",
    "forced out",
]


OVERCONFIDENT_PATTERNS = [
    r"\byou will win\b",
    r"\byou are guaranteed\b",
    r"\bguaranteed\b",
    r"\bdefinitely file\b",
    r"\bmust file\b",
    r"\byou must sue\b",
    r"\byou should sue\b",
    r"\bthis is illegal\b",
    r"\bthe court will\b",
    r"\bthe police will\b",
    r"\byou are entitled to\b",
]


UNSUPPORTED_DETAIL_PATTERNS = [
    r"\bwithin \d+ days\b",
    r"\bwithin \d+ months\b",
    r"\bsection \d+\b",
    r"\bIPC\b",
    r"\bCrPC\b",
    r"\bBNS\b",
    r"\bBNSS\b",
    r"\bArticle \d+\b",
]


STANDARD_DISCLAIMER = (
    "This is general legal/public-service information based on the retrieved "
    "sources, not personal legal advice. For case-specific guidance, contact "
    "the appropriate Legal Services Authority, government department, or a "
    "qualified lawyer."
)


INSUFFICIENT_SOURCE_ANSWER = (
    "I could not find enough information in the available official sources."
)


def detect_high_risk_query(user_message: str) -> bool:

    text = user_message.lower()

    return any(term in text for term in HIGH_RISK_TERMS)


def normalize_urgency(value: Any) -> str:

    if not isinstance(value, str):
        return "Unknown"

    value = value.strip()

    if value in ALLOWED_URGENCY_VALUES:
        return value

    return "Unknown"


def normalize_category(value: Any) -> str:

    if not isinstance(value, str):
        return "Unknown"

    value = value.strip()

    if value in ALLOWED_CATEGORIES:
        return value

    return "Unknown"


def contains_pattern(text: str, patterns: List[str]) -> bool:

    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def source_quality_is_weak(sources: List[SourceSnippet]) -> bool:

    if not sources:
        return True

    usable_scores = [
        source.score
        for source in sources
        if source.score is not None
    ]

    if not usable_scores:
        return False

    best_score = max(usable_scores)

    return best_score < settings.rag_min_score


def sanitize_llm_answer(answer: Dict[str, Any]) -> Dict[str, Any]:

    sanitized = {}

    sanitized["category"] = normalize_category(answer.get("category"))
    sanitized["urgency"] = normalize_urgency(answer.get("urgency"))

    simple_answer = answer.get("simple_answer", "")

    if not isinstance(simple_answer, str) or not simple_answer.strip():
        simple_answer = INSUFFICIENT_SOURCE_ANSWER

    sanitized["simple_answer"] = simple_answer.strip()

    next_steps = answer.get("next_steps", [])
    if not isinstance(next_steps, list):
        next_steps = []

    sanitized["next_steps"] = [
        str(step).strip()
        for step in next_steps
        if str(step).strip()
    ]

    documents = answer.get("documents_or_details_needed", [])
    if not isinstance(documents, list):
        documents = []

    sanitized["documents_or_details_needed"] = [
        str(doc).strip()
        for doc in documents
        if str(doc).strip()
    ]

    sanitized["insufficient_sources"] = bool(
        answer.get("insufficient_sources", False)
    )

    return sanitized


def apply_answer_guardrails(
    user_message: str,
    llm_answer: Dict[str, Any],
    sources: List[SourceSnippet],
) -> Tuple[Dict[str, Any], List[str]]:

    warnings: List[str] = []

    guarded = sanitize_llm_answer(llm_answer)

    high_risk = detect_high_risk_query(user_message)
    weak_sources = source_quality_is_weak(sources)

    if weak_sources:
        warnings.append("weak_retrieval_sources")
        guarded["simple_answer"] = INSUFFICIENT_SOURCE_ANSWER
        guarded["category"] = "Unknown"
        guarded["urgency"] = "Unknown"
        guarded["next_steps"] = [
            "Try asking with more specific details.",
            "Check whether the relevant official document has been added to the knowledge base.",
            "Contact the appropriate Legal Services Authority or government department.",
        ]
        guarded["documents_or_details_needed"] = []
        guarded["insufficient_sources"] = True
        return guarded, warnings

    if guarded.get("insufficient_sources"):
        warnings.append("llm_reported_insufficient_sources")
        guarded["simple_answer"] = INSUFFICIENT_SOURCE_ANSWER
        guarded["next_steps"] = [
            "Try asking with more specific details.",
            "Contact the relevant Legal Services Authority or official department for guidance.",
        ]
        return guarded, warnings

    answer_text = guarded["simple_answer"]

    if contains_pattern(answer_text, OVERCONFIDENT_PATTERNS):
        warnings.append("overconfident_legal_language_detected")
        guarded["simple_answer"] = (
            answer_text
            + "\n\nImportant: The system cannot determine the legal outcome of your case. "
            "Please treat this as general information and contact the appropriate authority "
            "or a qualified lawyer for case-specific guidance."
        )

    if contains_pattern(answer_text, UNSUPPORTED_DETAIL_PATTERNS):
        warnings.append("possibly_unsupported_legal_detail_detected")
        guarded["simple_answer"] = (
            answer_text
            + "\n\nNote: Any specific legal section, deadline, or procedure should be "
            "verified from the official source or with a qualified legal professional."
        )

    if high_risk:
        warnings.append("high_risk_query_detected")
        guarded["urgency"] = "High"

        safety_step = (
            "If there is immediate danger, contact local emergency services, police, "
            "or trusted local authorities immediately."
        )

        if safety_step not in guarded["next_steps"]:
            guarded["next_steps"].insert(0, safety_step)

    return guarded, warnings