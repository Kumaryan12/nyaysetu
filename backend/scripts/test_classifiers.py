import sys
from pathlib import Path

# Allows this script to import from app/ when run from backend/
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

from app.core.issue_classifier import classify_issue
from app.core.urgency_detector import detect_urgency


TEST_QUERIES = [
    "My employer has not paid my salary for three months.",
    "I bought headphones online and the seller is not giving a refund.",
    "I cannot afford a lawyer. Where can I get help?",
    "My husband is threatening me and I am scared.",
    "There is garbage and drainage problem near my house.",
    "I want to file a police complaint and get FIR copy.",
    "A government department is delaying my application.",
    "My landlord is forcing me to leave the house today.",
    "I want to check my court case status.",
]


def main() -> None:
    print("NyayaSetu classifier test")
    print("------------------------")

    for query in TEST_QUERIES:
        issue = classify_issue(query)
        urgency = detect_urgency(query)

        print("\n" + "=" * 80)
        print("Query:", query)
        print("-" * 80)
        print("Category:", issue.category)
        print("Category confidence:", issue.confidence)
        print("Matched keywords:", issue.matched_keywords)
        print("Urgency:", urgency.urgency)
        print("Urgency confidence:", urgency.confidence)
        print("Urgency reasons:", urgency.reasons)


if __name__ == "__main__":
    main()