import json
from typing import Any, Dict

import requests

from app.config import settings
from app.core.prompt_templates import SYSTEM_PROMPT_LEGAL_RAG


class LLMServiceError(Exception):
    """
    Custom error for LLM generation failures.
    """

    pass


class GroqLLMService:
    """
    Groq-backed LLM service.

    Responsibility:
    - Send retrieved RAG context to Groq
    - Ask for structured JSON
    - Parse and return the result

    Important:
    Groq is used only for explanation/generation.
    Legal truth must come from retrieved official sources.
    """

    def __init__(self):
        self.api_key = settings.groq_api_key
        self.api_url = settings.groq_api_url
        self.model = settings.groq_model

    def _ensure_api_key(self) -> None:
        if not self.api_key:
            raise LLMServiceError(
                "GROQ_API_KEY is missing. Add it to your .env file."
            )

    def generate_json_answer(self, user_prompt: str) -> Dict[str, Any]:
        """
        Calls Groq Chat Completions API and expects a JSON object response.
        """

        self._ensure_api_key()

        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_LEGAL_RAG,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.2,
            "max_tokens": 1200,
            "response_format": {
                "type": "json_object"
            },
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
        except requests.RequestException as exc:
            raise LLMServiceError(
                "Failed to connect to Groq API: " + str(exc)
            )

        if response.status_code != 200:
            raise LLMServiceError(
                "Groq API error "
                + str(response.status_code)
                + ": "
                + response.text
            )

        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise LLMServiceError(
                "Unexpected Groq response format: " + json.dumps(data)[:1000]
            )

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            raise LLMServiceError(
                "Groq did not return valid JSON. Raw content: " + content
            )

        return parsed