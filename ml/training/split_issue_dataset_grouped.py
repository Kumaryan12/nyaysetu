from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large.csv"
TRAIN_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_train.csv"
VAL_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_val.csv"
TEST_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_test.csv"


def main():
    df = pd.read_csv(INPUT_PATH)

    if "group" not in df.columns:
        raise ValueError("Dataset must contain a group column.")

    train_parts = []
    val_parts = []
    test_parts = []

    for category, cat_df in df.groupby("category"):
        groups = sorted(cat_df["group"].unique())

        if len(groups) >= 3:
            train_groups, temp_groups = train_test_split(
                groups,
                test_size=0.4,
                random_state=42,
            )

            val_groups, test_groups = train_test_split(
                temp_groups,
                test_size=0.5,
                random_state=42,
            )

            train_parts.append(cat_df[cat_df["group"].isin(train_groups)])
            val_parts.append(cat_df[cat_df["group"].isin(val_groups)])
            test_parts.append(cat_df[cat_df["group"].isin(test_groups)])
        else:
            train_df, temp_df = train_test_split(
                cat_df,
                test_size=0.3,
                random_state=42,
                stratify=cat_df["category"],
            )

            val_df, test_df = train_test_split(
                temp_df,
                test_size=0.5,
                random_state=42,
                stratify=temp_df["category"],
            )

            train_parts.append(train_df)
            val_parts.append(val_df)
            test_parts.append(test_df)

    train_df = pd.concat(train_parts).sample(frac=1, random_state=42)
    val_df = pd.concat(val_parts).sample(frac=1, random_state=42)
    test_df = pd.concat(test_parts).sample(frac=1, random_state=42)

    # Keep group in files for debugging.
    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    print("Train:", train_df.shape, TRAIN_PATH)
    print("Val:", val_df.shape, VAL_PATH)
    print("Test:", test_df.shape, TEST_PATH)

    print("\nTrain distribution:")
    print(train_df["category"].value_counts())

    print("\nVal distribution:")
    print(val_df["category"].value_counts())

    print("\nTest distribution:")
    print(test_df["category"].value_counts())


if __name__ == "__main__":
    main()