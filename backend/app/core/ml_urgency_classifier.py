from pathlib import Path
from typing import List, Optional

import torch
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import settings


class MLUrgencyResult(BaseModel):
    urgency: str
    confidence: float
    top_urgencies: List[str]
    top_scores: List[float]
    model_available: bool = True


class FineTunedUrgencyClassifier:
    """
    Loads and runs the fine-tuned XLM-R urgency classifier.

    In production, set URGENCY_CLASSIFIER_MODEL_ID to a Hugging Face model ID.
    Locally, it falls back to nyayasetu/ml/saved_models/urgency_classifier_xlmr.
    """

    def __init__(self):
        backend_dir = Path(__file__).resolve().parents[2]
        project_root = backend_dir.parent

        self.model_path = (
            project_root
            / "ml"
            / "saved_models"
            / "urgency_classifier_xlmr"
        )

        self.model_source = settings.urgency_classifier_model_id

        if self.model_source is None and self.model_path.exists():
            self.model_source = str(self.model_path)

        if self.model_source is None:
            raise FileNotFoundError(
                "Fine-tuned urgency classifier not found locally at "
                + str(self.model_path)
                + ". Set URGENCY_CLASSIFIER_MODEL_ID to load it from Hugging Face."
            )

        token_kwargs = {}
        if settings.hf_token:
            token_kwargs["token"] = settings.hf_token

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_source,
            **token_kwargs,
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_source,
            **token_kwargs,
        )

        self.model.eval()

    def classify(self, text: str) -> MLUrgencyResult:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=192,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]

        top_k = min(3, probs.shape[0])
        top = torch.topk(probs, k=top_k)

        top_indices = top.indices.tolist()
        top_scores = top.values.tolist()

        id2label = self.model.config.id2label

        top_urgencies = [
            id2label[int(index)]
            for index in top_indices
        ]

        return MLUrgencyResult(
            urgency=top_urgencies[0],
            confidence=float(top_scores[0]),
            top_urgencies=top_urgencies,
            top_scores=[float(score) for score in top_scores],
            model_available=True,
        )


class SafeUrgencyClassifier:
    """
    Safe wrapper around the fine-tuned urgency classifier.

    If the saved model is missing, backend will not crash.
    It will fall back to the rule-based urgency detector.
    """

    def __init__(self):
        self.classifier: Optional[FineTunedUrgencyClassifier] = None
        self.error: Optional[str] = None

        try:
            self.classifier = FineTunedUrgencyClassifier()
        except Exception as exc:
            self.error = str(exc)

    def is_available(self) -> bool:
        return self.classifier is not None

    def classify(self, text: str) -> Optional[MLUrgencyResult]:
        if self.classifier is None:
            return None

        return self.classifier.classify(text)
