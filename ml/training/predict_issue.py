import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "issue_classifier_xlmr"
LABEL_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_labels.json"


def load_labels():
    with LABEL_PATH.open("r", encoding="utf-8") as f:
        label2id = json.load(f)

    id2label = {int(v): k for k, v in label2id.items()}
    return id2label


def main():
    id2label = load_labels()

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_PATH))
    model.eval()

    print("NyayaSetu issue classifier")
    print("Type a query. Press Ctrl+C to exit.")

    while True:
        text = input("\nQuery: ").strip()

        if not text:
            continue

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=192,
        )

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]

        top = torch.topk(probs, k=3)

        print("\nTop predictions:")
        for idx, score in zip(top.indices.tolist(), top.values.tolist()):
            print(f"{id2label[int(idx)]}: {float(score):.4f}")


if __name__ == "__main__":
    main()