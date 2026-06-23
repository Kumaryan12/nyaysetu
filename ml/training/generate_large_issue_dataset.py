import random
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "ml" / "datasets" / "issue_classification_large.csv"


RANDOM_SEED = 42
random.seed(RANDOM_SEED)


LABELS = [
    "Labour Dispute",
    "Consumer Complaint",
    "Legal Aid",
    "Police Complaint",
    "Domestic Violence / Safety",
    "Municipal Issue",
    "Healthcare Access",
    "Government Scheme",
    "Property Issue",
    "Public Grievance",
    "Unknown",
]


# Each category has multiple independent pattern groups.
# group_id is important: train/val/test split should separate groups where possible.
DATA_GROUPS = {
    "Labour Dispute": {
        "salary_delay": [
            "My employer has not paid my salary for {duration}.",
            "Company salary nahi de rahi hai {duration} se.",
            "मुझे {duration} से वेतन नहीं मिला है।",
            "Office keeps delaying my salary.",
            "HR says payment will come later but nothing is paid.",
            "Sir mera salary abhi tak nahi aaya.",
            "Mera malik payment rok ke baitha hai.",
        ],
        "final_settlement": [
            "I left my job but final settlement is pending.",
            "Company ne full and final settlement nahi diya.",
            "Resign karne ke baad bhi dues clear nahi kiye.",
            "Employer is not clearing my pending salary after resignation.",
            "My previous company is not paying my last month salary.",
        ],
        "wage_worker": [
            "I worked at a shop but owner did not pay me.",
            "मजदूरी करने के बाद भी पैसे नहीं मिले।",
            "Contractor took work from us and disappeared without payment.",
            "Daily wage ka paisa nahi mila.",
            "Factory owner is not giving wages.",
        ],
        "workplace_violation": [
            "Company is forcing overtime without payment.",
            "Overtime ka paisa nahi mil raha.",
            "Employer terminated me without paying dues.",
            "Boss fired me suddenly and salary is pending.",
            "PF amount company ne nahi diya.",
        ],
    },

    "Consumer Complaint": {
        "refund_issue": [
            "I bought {product} online and seller is not giving refund.",
            "Order cancel hua but refund nahi aaya.",
            "Refund request pending for many days.",
            "Online company promised refund but stopped replying.",
            "Payment deducted but product not received.",
        ],
        "defective_product": [
            "The product is defective and company is refusing replacement.",
            "मेरा सामान खराब आया है और कंपनी बदल नहीं रही।",
            "Fake product mila online order mein.",
            "Shopkeeper sold duplicate product.",
            "Wrong product delivered and seller is ignoring me.",
        ],
        "service_warranty": [
            "Warranty claim rejected without proper reason.",
            "Service center is not repairing my {product}.",
            "Repair center damaged my device and refuses responsibility.",
            "Company is not honoring warranty.",
            "Bill hai but shopkeeper replacement nahi de raha.",
        ],
        "delivery_issue": [
            "Order says delivered but I never got the package.",
            "Parcel delivered dikha raha hai but mila nahi.",
            "Delivery boy marked delivered without giving product.",
            "Package missing but seller is not helping.",
            "I paid online but delivery never happened.",
        ],
    },

    "Legal Aid": {
        "free_lawyer": [
            "I cannot afford a lawyer.",
            "Mujhe free lawyer chahiye.",
            "मुझे मुफ्त कानूनी सहायता चाहिए।",
            "I need advocate help but have no money.",
            "Can poor people get lawyer from government?",
        ],
        "court_help": [
            "I have a court notice but cannot pay lawyer fees.",
            "Court case ke liye legal help chahiye.",
            "I need help for a court case but cannot afford advocate.",
            "Mujhe case ke liye kanooni sahayata chahiye.",
            "District legal services authority se help kaise milegi?",
        ],
        "nalsa_dlsa": [
            "How to apply for NALSA legal aid?",
            "DLSA se free advocate kaise milega?",
            "Legal services authority contact kaise kare?",
            "SLSA legal aid ke liye kya process hai?",
            "Where can I get free legal support?",
        ],
    },

    "Police Complaint": {
        "fir_complaint": [
            "I want to file a police complaint.",
            "Police station complaint kaise kare?",
            "मुझे FIR दर्ज करवानी है।",
            "How can I get FIR copy?",
            "Police FIR copy online kaise milegi?",
        ],
        "theft_fraud": [
            "My phone was stolen.",
            "Mera mobile chori ho gaya hai.",
            "Cyber fraud me paise chale gaye.",
            "Someone stole my bike.",
            "I lost documents and want to report it.",
        ],
        "blackmail_threat": [
            "Someone is blackmailing me online.",
            "Fake Instagram account bana diya mere naam se.",
            "Someone threatened me and I want police help.",
            "Online harassment ke liye police complaint karni hai.",
            "My neighbour hit me and police are not taking complaint.",
        ],
    },

    "Domestic Violence / Safety": {
        "domestic_abuse": [
            "My husband is threatening me and I am scared.",
            "Pati mujhe maar raha hai.",
            "मेरे पति मुझे धमकी दे रहे हैं।",
            "I am facing domestic violence at home.",
            "Partner gets violent and I feel unsafe.",
        ],
        "dowry_family_abuse": [
            "My in-laws are abusing me for dowry.",
            "Sasural wale dahej ke liye torture kar rahe hain.",
            "घर पर मारपीट हो रही है और मैं सुरक्षित नहीं हूं।",
            "I am afraid to go back home.",
            "Family is threatening me inside the house.",
        ],
        "stalking_harassment": [
            "Someone is stalking me daily.",
            "A man follows me from college and sends threats.",
            "My boyfriend is threatening to leak private photos.",
            "Someone is sexually harassing me.",
            "I feel unsafe because someone keeps following me.",
        ],
    },

    "Municipal Issue": {
        "garbage_sanitation": [
            "There is garbage near my house.",
            "गली में कचरा पड़ा है।",
            "No garbage collection in our lane.",
            "Public toilet is very dirty.",
            "Sanitation problem in my area.",
        ],
        "drainage_water": [
            "Drainage problem in my street.",
            "Open drain outside my house is overflowing.",
            "Nala block hai complaint karni hai.",
            "Water pipeline leakage in my colony.",
            "Dirty water is coming in taps.",
        ],
        "roads_lights": [
            "Streetlight is not working.",
            "Road has big potholes.",
            "Road broken hai accident ho sakta hai.",
            "Street dogs and waste problem near school.",
            "Municipal complaint kaha kare?",
        ],
    },

    "Healthcare Access": {
        "hospital_denial": [
            "Hospital denied treatment.",
            "Government hospital refused admission.",
            "मुझे अस्पताल में भर्ती नहीं कर रहे।",
            "Doctor in government hospital sent us away.",
            "Patient ko emergency ward me nahi liya.",
        ],
        "medicine_ambulance": [
            "Ambulance nahi mil rahi hai.",
            "Emergency patient ke liye ambulance nahi aa rahi.",
            "Medicine not available in government hospital.",
            "Hospital is asking money for free medicine.",
            "Medical emergency hai help chahiye.",
        ],
        "health_card": [
            "Health card not accepted.",
            "Ayushman card se treatment nahi mila.",
            "Insurance card hospital accept nahi kar raha.",
            "Clinic overcharged me for treatment.",
            "Government scheme health card not working.",
        ],
    },

    "Government Scheme": {
        "ration_pension": [
            "My pension application is pending.",
            "Widow pension stopped suddenly.",
            "Ration card not approved.",
            "Ration dealer says my name is removed.",
            "सरकारी योजना का लाभ नहीं मिला।",
        ],
        "certificates": [
            "Income certificate application delayed.",
            "Caste certificate pending for months.",
            "Domicile certificate reject ho gaya.",
            "Certificate application portal me stuck hai.",
            "Government certificate not issued yet.",
        ],
        "scholarship_subsidy": [
            "Scholarship nahi mili.",
            "Subsidy not received.",
            "PM scholarship application rejected without reason.",
            "Government benefit has not been received.",
            "Aadhaar update problem is blocking scheme benefit.",
        ],
    },

    "Property Issue": {
        "landlord_tenant": [
            "My landlord is forcing me to leave.",
            "Makan malik jabardasti nikal raha hai.",
            "Landlord not returning security deposit.",
            "Landlord entered my room without permission.",
            "Tenant ko ghar se nikal rahe hain.",
        ],
        "land_dispute": [
            "Land dispute with neighbour.",
            "Neighbour has occupied part of our land.",
            "Illegal occupation of my land.",
            "Property boundary dispute with neighbour.",
            "Zameen par illegal kabza ho gaya.",
        ],
        "builder_registry": [
            "Builder delayed flat possession.",
            "Property registry problem.",
            "Flat possession not given by builder.",
            "Lease dispute with house owner.",
            "Rent agreement issue.",
        ],
    },

    "Public Grievance": {
        "department_delay": [
            "Government department is delaying my application.",
            "Public authority is not responding.",
            "सरकारी विभाग जवाब नहीं दे रहा।",
            "Department has not updated my application.",
            "Government office keeps sending me from one counter to another.",
        ],
        "portal_complaint": [
            "CPGRAMS complaint kaise kare?",
            "No response to complaint submitted on portal.",
            "Department complaint portal me grievance file karna hai.",
            "Application number hai but no update.",
            "Public service delivery problem.",
        ],
        "official_inaction": [
            "Officer is not taking action on complaint.",
            "Government office me complaint kaha kare?",
            "My service request is pending for long time.",
            "Written complaint diya but no action.",
            "Public authority ignored my request.",
        ],
    },

    "Unknown": {
        "general_chat": [
            "Tell me a joke.",
            "Write a birthday message for my friend.",
            "Explain blockchain in simple words.",
            "What is the capital of Japan?",
            "Who won the cricket match?",
        ],
        "shopping_general": [
            "Suggest a good phone under 20000.",
            "Which laptop should I buy for coding?",
            "Best headphones under 3000?",
            "Recommend shoes for running.",
            "Compare iPhone and Samsung.",
        ],
        "education_tech": [
            "I want to learn Python.",
            "Explain machine learning.",
            "How to prepare for GATE?",
            "Give me a DSA roadmap.",
            "Help me build a portfolio website.",
        ],
        "health_general": [
            "What is the best diet for weight loss?",
            "How many calories in rice?",
            "Give me a gym workout plan.",
            "What is good skincare routine?",
            "How to improve sleep?",
        ],
    },
}


DURATIONS = [
    "one week",
    "two weeks",
    "one month",
    "two months",
    "three months",
    "four months",
    "six months",
    "90 days",
    "many weeks",
]


PRODUCTS = [
    "phone",
    "headphones",
    "laptop",
    "washing machine",
    "shoes",
    "watch",
    "earbuds",
    "refrigerator",
    "mobile charger",
]


PREFIXES = [
    "",
    "Sir ",
    "Madam ",
    "Please help, ",
    "Bhai ",
    "Hello, ",
    "Urgent, ",
    "I need help, ",
    "Can you guide me, ",
]


SUFFIXES = [
    "",
    " what should I do?",
    " please guide.",
    " help me.",
    " complaint kaha karu?",
    " kaise solve hoga?",
    " where should I go?",
    " mujhe kya karna chahiye?",
]


TYPO_REPLACEMENTS = {
    "salary": ["salry", "sallery"],
    "complaint": ["complain", "complnt"],
    "government": ["govt", "goverment"],
    "police": ["polic", "policee"],
    "refund": ["refnd", "refundd"],
    "hospital": ["hospitl"],
    "application": ["aplication", "applicaton"],
}


def fill_placeholders(text: str) -> str:
    text = text.replace("{duration}", random.choice(DURATIONS))
    text = text.replace("{product}", random.choice(PRODUCTS))
    return text


def maybe_add_noise(text: str) -> str:
    if random.random() < 0.65:
        text = random.choice(PREFIXES) + text

    if random.random() < 0.65:
        text = text + random.choice(SUFFIXES)

    # Random lowercasing
    if random.random() < 0.25:
        text = text.lower()

    # Light typo injection
    if random.random() < 0.20:
        for word, replacements in TYPO_REPLACEMENTS.items():
            if word in text.lower():
                text = text.replace(word, random.choice(replacements))
                break

    # Speech-like filler
    if random.random() < 0.20:
        text = text.replace("I ", "Actually I ", 1)

    return " ".join(text.split())


def generate_rows(examples_per_template: int = 10):
    rows = []

    for category, groups in DATA_GROUPS.items():
        for group_name, templates in groups.items():
            for template in templates:
                for _ in range(examples_per_template):
                    text = fill_placeholders(template)
                    text = maybe_add_noise(text)

                    rows.append(
                        {
                            "text": text,
                            "category": category,
                            "group": category + "__" + group_name,
                        }
                    )

    random.shuffle(rows)
    return rows


def main():
    rows = generate_rows(examples_per_template=10)

    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Saved:", OUTPUT_PATH)
    print("Rows:", len(df))
    print("\nCategory distribution:")
    print(df["category"].value_counts())
    print("\nGroup distribution:")
    print(df["group"].value_counts().head(20))


if __name__ == "__main__":
    main()