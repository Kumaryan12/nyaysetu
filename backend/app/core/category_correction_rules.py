import re
from typing import List, Tuple


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_any(text: str, phrases: List[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def apply_category_correction(
    user_message: str,
    predicted_category: str,
) -> Tuple[str, List[str]]:
    """
    Applies high-precision category corrections.

    This is not a replacement for the ML classifier.
    It only fixes known high-risk or high-confusion patterns.
    """

    text = normalize(user_message)
    reasons: List[str] = []

    # Legal Aid override:
    # If the user's main problem is inability to afford lawyer/advocate,
    # classify as Legal Aid even if the case type is police/property/labour.
    legal_aid_terms = [
        "cannot pay advocate",
        "can't pay advocate",
        "cannot afford advocate",
        "cannot afford lawyer",
        "can't afford lawyer",
        "no money for lawyer",
        "free lawyer",
        "free advocate",
        "legal aid",
        "government lawyer",
        "district legal authority",
        "dlsa",
        "nalsa",
    ]

    if contains_any(text, legal_aid_terms):
        reasons.append("legal_aid_affordability_or_free_lawyer_pattern")
        return "Legal Aid", reasons

    # Domestic Violence / Safety override:
    # Family/relationship control, confinement, coercion, threats.
    family_terms = [
        "husband",
        "wife",
        "partner",
        "boyfriend",
        "in laws",
        "in-laws",
        "sasural",
        "ghar wale",
    ]

    safety_control_terms = [
        "locked me",
        "locked inside",
        "not allowing me",
        "took my phone",
        "phone le liya",
        "does not let me leave",
        "not let me leave",
        "controls",
        "threatens me",
        "maar",
        "beating",
        "violence",
        "abuse",
        "torture",
        "dowry",
        "dahej",
    ]

    if contains_any(text, family_terms) and contains_any(text, safety_control_terms):
        reasons.append("family_or_relationship_safety_control_pattern")
        return "Domestic Violence / Safety", reasons

    # Stalking / following / private photo threats:
    safety_stalking_terms = [
        "stalking",
        "follows me",
        "following me",
        "waiting outside",
        "private photos",
        "leak my photos",
        "morphed my photo",
        "acid attack",
    ]

    if contains_any(text, safety_stalking_terms):
        reasons.append("stalking_or_private_image_threat_pattern")
        return "Domestic Violence / Safety", reasons

    # Consumer Complaint override:
    # Product/service seller/provider problems.
    consumer_terms = [
        "wrong medicines",
        "wrong medicine",
        "online pharmacy",
        "pharmacy sent",
        "broadband company",
        "connection not installed",
        "charged twice",
        "refund",
        "replacement",
        "defective",
        "duplicate",
        "empty box",
        "delivery app",
        "cab",
        "hotel charged",
        "coaching center denied refund",
        "repair shop",
    ]

    if contains_any(text, consumer_terms):
        reasons.append("consumer_product_or_service_provider_pattern")
        return "Consumer Complaint", reasons

    # Property Issue override:
    property_terms = [
        "security deposit",
        "landlord",
        "tenant",
        "builder",
        "flat",
        "rent",
        "lease",
        "possession",
        "registry",
        "agreement",
    ]

    if contains_any(text, property_terms):
        reasons.append("property_landlord_tenant_builder_pattern")
        return "Property Issue", reasons

    # Labour Dispute override:
    labour_terms = [
        "stipend",
        "internship stipend",
        "intern stipend",
        "weekly payment",
        "delivery boy",
        "salary",
        "wages",
        "payout",
        "final settlement",
    ]

    if contains_any(text, labour_terms):
        reasons.append("work_payment_salary_stipend_pattern")
        return "Labour Dispute", reasons

    return predicted_category, reasons