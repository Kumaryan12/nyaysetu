import re
from pathlib import Path
from typing import List


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = BACKEND_ROOT / "app" / "data" / "official_docs"


DROP_EXACT = {
    "home",
    "about",
    "contact",
    "contact us",
    "download",
    "site map",
    "disclaimer",
    "privacy policy",
    "website policies",
    "previous",
    "next",
    "register",
    "track now",
    "upload",
    "chat now",
    "feedback",
    "logins",
    "company login",
    "regulators login",
    "other",
    "track grievance",
    "upload docs",
    "leave a feedback",
    "quick links",
    "services",
    "library",
    "reports",
    "accounts",
    "newsletters",
    "publications",
    "campaigns",
    "commendation",
    "covid 19",
    "what's new",
    "register / login",
    "screen reader",
    "skip to main content",
    "screen reader access",
    "accessibility tools",
    "menu toggle",
    "more",
    "normal font",
    "big cursor",
    "hide images",
    "font size increase",
    "font size decrease",
    "high contrast",
    "normal contrast",
    "highlight links",
    "invert",
    "saturation",
    "text size",
    "text spacing",
    "line height",
    "others",
}


DROP_CONTAINS = [
    "total visitors",
    "last updated on",
    "best viewed",
    "this site is designed",
    "copyright",
    "your browser does not support",
    "view story",
    "excellent",
    "thank you",
    "received satisfactory resolution",
    "click here",
    "portal is compatible",
    "version ",
    "facebook",
    "twitter",
    "instagram",
    "youtube",
]


STATE_NAMES = {
    "andaman and nicobar",
    "andhra pradesh",
    "arunachal pradesh",
    "assam",
    "bihar",
    "chandigarh",
    "chhattisgarh",
    "dadra & nagar haveli and daman & diu",
    "delhi",
    "goa",
    "gujarat",
    "haryana",
    "himachal pradesh",
    "jammu and kashmir",
    "jharkhand",
    "karnataka",
    "kerala",
    "lakshadweep",
    "madhya pradesh",
    "maharashtra",
    "manipur",
    "meghalaya",
    "mizoram",
    "nagaland",
    "odisha",
    "puducherry",
    "punjab",
    "rajasthan",
    "sikkim",
    "tamil nadu",
    "telangana",
    "tripura",
    "uttar pradesh",
    "uttarakhand",
    "west bengal",
}


NALSA_MENU_TERMS = {
    "about nalsa",
    "introduction",
    "promoting inclusive legal system",
    "vision and mission",
    "organogram",
    "patron-in-chief",
    "former patrons-in-chief",
    "executive chairman",
    "former executive chairman",
    "members",
    "member secretaries, nalsa",
    "directory",
    "acts & rules",
    "rules",
    "regulations",
    "preventive & strategic legal services schemes",
    "the commercial courts act & rules",
    "women and law",
    "important bare acts",
    "guidelines",
    "lok adalats",
    "permanent lok adalat",
    "regular lok adalat",
    "national lok adalat",
    "mediation",
    "legal awareness/literacy",
    "victim compensation",
    "social action litigation",
    "vulnerable groups",
    "women",
    "children",
    "persons with mental disability or intellectual disability",
    "e-services",
    "legal aid application",
    "victim compensation application",
    "lsams portal",
    "lacms portal",
    "legal aid defense counsel",
    "handbook of formats",
    "pan india campaign 2022",
    "pan india awareness & outreach campaign",
    "nyaya deep",
    "nalsa asha",
    "nalsa asha english",
    "nalsa asha hindi",
    "nari ki udaan",
    "training modules",
    "grants & accounts",
}


def clean_line(line: str) -> str:
    line = line.replace("\xa0", " ")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def is_noise_line(line: str) -> bool:
    lower = line.lower().strip()

    if not lower:
        return True

    if len(lower) <= 2:
        return True

    if lower in DROP_EXACT:
        return True

    if lower in STATE_NAMES:
        return True

    if lower in NALSA_MENU_TERMS:
        return True

    if any(fragment in lower for fragment in DROP_CONTAINS):
        return True

    # Drop isolated dates/month headings from news sections.
    if lower in {
        "january 2022",
        "february 2022",
        "march 2022",
        "april 2022",
        "may 2022",
        "june 2022",
        "july 2022",
        "august 2022",
        "september 2022",
        "october 2022",
        "november 2022",
        "december 2022",
        "january 2023",
        "february 2023",
        "march 2023",
        "april 2023",
        "may 2023",
        "june 2023",
        "july 2023",
        "august 2023",
        "january 2024",
        "february 2024",
        "march 2024",
        "april 2024",
        "may 2024",
        "june 2024",
        "july 2024",
        "august 2024",
    }:
        return True

    return False


def preserve_header(lines: List[str]) -> tuple[List[str], List[str]]:
    """
    Keeps the first metadata header block until the first blank line.
    """

    header = []
    rest_start = 0

    for index, line in enumerate(lines):
        header.append(line)
        if not line.strip():
            rest_start = index + 1
            break

    return header, lines[rest_start:]


def clean_document_text(text: str) -> str:
    raw_lines = text.splitlines()

    header, body_lines = preserve_header(raw_lines)

    cleaned_body = []
    seen = set()

    for line in body_lines:
        line = clean_line(line)

        if is_noise_line(line):
            continue

        lower = line.lower()

        if lower in seen:
            continue

        seen.add(lower)
        cleaned_body.append(line)

    # Remove excessive blank lines.
    final_text = "\n".join(header + cleaned_body)
    final_text = re.sub(r"\n{3,}", "\n\n", final_text)
    return final_text.strip() + "\n"


def main() -> None:
    print("NyayaSetu official docs cleaner")
    print("-------------------------------")
    print("Docs dir:", DOCS_DIR)

    txt_files = sorted(DOCS_DIR.glob("*.txt"))

    for path in txt_files:
        before = path.read_text(encoding="utf-8", errors="ignore")
        after = clean_document_text(before)

        before_words = len(before.split())
        after_words = len(after.split())

        path.write_text(after, encoding="utf-8")

        print(
            f"{path.name}: {before_words} words -> {after_words} words"
        )


if __name__ == "__main__":
    main()