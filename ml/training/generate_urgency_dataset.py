import random
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "urgency_classification_large.csv"

random.seed(42)


DATA = {
    "High": [
        "My husband is threatening me tonight.",
        "Pati mujhe maar raha hai abhi.",
        "I am locked inside my house and cannot leave.",
        "Someone is following me and I feel unsafe.",
        "My child is missing and phone is off.",
        "My wife is missing since morning.",
        "There is domestic violence at home.",
        "I am being beaten at home.",
        "Someone is threatening to kill me.",
        "I need police help immediately.",
        "Medical emergency hai ambulance nahi aa rahi.",
        "Patient is bleeding and hospital refused treatment.",
        "My boyfriend is threatening to leak my private photos.",
        "In-laws locked me inside and took my phone.",
        "Someone is stalking me daily.",
        "Emergency patient ko admission nahi diya.",
        "Loan app is threatening my family and contacts.",
        "Neighbour attacked me and ran away.",
        "I am scared to stay at home tonight.",
        "My daughter has not returned from tuition.",
    ],

    "Medium": [
        "My employer has not paid salary for three months.",
        "Company is holding my internship stipend.",
        "My final settlement is pending.",
        "Seller is not giving refund.",
        "Warranty claim was rejected.",
        "Ration card benefit stopped.",
        "Pension application is pending.",
        "Passport verification is pending for months.",
        "Government office is delaying my certificate.",
        "Landlord is not returning security deposit.",
        "Builder delayed possession for two years.",
        "Police are not taking my complaint.",
        "Department closed my grievance without solving issue.",
        "Hospital denied treatment yesterday.",
        "Broadband company took payment but connection not installed.",
        "Ration dealer refused grains because fingerprint failed.",
        "Salary deducted without explanation.",
        "Online fraud happened and money is gone.",
        "Property registry is stuck.",
        "Officer is not taking action on my complaint.",
    ],

    "Low": [
        "How can I apply for legal aid?",
        "What documents are needed for consumer complaint?",
        "Where can I check my court case status?",
        "How to file a municipal complaint?",
        "What is the process for CPGRAMS grievance?",
        "How can I get FIR copy online?",
        "Can I get free lawyer from DLSA?",
        "Where to complain about streetlight issue?",
        "How to check pension application status?",
        "What documents are needed for salary complaint?",
        "How to contact labour department?",
        "Where can I file complaint against seller?",
        "How to apply for ration card correction?",
        "How to check passport application status?",
        "What is NALSA?",
        "Can legal services authority help poor people?",
        "How to file public grievance online?",
        "What details should I keep for municipal complaint?",
        "How to complain about defective product?",
        "Where to go for property dispute help?",
    ],

    "Unknown": [
        "Tell me a joke.",
        "Write a birthday message.",
        "Explain transformer architecture.",
        "Help me solve two sum.",
        "Make a gym plan.",
        "What should I eat after workout?",
        "Suggest a laptop.",
        "Plan a trip to Rameshwaram.",
        "How to learn Python?",
        "Explain op amp virtual ground.",
        "Best places to visit in Chennai.",
        "How much protein in paneer?",
        "Make notes for exam.",
        "Write a LinkedIn post.",
        "What is machine learning?",
        "How to deploy Streamlit app?",
        "Give me DSA roadmap.",
        "Best camera settings?",
        "Who won the cricket match?",
        "Teach me binary search.",
    ],
}


PREFIXES = [
    "",
    "Sir ",
    "Please help, ",
    "Madam ",
    "Bhai ",
    "Urgent, ",
    "I need help, ",
]

SUFFIXES = [
    "",
    " what should I do?",
    " please guide.",
    " help me.",
    " kya karu?",
    " where should I go?",
]


def add_noise(text: str) -> str:
    if random.random() < 0.50:
        text = random.choice(PREFIXES) + text

    if random.random() < 0.50:
        text = text + random.choice(SUFFIXES)

    if random.random() < 0.20:
        text = text.lower()

    return " ".join(text.split())


def main():
    rows = []

    examples_per_template = 12

    for urgency, templates in DATA.items():
        for template in templates:
            for _ in range(examples_per_template):
                rows.append(
                    {
                        "text": add_noise(template),
                        "urgency": urgency,
                    }
                )

    random.shuffle(rows)

    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Saved:", OUTPUT_PATH)
    print("Rows:", len(df))
    print(df["urgency"].value_counts())


if __name__ == "__main__":
    main()