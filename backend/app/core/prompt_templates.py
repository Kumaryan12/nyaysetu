import json
from typing import List

from app.models.schemas import SourceSnippet


SYSTEM_PROMPT_LEGAL_RAG = """
You are NyayaSetu, a legal-aid and public-service grievance information assistant.

You are NOT a lawyer.
You must NOT provide personal legal advice.
You must explain official information in simple language.

You must answer ONLY using the retrieved source passages provided by the system.

Critical rules:
1. Do not invent laws, sections, deadlines, phone numbers, procedures, rights, schemes, or authorities.
2. Do not answer from your own memory.
3. Do not claim the user will win a case.
4. Do not provide aggressive legal strategy.
5. If the sources are insufficient, clearly say that enough information was not found in the available official sources.
6. For urgent safety issues, advise the user to contact appropriate emergency/local authorities or legal aid immediately.
7. Keep the answer simple enough for a non-lawyer to understand.

Return ONLY valid JSON.
Do not wrap the JSON in markdown.
"""


def build_context_from_sources(sources: List[SourceSnippet]) -> str:
    """
    Converts retrieved source snippets into a numbered context block.

    The source numbers are important because the LLM can refer to them
    in the final answer.
    """

    context_blocks = []

    for index, source in enumerate(sources, start=1):
        block = {
            "source_number": index,
            "title": source.title,
            "source_type": source.source_type,
            "url": source.url or "",
            "text": source.text,
        }

        context_blocks.append(block)

    return json.dumps(context_blocks, ensure_ascii=False, indent=2)


def build_rag_prompt(user_question: str, sources: List[SourceSnippet]) -> str:
    """
    Builds the final user prompt sent to Groq.

    The model receives:
    - the user's question
    - retrieved source passages
    - strict JSON output format
    """

    context = build_context_from_sources(sources)

    return f"""
User question:
{user_question}

Retrieved official source passages:
{context}

Return a JSON object with exactly these keys:

{{
  "category": "One short category such as Labour Dispute, Consumer Complaint, Legal Aid, Police Complaint, Municipal Issue, Healthcare Access, Government Scheme, Property Issue, or Unknown",
  "urgency": "Low, Medium, High, or Unknown",
  "simple_answer": "A simple explanation based only on the retrieved sources.",
  "next_steps": [
    "Practical next step 1",
    "Practical next step 2"
  ],
  "documents_or_details_needed": [
    "Document or detail 1",
    "Document or detail 2"
  ],
  "source_numbers_used": [1, 2],
  "insufficient_sources": false
}}

If the retrieved sources do not contain enough information, set:
"insufficient_sources": true

and make "simple_answer":
"I could not find enough information in the available official sources."
"""