import random
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_generated.csv"


DATA = {
    "Labour Dispute": [
        "My employer has not paid my salary for {time}.",
        "Company salary nahi de rahi hai for {time}.",
        "Boss ne payment rok diya hai.",
        "मुझे {time} से वेतन नहीं मिला है।",
        "Factory owner is not giving wages.",
        "I worked but did not receive payment.",
        "Overtime ka paisa nahi mila.",
        "My company fired me without paying dues.",
        "PF amount company ne nahi diya.",
        "Employer is delaying my salary again.",
    ],

    "Consumer Complaint": [
        "I bought {item} online and seller is not giving refund.",
        "Product defective hai aur replacement nahi mil raha.",
        "मेरा सामान खराब आया है और कंपनी बदल नहीं रही।",
        "Warranty claim rejected without proper reason.",
        "Order cancel hua but refund nahi aaya.",
        "Delivery not received but money got deducted.",
        "Shopkeeper is refusing to replace defective product.",
        "Fake product mila online order mein.",
        "Service center is not repairing my {item}.",
        "Seller sent wrong product and is ignoring me.",
    ],

    "Legal Aid": [
        "I cannot afford a lawyer.",
        "Mujhe free lawyer chahiye.",
        "मुझे मुफ्त कानूनी सहायता चाहिए।",
        "Where can I get free legal aid?",
        "I need advocate help but have no money.",
        "DLSA se help kaise milegi?",
        "NALSA legal aid ke liye apply kaise kare?",
        "I need court help but cannot pay lawyer fees.",
        "Can poor people get free legal support?",
        "Legal services authority contact kaise kare?",
    ],

    "Police Complaint": [
        "I want to file a police complaint.",
        "Mera phone chori ho gaya hai.",
        "मेरा मोबाइल चोरी हो गया है।",
        "How can I get FIR copy?",
        "Someone is blackmailing me online.",
        "Fraud hua hai police complaint karni hai.",
        "My bike was stolen yesterday.",
        "Police station complaint kaise kare?",
        "I want to report cyber crime.",
        "Someone threatened me and I want police help.",
    ],

    "Domestic Violence / Safety": [
        "My husband is threatening me and I am scared.",
        "Pati mujhe maar raha hai.",
        "मेरे पति मुझे धमकी दे रहे हैं।",
        "I am facing domestic violence at home.",
        "My in-laws are abusing me for dowry.",
        "I feel unsafe at home.",
        "Someone is stalking me daily.",
        "Partner ne mujhe beat kiya hai.",
        "I am afraid to go back home.",
        "There is violence in my house and I need help.",
    ],

    "Municipal Issue": [
        "There is garbage near my house.",
        "Drainage problem in my street.",
        "गली में कचरा पड़ा है।",
        "Streetlight is not working.",
        "Road has big potholes.",
        "Nala block hai complaint karni hai.",
        "Water supply is dirty in my area.",
        "Mosquito problem due to sewage.",
        "Public toilet is very dirty.",
        "Municipal complaint kaha kare?",
    ],

    "Healthcare Access": [
        "Hospital denied treatment.",
        "Ambulance nahi mil rahi hai.",
        "मुझे अस्पताल में भर्ती नहीं कर रहे।",
        "Government hospital refused admission.",
        "Medicine not available in government hospital.",
        "Patient ko emergency ward me nahi liya.",
        "Health card not accepted.",
        "Ayushman card se treatment nahi mila.",
        "Doctor refused to treat patient.",
        "Clinic overcharged me for treatment.",
    ],

    "Government Scheme": [
        "My pension application is pending.",
        "Ration card not approved.",
        "Scholarship nahi mili.",
        "सरकारी योजना का लाभ नहीं मिला।",
        "Aadhaar update problem.",
        "Income certificate application delayed.",
        "Caste certificate pending for months.",
        "Subsidy not received.",
        "Domicile certificate reject ho gaya.",
        "Government benefit has not been received.",
    ],

    "Property Issue": [
        "My landlord is forcing me to leave.",
        "Tenant ko ghar se nikal rahe hain.",
        "मकान मालिक जबरदस्ती निकाल रहा है।",
        "Land dispute with neighbour.",
        "Property registry problem.",
        "Illegal occupation of my land.",
        "Rent agreement issue.",
        "Landlord not returning security deposit.",
        "Builder has not given flat possession.",
        "Lease dispute with house owner.",
    ],

    "Public Grievance": [
        "Government department is delaying my application.",
        "Public authority is not responding.",
        "सरकारी विभाग जवाब नहीं दे रहा।",
        "CPGRAMS complaint kaise kare?",
        "My service request is pending for long time.",
        "Department complaint portal me grievance file karna hai.",
        "Application number hai but no update.",
        "Officer is not taking action on complaint.",
        "Public service delivery problem.",
        "Government office me complaint kaha kare?",
    ],

    "Unknown": [
        "Tell me a joke.",
        "What is the weather today?",
        "I want to learn Python.",
        "Who won the cricket match?",
        "Suggest a good phone under 20000.",
        "How to cook pasta?",
        "Explain machine learning.",
        "Play some music.",
        "Write a poem about rain.",
        "What is the capital of Japan?",
    ],
}


FILLERS = {
    "time": [
        "one month",
        "two months",
        "three months",
        "six months",
        "many weeks",
        "90 days",
    ],
    "item": [
        "headphones",
        "phone",
        "laptop",
        "washing machine",
        "shoes",
        "watch",
    ],
}


NOISE_PREFIXES = [
    "",
    "Sir ",
    "Please help, ",
    "Bhai ",
    "Madam ",
    "Urgent, ",
]


NOISE_SUFFIXES = [
    "",
    " what should I do?",
    " help me",
    " complaint kaha karu?",
    " please guide",
    " kaise solve hoga?",
]


def fill_template(template: str) -> str:
    text = template

    for key, values in FILLERS.items():
        placeholder = "{" + key + "}"
        if placeholder in text:
            text = text.replace(placeholder, random.choice(values))

    return text


def add_noise(text: str) -> str:
    prefix = random.choice(NOISE_PREFIXES)
    suffix = random.choice(NOISE_SUFFIXES)

    return (prefix + text + suffix).strip()


def main():
    random.seed(42)

    rows = []

    examples_per_template = 8

    for category, templates in DATA.items():
        for template in templates:
            for _ in range(examples_per_template):
                text = fill_template(template)
                text = add_noise(text)

                rows.append(
                    {
                        "text": text,
                        "category": category,
                    }
                )

    random.shuffle(rows)

    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Saved:", OUTPUT_PATH)
    print("Rows:", len(df))
    print(df["category"].value_counts())


if __name__ == "__main__":
    main()