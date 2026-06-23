from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "urgency_classification_large.csv"
TRAIN_PATH = PROJECT_ROOT / "ml" / "datasets" / "urgency_train.csv"
VAL_PATH = PROJECT_ROOT / "ml" / "datasets" / "urgency_val.csv"


def main():
    df = pd.read_csv(INPUT_PATH)

    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["urgency"],
    )

    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)

    print("Train:", train_df.shape)
    print("Val:", val_df.shape)
    print("\nValidation distribution:")
    print(val_df["urgency"].value_counts())


if __name__ == "__main__":
    main()