import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, classification_report
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAIN_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_train.csv"
VAL_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_val.csv"
LABEL_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_labels.json"
OUTPUT_DIR = PROJECT_ROOT / "ml" / "saved_models" / "issue_classifier_xlmr"

MODEL_NAME = "xlm-roberta-base"
MAX_LENGTH = 192


def load_label_maps():
    with LABEL_PATH.open("r", encoding="utf-8") as f:
        label2id = json.load(f)

    id2label = {int(v): k for k, v in label2id.items()}
    return label2id, id2label


def load_dataset(csv_path, label2id):
    df = pd.read_csv(csv_path)

    if "text" not in df.columns or "category" not in df.columns:
        raise ValueError("CSV must contain text and category columns.")

    df = df.dropna(subset=["text", "category"]).copy()
    df["label"] = df["category"].map(label2id)

    if df["label"].isna().any():
        unknown_labels = df[df["label"].isna()]["category"].unique()
        raise ValueError(f"Unknown labels found: {unknown_labels}")

    df["label"] = df["label"].astype(int)

    return Dataset.from_pandas(df[["text", "label"]])


def main():
    print("Loading labels...")
    label2id, id2label = load_label_maps()
    num_labels = len(label2id)

    print("Labels:", label2id)

    print("Loading dataset...")
    train_dataset = load_dataset(TRAIN_PATH, label2id)
    val_dataset = load_dataset(VAL_PATH, label2id)

    print("Train rows:", len(train_dataset))
    print("Val rows:", len(val_dataset))

    print("Loading tokenizer and model:", MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
    )

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
        )

    train_dataset = train_dataset.map(tokenize, batched=True)
    val_dataset = val_dataset.map(tokenize, batched=True)

    train_dataset = train_dataset.remove_columns(["text"])
    val_dataset = val_dataset.remove_columns(["text"])

    train_dataset.set_format("torch")
    val_dataset.set_format("torch")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)

        return {
            "accuracy": accuracy_score(labels, preds),
            "macro_f1": f1_score(labels, preds, average="macro"),
            "weighted_f1": f1_score(labels, preds, average="weighted"),
        }

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=4,
        weight_decay=0.01,
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        save_total_limit=2,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    print("Training...")
    trainer.train()

    print("Evaluating...")
    metrics = trainer.evaluate()
    print(metrics)

    print("Saving model...")
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))

    predictions = trainer.predict(val_dataset)
    preds = np.argmax(predictions.predictions, axis=-1)
    labels = predictions.label_ids

    label_names = [id2label[i] for i in range(num_labels)]

    print("\nClassification report:")
    print(
        classification_report(
            labels,
            preds,
            target_names=label_names,
            zero_division=0,
        )
    )

    report_path = OUTPUT_DIR / "classification_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as f:
        f.write(str(metrics))
        f.write("\n\n")
        f.write(
            classification_report(
                labels,
                preds,
                target_names=label_names,
                zero_division=0,
            )
        )

    print("Saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()