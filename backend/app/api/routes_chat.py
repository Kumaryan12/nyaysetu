from fastapi import APIRouter

from app.core.answer_guardrails import apply_answer_guardrails
from app.core.category_correction_rules import apply_category_correction
from app.core.issue_classifier import classify_issue
from app.core.ml_classifier import SafeIssueClassifier
from app.core.ml_urgency_classifier import SafeUrgencyClassifier
from app.core.prompt_templates import build_rag_prompt
from app.core.urgency_correction_rules import apply_urgency_correction
from app.core.urgency_detector import detect_urgency
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import GroqLLMService, LLMServiceError
from app.services.rag_service import RAGService


router = APIRouter(prefix="/chat", tags=["Chat"])

rag_service = RAGService()
llm_service = GroqLLMService()

ml_issue_classifier = SafeIssueClassifier()
ml_urgency_classifier = SafeUrgencyClassifier()


def get_best_issue_category(user_message: str) -> str:
    """
    Chooses the best issue category.

    Priority:
    1. Fine-tuned issue classifier if available and confident
    2. Rule-based issue classifier fallback
    3. Category correction rules for known high-risk/boundary cases
    """

    ml_result = ml_issue_classifier.classify(user_message)

    if ml_result is not None and ml_result.confidence >= 0.55:
        predicted_category = ml_result.category
    else:
        rule_result = classify_issue(user_message)

        if rule_result.confidence >= 0.20:
            predicted_category = rule_result.category
        elif ml_result is not None:
            predicted_category = ml_result.category
        else:
            predicted_category = "Unknown"

    corrected_category, correction_reasons = apply_category_correction(
        user_message=user_message,
        predicted_category=predicted_category,
    )

    return corrected_category


def get_best_urgency(user_message: str) -> str:
    """
    Chooses the best urgency level.

    Priority:
    1. Fine-tuned urgency classifier if available and confident
    2. Rule-based urgency detector fallback
    3. Urgency correction rules for safety-critical cases
    """

    ml_result = ml_urgency_classifier.classify(user_message)

    if ml_result is not None and ml_result.confidence >= 0.55:
        predicted_urgency = ml_result.urgency
    else:
        rule_result = detect_urgency(user_message)

        if rule_result.confidence >= 0.20:
            predicted_urgency = rule_result.urgency
        elif ml_result is not None:
            predicted_urgency = ml_result.urgency
        else:
            predicted_urgency = "Unknown"

    corrected_urgency, correction_reasons = apply_urgency_correction(
        user_message=user_message,
        predicted_urgency=predicted_urgency,
    )

    return corrected_urgency


@router.get("/classifier-status")
def classifier_status():
    """
    Checks whether the fine-tuned classifiers loaded successfully.
    """

    return {
        "ml_issue_classifier_available": ml_issue_classifier.is_available(),
        "ml_issue_classifier_error": ml_issue_classifier.error,
        "ml_urgency_classifier_available": ml_urgency_classifier.is_available(),
        "ml_urgency_classifier_error": ml_urgency_classifier.error,
    }


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.

    Flow:
    1. Classify issue using fine-tuned ML classifier if available
    2. Fall back to rule-based issue classifier if needed
    3. Apply category correction rules
    4. Classify urgency using fine-tuned ML classifier if available
    5. Fall back to rule-based urgency detector if needed
    6. Apply urgency correction rules
    7. Retrieve relevant official source chunks
    8. Send retrieved chunks to Groq
    9. Apply answer guardrails
    10. Return structured response
    """

    issue_category = get_best_issue_category(request.message)
    urgency_value = get_best_urgency(request.message)

    sources = rag_service.retrieve_sources(
        query=request.message,
        top_k=5,
    )

    if not sources:
        return ChatResponse(
            category=issue_category,
            urgency=urgency_value,
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
            category=issue_category,
            urgency=urgency_value,
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

    final_urgency = urgency_value

    if final_urgency == "Unknown":
        final_urgency = guarded_answer.get("urgency", "Unknown")

    return ChatResponse(
        category=issue_category,
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