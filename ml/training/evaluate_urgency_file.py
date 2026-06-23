import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import classification_report, confusion_matrix
from transformers import AutoModelForSequenceClassification, AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "urgency_classifier_xlmr"
LABEL_PATH = PROJECT_ROOT / "ml" / "datasets" / "urgency_labels.json"


def load_labels():
    with LABEL_PATH.open("r", encoding="utf-8") as f:
        label2id = json.load(f)

    id2label = {int(v): k for k, v in label2id.items()}
    return label2id, id2label


def predict_one(text, tokenizer, model):
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

    pred_id = int(torch.argmax(probs).item())
    confidence = float(probs[pred_id].item())

    return pred_id, confidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    args = parser.parse_args()

    csv_path = Path(args.csv)

    label2id, id2label = load_labels()

    df = pd.read_csv(csv_path)
    df["true_id"] = df["urgency"].map(label2id)

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_PATH))
    model.eval()

    pred_ids = []
    confidences = []

    for text in df["text"].tolist():
        pred_id, confidence = predict_one(text, tokenizer, model)
        pred_ids.append(pred_id)
        confidences.append(confidence)

    df["pred_id"] = pred_ids
    df["confidence"] = confidences
    df["prediction"] = df["pred_id"].map(id2label)

    labels = list(range(len(label2id)))
    label_names = [id2label[i] for i in labels]

    print("\nClassification report:")
    print(
        classification_report(
            df["true_id"],
            df["pred_id"],
            labels=labels,
            target_names=label_names,
            zero_division=0,
        )
    )

    print("\nConfusion matrix:")
    cm = confusion_matrix(df["true_id"], df["pred_id"], labels=labels)
    print(pd.DataFrame(cm, index=label_names, columns=label_names))

    errors = df[df["true_id"] != df["pred_id"]]

    print("\nErrors:")
    if errors.empty:
        print("No errors.")
    else:
        print(errors[["text", "urgency", "prediction", "confidence"]].to_string(index=False))


if __name__ == "__main__":
    main()