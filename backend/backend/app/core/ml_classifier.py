from pathlib import Path
from typing import List

import torch
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class MLClassificationResult(BaseModel):
    category: str
    confidence: float
    top_categories: List[str]
    top_scores: List[float]


class FineTunedIssueClassifier:
    """
    Loads the fine-tuned XLM-R issue classifier.

    This should be initialized once when the backend starts.
    """

    def __init__(self):
        backend_root = Path(__file__).resolve().parents[2]
        project_root = backend_root.parent

        self.model_path = (
            project_root
            / "ml"
            / "saved_models"
            / "issue_classifier_xlmr"
        )

        if not self.model_path.exists():
            raise FileNotFoundError(
                "Fine-tuned issue classifier not found at: "
                + str(self.model_path)
                + ". Train it first using ml/training/train_issue_classifier.py"
            )

        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(
            str(self.model_path)
        )
        self.model.eval()

    def classify(self, text: str) -> MLClassificationResult:
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

        top = torch.topk(probs, k=min(3, probs.shape[0]))

        top_indices = top.indices.tolist()
        top_scores = top.values.tolist()

        id2label = self.model.config.id2label

        top_categories = [
            id2label[int(index)]
            for index in top_indices
        ]

        return MLClassificationResult(
            category=top_categories[0],
            confidence=float(top_scores[0]),
            top_categories=top_categories,
            top_scores=[float(score) for score in top_scores],
        )