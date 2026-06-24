from typing import Literal, Optional, List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    User query sent to the legal-aid assistant.
    """

    message: str = Field(
        ...,
        min_length=5,
        max_length=3000,
        description="The user's legal/grievance question or complaint.",
    )

    language: Optional[str] = Field(
        default=None,
        description="Optional user language, for example: en, hi, ta, te.",
    )


class SourceSnippet(BaseModel):
    """
    A retrieved official source passage used by the RAG system.
    """

    title: str
    source_type: str = "official_document"
    url: Optional[str] = None
    text: str
    score: Optional[float] = None


class ChatResponse(BaseModel):
    """
    Structured response returned by NyayaSetu.
    """

    category: Optional[str] = None

    urgency: Literal["Low", "Medium", "High", "Unknown"] = "Unknown"

    simple_answer: str

    next_steps: List[str] = []

    documents_or_details_needed: List[str] = []

    disclaimer: str = (
        "This is general legal information based on retrieved sources, "
        "not personal legal advice. For case-specific guidance, contact "
        "a qualified lawyer or the appropriate Legal Services Authority."
    )

    sources: List[SourceSnippet] = []


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class ClassifierDebugResponse(BaseModel):
    user_message: str

    ml_issue_available: bool
    ml_issue_category: Optional[str] = None
    ml_issue_confidence: Optional[float] = None
    ml_issue_top_categories: List[str] = []
    ml_issue_top_scores: List[float] = []

    rule_issue_category: str
    rule_issue_confidence: float
    rule_issue_matched_keywords: List[str] = []

    final_issue_category_before_correction: str
    final_issue_category_after_correction: str
    category_correction_reasons: List[str] = []

    ml_urgency_available: bool
    ml_urgency: Optional[str] = None
    ml_urgency_confidence: Optional[float] = None
    ml_urgency_top_urgencies: List[str] = []
    ml_urgency_top_scores: List[float] = []

    rule_urgency: str
    rule_urgency_confidence: float
    rule_urgency_reasons: List[str] = []

    final_urgency_before_correction: str
    final_urgency_after_correction: str
    urgency_correction_reasons: List[str] = []

    retrieved_sources: List[SourceSnippet] = []

class ClassifierDebugResponse(BaseModel):
    user_message: str

    ml_issue_available: bool
    ml_issue_category: Optional[str] = None
    ml_issue_confidence: Optional[float] = None
    ml_issue_top_categories: List[str] = []
    ml_issue_top_scores: List[float] = []

    rule_issue_category: str
    rule_issue_confidence: float
    rule_issue_matched_keywords: List[str] = []

    final_issue_category_before_correction: str
    final_issue_category_after_correction: str
    category_correction_reasons: List[str] = []

    ml_urgency_available: bool
    ml_urgency: Optional[str] = None
    ml_urgency_confidence: Optional[float] = None
    ml_urgency_top_urgencies: List[str] = []
    ml_urgency_top_scores: List[float] = []

    rule_urgency: str
    rule_urgency_confidence: float
    rule_urgency_reasons: List[str] = []

    final_urgency_before_correction: str
    final_urgency_after_correction: str
    urgency_correction_reasons: List[str] = []

    retrieved_sources: List[SourceSnippet] = []