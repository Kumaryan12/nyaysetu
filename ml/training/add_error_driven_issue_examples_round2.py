from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_CANDIDATES = [
    PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large_augmented.csv",
    PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large.csv",
]

OUTPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large_augmented_round2.csv"


ROUND2_ROWS = [
    # Labour Dispute — stipend, gig work, delivery work, informal work
    ("my internship certificate is given but stipend still pending", "Labour Dispute", "round2_labour_stipend"),
    ("college made us work for event but promised stipend is not coming", "Labour Dispute", "round2_labour_stipend"),
    ("internship completed but company has not paid stipend", "Labour Dispute", "round2_labour_stipend"),
    ("stipend pending hai internship khatam hone ke baad bhi", "Labour Dispute", "round2_labour_stipend"),
    ("training period ka stipend company nahi de rahi", "Labour Dispute", "round2_labour_stipend"),

    ("worked as delivery boy but weekly payment not received", "Labour Dispute", "round2_labour_gig_payment"),
    ("delivery company is not paying weekly payout", "Labour Dispute", "round2_labour_gig_payment"),
    ("gig work ka payment app company nahi de rahi", "Labour Dispute", "round2_labour_gig_payment"),
    ("worked for delivery platform but payout is pending", "Labour Dispute", "round2_labour_gig_payment"),
    ("daily delivery payment not credited by company", "Labour Dispute", "round2_labour_gig_payment"),

    # Police Complaint — missing person
    ("my daughter has not returned from tuition and phone is off", "Police Complaint", "round2_police_missing_person"),
    ("my child did not come back from school", "Police Complaint", "round2_police_missing_person"),
    ("my wife left home and phone is switched off", "Police Complaint", "round2_police_missing_person"),
    ("family member missing hai aur phone band hai", "Police Complaint", "round2_police_missing_person"),
    ("missing person report file karni hai", "Police Complaint", "round2_police_missing_person"),

    # Police Complaint — loan app threats, blackmail, forgery, property damage
    ("online loan app is threatening my contacts", "Police Complaint", "round2_police_loan_app_threat"),
    ("loan app wale mere contacts ko dhamki de rahe hain", "Police Complaint", "round2_police_loan_app_threat"),
    ("loan recovery agent is threatening my family", "Police Complaint", "round2_police_loan_app_threat"),
    ("someone is threatening to call all my contacts", "Police Complaint", "round2_police_loan_app_threat"),
    ("loan app blackmail kar raha hai", "Police Complaint", "round2_police_loan_app_threat"),

    ("neighbour broke our gate and ran away", "Police Complaint", "round2_police_damage"),
    ("someone damaged my vehicle and escaped", "Police Complaint", "round2_police_damage"),
    ("neighbour broke my door during fight", "Police Complaint", "round2_police_damage"),
    ("someone forged my signature on document", "Police Complaint", "round2_police_forgery"),
    ("fake signature se document bana diya", "Police Complaint", "round2_police_forgery"),

    # Domestic Violence / Safety — coercive control by in-laws/family/partner
    ("in laws are not allowing me to contact my parents", "Domestic Violence / Safety", "round2_dv_coercive_control"),
    ("sasural wale mujhe parents se baat nahi karne dete", "Domestic Violence / Safety", "round2_dv_coercive_control"),
    ("husband locks my phone and stops me from calling family", "Domestic Violence / Safety", "round2_dv_coercive_control"),
    ("my partner controls who I can talk to and threatens me", "Domestic Violence / Safety", "round2_dv_coercive_control"),
    ("ghar wale mujhe bahar nahi jaane dete aur dhamki dete hain", "Domestic Violence / Safety", "round2_dv_coercive_control"),

    # Property Issue — builder layout, booking amount, possession
    ("builder changed layout after taking booking amount", "Property Issue", "round2_property_builder_booking"),
    ("builder changed flat plan after taking money", "Property Issue", "round2_property_builder_booking"),
    ("builder took booking amount but changed project layout", "Property Issue", "round2_property_builder_booking"),
    ("builder asking extra money before possession", "Property Issue", "round2_property_builder_booking"),
    ("flat layout changed after agreement", "Property Issue", "round2_property_builder_booking"),

    # Public Grievance — passport / verification / office delay
    ("my passport police verification is pending for months", "Public Grievance", "round2_public_passport_delay"),
    ("passport verification stuck at police station", "Public Grievance", "round2_public_passport_delay"),
    ("passport file pending with department for long time", "Public Grievance", "round2_public_passport_delay"),
    ("passport application stuck and no update from office", "Public Grievance", "round2_public_passport_delay"),
    ("police verification for passport not completed yet", "Public Grievance", "round2_public_passport_delay"),

    ("my certificate file is moving between two offices", "Public Grievance", "round2_public_office_delay"),
    ("tehsil office keeps sending me to another office", "Public Grievance", "round2_public_office_delay"),
    ("file is moving from one department to another", "Public Grievance", "round2_public_office_delay"),
    ("government office lost my application documents", "Public Grievance", "round2_public_office_delay"),
    ("public office is delaying my certificate without reason", "Public Grievance", "round2_public_office_delay"),

    # Government Scheme — distinguish from public grievance
    ("ration benefit stopped after biometric problem", "Government Scheme", "round2_scheme_benefit_specific"),
    ("widow pension approved but money not credited", "Government Scheme", "round2_scheme_benefit_specific"),
    ("scholarship failed due to bank account linking issue", "Government Scheme", "round2_scheme_benefit_specific"),
    ("PMAY subsidy not released", "Government Scheme", "round2_scheme_benefit_specific"),
    ("anganwadi benefit not given to my child", "Government Scheme", "round2_scheme_benefit_specific"),

    # Unknown — strengthen non-legal rejection
    ("help me make a badminton training plan", "Unknown", "round2_unknown_sports"),
    ("explain transformer architecture", "Unknown", "round2_unknown_tech"),
    ("make notes for analog electronics exam", "Unknown", "round2_unknown_study"),
    ("which mutual fund should I invest in", "Unknown", "round2_unknown_finance"),
    ("write a caption for instagram", "Unknown", "round2_unknown_writing"),
    ("how to install react app", "Unknown", "round2_unknown_tech"),
    ("what should I eat after workout", "Unknown", "round2_unknown_fitness"),
    ("plan a trip to rameshwaram", "Unknown", "round2_unknown_travel"),
    ("teach me linked list reversal", "Unknown", "round2_unknown_study"),
    ("suggest youtube channels for machine learning", "Unknown", "round2_unknown_study"),
]


def find_input_path():
    for path in INPUT_CANDIDATES:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Could not find base dataset. Expected one of:\n"
        + "\n".join(str(path) for path in INPUT_CANDIDATES)
    )


def main():
    input_path = find_input_path()
    base_df = pd.read_csv(input_path)

    round2_df = pd.DataFrame(
        ROUND2_ROWS,
        columns=["text", "category", "group"],
    )

    combined_df = pd.concat([base_df, round2_df], ignore_index=True)
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

    combined_df.to_csv(OUTPUT_PATH, index=False)

    print("Input:", input_path)
    print("Base rows:", len(base_df))
    print("Round 2 rows:", len(round2_df))
    print("Combined rows:", len(combined_df))
    print("Saved:", OUTPUT_PATH)
    print("\nCategory distribution:")
    print(combined_df["category"].value_counts())


if __name__ == "__main__":
    main()