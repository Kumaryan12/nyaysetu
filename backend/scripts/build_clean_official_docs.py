import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


BACKEND_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = BACKEND_ROOT / "app" / "data" / "official_docs_raw"
CLEAN_DIR = BACKEND_ROOT / "app" / "data" / "official_docs_clean"


DROP_EXACT = {
    "share on facebook",
"share of x (formerly twitter)",
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
"legal aid",
"grants & accounts",
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
    "normal contrast",
    "high contrast",
    "highlight links",
    "invert",
    "saturation",
    "text size",
    "text spacing",
    "line height",
    "others",
    "close",
    "share on linkedin",
    "subscribe",
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
    "portal is compatible",
    "version ",
    "visitors count",
    "content owned by",
    "site maintained by",
    "hyperlink policy",
    "accessibility statement",
    "terms and conditions",
    "sitemap",
    "web information manager",
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


NALSA_NOISE = {
    "department of justice",
    "राष्ट्रीय विधिक सेवा प्राधिकरण",
    "national legal services authority",
    "the legal services authorities act, 1987",
    "e-book – compendium on human-wildlife conflict, 2025",
    "manual for district legal services authorities 2023",
    "report on the north zone regional conference on enhancing access to justice",
    "report of the national conference on “strengthening legal aid delivery mechanisms”, 8–9 november 2025",
    "state profiles 2022-23",
    "nalsa at a glance",
    "statistical snapshot",
    "annual reports",
    "green verdicts: a comprehensive digest of recent environmental law cases",
    "student awareness resource on ragging, 2026",
    "expenditure of slsa",
    "grants",
    "notice",
    "samadhan samaroh, 2026",
    "internship programme",
    "internal committee",
    "tenders",
    "recruitment",
    "media",
    "photo gallery",
    "video gallery",
    "audio gallery",
    "media coverage",
    "statistics",
    "slsas",
    "panel lawyers",
    "para legal volunteers",
}


def clean_line(line: str) -> str:
    line = line.replace("\xa0", " ")
    line = line.replace("&amp;", "&")
    line = line.replace("&#39;", "'")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def split_header_and_body(text: str) -> Tuple[List[str], List[str]]:
    lines = text.splitlines()

    header = []
    body_start = 0

    for index, line in enumerate(lines):
        header.append(line)
        if not line.strip():
            body_start = index + 1
            break

    return header, lines[body_start:]


def is_noise_line(line: str) -> bool:
    lower = line.lower().strip()

    if not lower:
        return True

    if len(lower) <= 2:
        return True

    if lower in DROP_EXACT:
        return True

    if lower in DROP_CONTAINS:
        return True

    if lower in STATE_NAMES:
        return True

    if lower in NALSA_NOISE:
        return True

    if any(fragment in lower for fragment in DROP_CONTAINS):
        return True

    if re.fullmatch(r"[0-9,]+", lower):
        return True

    if re.fullmatch(r"\(?since [0-9\-]+\)?", lower):
        return True

    return False


def keep_from_marker(lines: List[str], markers: List[str]) -> List[str]:
    """
    Trim lines before the first useful marker.
    If no marker is found, return original lines.
    """

    for index, line in enumerate(lines):
        lower = line.lower()

        if any(marker in lower for marker in markers):
            return lines[index:]

    return lines


def stop_after_marker(lines: List[str], stop_markers: List[str]) -> List[str]:
    """
    Remove footer/news content after a stop marker.
    """

    for index, line in enumerate(lines):
        lower = line.lower()

        if any(marker in lower for marker in stop_markers):
            return lines[:index]

    return lines


def generic_clean_body(lines: List[str]) -> List[str]:
    cleaned = []
    seen = set()

    for line in lines:
        line = clean_line(line)

        if is_noise_line(line):
            continue

        lower = line.lower()

        if lower in seen:
            continue

        seen.add(lower)
        cleaned.append(line)

    return cleaned


def clean_nalsa(source_id: str, lines: List[str]) -> List[str]:
    if source_id == "nalsa_legal_aid":
        lines = keep_from_marker(
            lines,
            markers=[
                "what are legal services?",
                "what are legal services",
                "legal services includes providing free legal aid",
            ],
        )

        lines = stop_after_marker(
            lines,
            stop_markers=[
                "the income ceiling limit prescribed",
                "s.no",
                "states/union territories",
                "income ceiling limit",
            ],
        )

    elif source_id == "nalsa_faq":
        lines = keep_from_marker(
            lines,
            markers=[
                "frequently asked questions",
                "who are entitled to free legal services",
                "whether a woman is eligible for free legal aid",
                "free legal aid",
            ],
        )

        lines = stop_after_marker(
            lines,
            stop_markers=[
                "the income ceiling limit prescribed",
                "s.no",
                "states/union territories",
                "income ceiling limit",
            ],
        )

    elif source_id == "nalsa_womens_assistance":
        lines = keep_from_marker(
            lines,
            markers=[
                "women",
                "assistance",
                "domestic violence",
                "legal services",
            ],
        )

    return generic_clean_body(lines)

def clean_consumer(source_id: str, lines: List[str]) -> List[str]:
    lines = keep_from_marker(
        lines,
        markers=[
            "your grievances, our redressal",
            "multiple ways to lodge grievances",
            "national consumer helpline",
            "register grievance",
        ],
    )

    lines = stop_after_marker(
        lines,
        stop_markers=[
            "nch success stories",
            "provide feedback",
            "privacy policy",
            "total visitors",
        ],
    )

    return generic_clean_body(lines)


def clean_digital_police(source_id: str, lines: List[str]) -> List[str]:
    lines = keep_from_marker(
        lines,
        markers=[
            "this portal is a platform",
            "services for citizen",
            "services provided by state police citizen portals",
        ],
    )

    lines = stop_after_marker(
        lines,
        stop_markers=[
            "services for police",
            "quick links",
            "reach us",
            "ministry of home affairs, north block",
        ],
    )

    return generic_clean_body(lines)


def clean_labour(source_id: str, lines: List[str]) -> List[str]:
    if source_id == "chief_labour_commissioner":
        lines = keep_from_marker(
            lines,
            markers=[
                "the organization of the chief labour commissioner",
                "workers grievances & claim",
                "lodge a grievance",
                "public grievance",
            ],
        )

        lines = stop_after_marker(
            lines,
            stop_markers=[
                "what's new",
                "annual general transfer",
                "importants links",
                "footer utility",
                "disclaimer",
                "copyright",
            ],
        )

    elif source_id == "samadhan_portal":
        lines = keep_from_marker(
            lines,
            markers=[
                "samadhan",
                "grievance",
                "labour",
                "workers",
            ],
        )

    elif source_id == "ministry_labour_home":
        lines = keep_from_marker(
            lines,
            markers=[
                "ministry of labour",
                "labour",
                "employment",
            ],
        )

    return generic_clean_body(lines)


def clean_cpgrams(source_id: str, lines: List[str]) -> List[str]:
    lines = keep_from_marker(
        lines,
        markers=[
            "any grievance sent by email",
            "about cpgrams",
            "centralised public grievance",
        ],
    )

    lines = stop_after_marker(
        lines,
        stop_markers=[
            "what's new",
            "register / login",
            "this site is designed",
            "web information manager",
        ],
    )

    return generic_clean_body(lines)


def clean_default(source_id: str, lines: List[str]) -> List[str]:
    return generic_clean_body(lines)


def choose_cleaner(source_id: str):
    if source_id.startswith("nalsa"):
        return clean_nalsa

    if source_id.startswith("consumer_"):
        return clean_consumer

    if source_id.startswith("digital_police"):
        return clean_digital_police

    if source_id.startswith("cpgrams"):
        return clean_cpgrams
    
    if source_id in {
        "code_on_wages_2019",
        "payment_of_wages_act_1936",
    }:
        return clean_labour_pdf
    
    if source_id in {
        "samadhan_portal",
        "chief_labour_commissioner",
        "ministry_labour_home",
    }:
        return clean_labour

    return clean_default

def clean_labour_pdf(source_id: str, lines: List[str]) -> List[str]:
    """
    Cleans labour law PDF text extracted from India Code.
    Keeps useful sections and removes excessive arrangement/index pages where possible.
    """

    if source_id == "code_on_wages_2019":
        lines = keep_from_marker(
            lines,
            markers=[
                "the code on wages, 2019",
                "chapter i",
                "preliminary",
                "definitions",
            ],
        )

        # Keep the Act text, but remove excessive later schedules/rules if needed later.
        return generic_clean_body(lines)

    if source_id == "payment_of_wages_act_1936":
        lines = keep_from_marker(
            lines,
            markers=[
                "the payment of wages act, 1936",
                "an act to regulate the payment of wages",
                "short title, extent, commencement and application",
            ],
        )

        return generic_clean_body(lines)

    return generic_clean_body(lines)


def clean_file(raw_path: Path) -> None:
    source_id = raw_path.stem

    text = raw_path.read_text(encoding="utf-8", errors="ignore")
    header, body_lines = split_header_and_body(text)

    cleaner = choose_cleaner(source_id)
    cleaned_body = cleaner(source_id, body_lines)

    if len(cleaned_body) < 5:
        print(f"WARNING: Very short cleaned body for {raw_path.name}")

    final_text = "\n".join(header + cleaned_body)
    final_text = re.sub(r"\n{3,}", "\n\n", final_text).strip() + "\n"

    clean_path = CLEAN_DIR / raw_path.name
    clean_path.write_text(final_text, encoding="utf-8")

    raw_words = len(text.split())
    clean_words = len(final_text.split())

    print(f"{raw_path.name}: {raw_words} words -> {clean_words} words")


def copy_metadata(raw_metadata_path: Path) -> None:
    clean_metadata_path = CLEAN_DIR / raw_metadata_path.name
    data = json.loads(raw_metadata_path.read_text(encoding="utf-8"))
    clean_metadata_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    print("NyayaSetu raw-to-clean official docs builder")
    print("--------------------------------------------")
    print("Raw dir:", RAW_DIR)
    print("Clean dir:", CLEAN_DIR)

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    # Clear old generated clean txt/metadata files only.
    for path in CLEAN_DIR.glob("*.txt"):
        path.unlink()

    for path in CLEAN_DIR.glob("*.metadata.json"):
        path.unlink()

    raw_txt_files = sorted(RAW_DIR.glob("*.txt"))
    raw_metadata_files = sorted(RAW_DIR.glob("*.metadata.json"))

    for raw_path in raw_txt_files:
        clean_file(raw_path)

    for metadata_path in raw_metadata_files:
        copy_metadata(metadata_path)

    print("\nDone.")


if __name__ == "__main__":
    main()