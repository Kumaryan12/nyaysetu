from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large_augmented_round2.csv"
TRAIN_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_train.csv"
VAL_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_val.csv"


def main():
    df = pd.read_csv(INPUT_PATH)

    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["category"],
    )

    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)

    print("Train:", TRAIN_PATH, train_df.shape)
    print("Val:", VAL_PATH, val_df.shape)

    print("\nValidation distribution:")
    print(val_df["category"].value_counts())


if __name__ == "__main__":
    main()