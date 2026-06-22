from fastapi import APIRouter

from app.core.answer_guardrails import apply_answer_guardrails
from app.core.issue_classifier import classify_issue
from app.core.prompt_templates import build_rag_prompt
from app.core.urgency_detector import detect_urgency
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import GroqLLMService, LLMServiceError
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])

rag_service = RAGService()
llm_service = GroqLLMService()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.

    Flow:
    1. Classify user issue using deterministic classifier
    2. Detect urgency using deterministic urgency detector
    3. Retrieve relevant official source chunks
    4. Send retrieved chunks to Groq
    5. Apply guardrails
    6. Return structured response
    """

    issue_result = classify_issue(request.message)
    urgency_result = detect_urgency(request.message)

    sources = rag_service.retrieve_sources(
        query=request.message,
        top_k=5,
    )

    if not sources:
        return ChatResponse(
            category=issue_result.category,
            urgency=urgency_result.urgency,
            simple_answer=(
                "I could not find enough information in the available official "
                "sources. Please contact the appropriate authority, Legal Services "
                "Authority, or a qualified lawyer for case-specific guidance."
            ),
            next_steps=[
                "Try asking with more specific details.",
                "Make sure the relevant official documents have been added to the knowledge base.",
                "Contact the appropriate Legal Services Authority or government department.",
            ],
            documents_or_details_needed=[],
            sources=[],
        )

    user_prompt = build_rag_prompt(
        user_question=request.message,
        sources=sources,
    )

    try:
        llm_answer = llm_service.generate_json_answer(user_prompt)
    except LLMServiceError as exc:
        return ChatResponse(
            category=issue_result.category,
            urgency=urgency_result.urgency,
            simple_answer=(
                "Relevant official sources were found, but the answer generation "
                "service failed. Error: " + str(exc)
            ),
            next_steps=[
                "Check whether GROQ_API_KEY is correctly set.",
                "Check whether the selected Groq model is available.",
                "Try again after verifying the API configuration.",
            ],
            documents_or_details_needed=[],
            sources=sources,
        )

    guarded_answer, guardrail_warnings = apply_answer_guardrails(
        user_message=request.message,
        llm_answer=llm_answer,
        sources=sources,
    )

    final_category = issue_result.category
    if final_category == "Unknown":
        final_category = guarded_answer.get("category", "Unknown")

    final_urgency = urgency_result.urgency
    if final_urgency == "Unknown":
        final_urgency = guarded_answer.get("urgency", "Unknown")

    return ChatResponse(
        category=final_category,
        urgency=final_urgency,
        simple_answer=guarded_answer.get(
            "simple_answer",
            "I could not generate a grounded answer from the available sources.",
        ),
        next_steps=guarded_answer.get("next_steps", []),
        documents_or_details_needed=guarded_answer.get(
            "documents_or_details_needed",
            [],
        ),
        sources=sources,
    )