from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large.csv"
OUTPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large_augmented.csv"


TARGETED_ROWS = [
    # Labour Dispute — internship / stipend / trainee payment
    ("company is holding my internship stipend", "Labour Dispute", "targeted_labour_stipend"),
    ("my internship stipend has not been paid", "Labour Dispute", "targeted_labour_stipend"),
    ("internship company is not giving stipend", "Labour Dispute", "targeted_labour_stipend"),
    ("I worked as intern but stipend is pending", "Labour Dispute", "targeted_labour_stipend"),
    ("intern stipend nahi mila ab kya karu", "Labour Dispute", "targeted_labour_stipend"),
    ("company made me work but says intern stipend will not be paid", "Labour Dispute", "targeted_labour_stipend"),
    ("trainee payment is pending from company", "Labour Dispute", "targeted_labour_stipend"),
    ("apprenticeship stipend not received", "Labour Dispute", "targeted_labour_stipend"),
    ("stipend rok diya hai company ne", "Labour Dispute", "targeted_labour_stipend"),
    ("I completed internship but company is not paying stipend", "Labour Dispute", "targeted_labour_stipend"),

    # Police Complaint — extortion / documents held / blackmail
    ("they took my documents and now asking money to return them", "Police Complaint", "targeted_police_extortion"),
    ("someone is demanding money to return my documents", "Police Complaint", "targeted_police_extortion"),
    ("my certificates are being held and they are asking money", "Police Complaint", "targeted_police_extortion"),
    ("documents le liye aur paise maang rahe hain", "Police Complaint", "targeted_police_extortion"),
    ("someone is threatening me for money", "Police Complaint", "targeted_police_extortion"),
    ("person is extorting money from me", "Police Complaint", "targeted_police_extortion"),
    ("blackmail karke paise maang raha hai", "Police Complaint", "targeted_police_extortion"),
    ("they are not returning my ID card and demanding cash", "Police Complaint", "targeted_police_extortion"),
    ("my documents were taken forcefully", "Police Complaint", "targeted_police_extortion"),
    ("someone is holding my papers and asking for money", "Police Complaint", "targeted_police_extortion"),

    # Police Complaint — missing person
    ("my wife is missing and phone is switched off", "Police Complaint", "targeted_police_missing_person"),
    ("my husband is missing since morning", "Police Complaint", "targeted_police_missing_person"),
    ("my child is missing from school", "Police Complaint", "targeted_police_missing_person"),
    ("family member missing hai police complaint karni hai", "Police Complaint", "targeted_police_missing_person"),
    ("my sister has not returned home and phone is off", "Police Complaint", "targeted_police_missing_person"),
    ("my father is missing since yesterday", "Police Complaint", "targeted_police_missing_person"),
    ("missing person complaint kaise kare", "Police Complaint", "targeted_police_missing_person"),
    ("wife ghar nahi aayi phone band hai", "Police Complaint", "targeted_police_missing_person"),
    ("brother missing hai kya karu", "Police Complaint", "targeted_police_missing_person"),
    ("my friend is missing and not reachable", "Police Complaint", "targeted_police_missing_person"),

    # Government Scheme — ration / PDS / biometric
    ("ration shop says fingerprint not matching so no ration", "Government Scheme", "targeted_scheme_ration_pds"),
    ("ration dealer refused to give ration because biometric failed", "Government Scheme", "targeted_scheme_ration_pds"),
    ("fingerprint not matching in ration shop", "Government Scheme", "targeted_scheme_ration_pds"),
    ("ration card active hai but ration nahi mil raha", "Government Scheme", "targeted_scheme_ration_pds"),
    ("PDS shop is not giving ration", "Government Scheme", "targeted_scheme_ration_pds"),
    ("biometric fail ho raha ration lene me", "Government Scheme", "targeted_scheme_ration_pds"),
    ("ration dealer says name not in list", "Government Scheme", "targeted_scheme_ration_pds"),
    ("public distribution ration issue", "Government Scheme", "targeted_scheme_ration_pds"),
    ("ration shop machine fingerprint accept nahi kar rahi", "Government Scheme", "targeted_scheme_ration_pds"),
    ("my family is not getting ration benefit", "Government Scheme", "targeted_scheme_ration_pds"),

    # Healthcare Access — ambulance / emergency / rural access
    ("ambulance refused to come to village", "Healthcare Access", "targeted_health_ambulance"),
    ("ambulance nahi aa rahi village me", "Healthcare Access", "targeted_health_ambulance"),
    ("emergency ambulance did not come", "Healthcare Access", "targeted_health_ambulance"),
    ("called ambulance but nobody came", "Healthcare Access", "targeted_health_ambulance"),
    ("ambulance service refused rural area", "Healthcare Access", "targeted_health_ambulance"),
    ("patient ko ambulance nahi mila", "Healthcare Access", "targeted_health_ambulance"),
    ("medical emergency hai ambulance chahiye", "Healthcare Access", "targeted_health_ambulance"),
    ("government ambulance number not responding", "Healthcare Access", "targeted_health_ambulance"),
    ("ambulance driver refused to take patient", "Healthcare Access", "targeted_health_ambulance"),
    ("village me emergency ambulance nahi mil rahi", "Healthcare Access", "targeted_health_ambulance"),

    # Unknown — broader non-legal queries
    ("need help writing resume", "Unknown", "targeted_unknown_career"),
    ("make a timetable for DSA", "Unknown", "targeted_unknown_education"),
    ("create study plan for exams", "Unknown", "targeted_unknown_education"),
    ("help me prepare for coding interview", "Unknown", "targeted_unknown_education"),
    ("write a LinkedIn post for my project", "Unknown", "targeted_unknown_writing"),
    ("give me gym workout plan", "Unknown", "targeted_unknown_fitness"),
    ("how to lose weight fast", "Unknown", "targeted_unknown_fitness"),
    ("how much protein in paneer", "Unknown", "targeted_unknown_food"),
    ("best places to visit in Chennai", "Unknown", "targeted_unknown_travel"),
    ("recommend a laptop for machine learning", "Unknown", "targeted_unknown_shopping"),
    ("explain neural networks", "Unknown", "targeted_unknown_education"),
    ("write an email to professor", "Unknown", "targeted_unknown_writing"),
    ("make ppt content for my project", "Unknown", "targeted_unknown_writing"),
    ("what is XLM roberta", "Unknown", "targeted_unknown_tech"),
    ("teach me binary search", "Unknown", "targeted_unknown_education"),
    ("diet plan for fat loss", "Unknown", "targeted_unknown_fitness"),
    ("which phone should I buy", "Unknown", "targeted_unknown_shopping"),
    ("help me debug python code", "Unknown", "targeted_unknown_tech"),
    ("make a birthday message", "Unknown", "targeted_unknown_writing"),
    ("tell me current cricket score", "Unknown", "targeted_unknown_sports"),
]


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Base dataset not found: {DATASET_PATH}. "
            "Run generate_issue_dataset.py first."
        )

    base_df = pd.read_csv(DATASET_PATH)

    targeted_df = pd.DataFrame(
        TARGETED_ROWS,
        columns=["text", "category", "group"],
    )

    combined_df = pd.concat([base_df, targeted_df], ignore_index=True)
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

    combined_df.to_csv(OUTPUT_PATH, index=False)

    print("Base rows:", len(base_df))
    print("Targeted rows:", len(targeted_df))
    print("Combined rows:", len(combined_df))
    print("Saved:", OUTPUT_PATH)
    print("\nCategory distribution:")
    print(combined_df["category"].value_counts())


if __name__ == "__main__":
    main()