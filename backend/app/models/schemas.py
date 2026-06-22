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