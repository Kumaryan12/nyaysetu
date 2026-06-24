import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List


BACKEND_ROOT = Path(__file__).resolve().parents[1]
RAG_DOCS_DIR = BACKEND_ROOT / "app" / "data" / "rag_docs"


REQUIRED_METADATA_FIELDS = [
    "title",
    "source_type",
    "url",
    "jurisdiction",
    "publisher",
    "domain",
    "last_checked",
]


NOISE_PATTERNS = [
    "login",
    "skip to main content",
    "screen reader",
    "accessibility tools",
    "font size",
    "total visitors",
    "copyright",
    "best viewed",
    "privacy policy",
    "login",
    "sign in",
    "photo gallery",
    "video gallery",
    "sitemap",
]


BROKEN_TABLE_PATTERNS = [
    "s.no",
    "states/union territories",
    "income ceiling limit",
]


def load_metadata(metadata_path: Path) -> Dict:
    if not metadata_path.exists():
        return {}

    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect_noise(text: str) -> List[str]:
    text_lower = text.lower()

    flags = []

    for pattern in NOISE_PATTERNS:
        if pattern in text_lower:
            flags.append(pattern)

    return flags


def detect_broken_table(text: str) -> List[str]:
    text_lower = text.lower()

    flags = []

    for pattern in BROKEN_TABLE_PATTERNS:
        if pattern in text_lower:
            flags.append(pattern)

    return flags


def top_repeated_lines(text: str, min_count: int = 3) -> List[str]:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    counts = Counter(lines)

    repeated = [
        line
        for line, count in counts.most_common(10)
        if count >= min_count
    ]

    return repeated


def audit_file(txt_path: Path) -> Dict:
    text = txt_path.read_text(encoding="utf-8", errors="ignore")
    words = text.split()

    metadata_path = txt_path.with_suffix(".metadata.json")
    metadata = load_metadata(metadata_path)

    missing_fields = [
        field for field in REQUIRED_METADATA_FIELDS
        if not metadata.get(field)
    ]

    noise_flags = detect_noise(text)
    broken_table_flags = detect_broken_table(text)
    repeated_lines = top_repeated_lines(text)

    status = "GOOD"

    if not metadata:
        status = "REVIEW"

    if missing_fields:
        status = "REVIEW"

    if len(words) < 120:
        status = "REVIEW"

    if noise_flags:
        status = "REVIEW"

    if broken_table_flags:
        status = "REVIEW"

    return {
        "file": txt_path.name,
        "words": len(words),
        "title": metadata.get("title", ""),
        "domain": metadata.get("domain", ""),
        "source_type": metadata.get("source_type", ""),
        "metadata_exists": bool(metadata),
        "missing_fields": missing_fields,
        "noise_flags": noise_flags,
        "broken_table_flags": broken_table_flags,
        "repeated_lines": repeated_lines,
        "status": status,
    }


def main() -> None:
    print("NyayaSetu RAG docs audit")
    print("------------------------")
    print("RAG docs dir:", RAG_DOCS_DIR)

    txt_files = sorted(RAG_DOCS_DIR.glob("*.txt"))

    if not txt_files:
        print("No .txt files found.")
        return

    results = []

    for txt_path in txt_files:
        result = audit_file(txt_path)
        results.append(result)

    good_count = sum(1 for item in results if item["status"] == "GOOD")
    review_count = sum(1 for item in results if item["status"] == "REVIEW")

    print("\nSummary")
    print("-------")
    print("Total docs:", len(results))
    print("GOOD:", good_count)
    print("REVIEW:", review_count)

    print("\nDetails")
    print("-------")

    for item in results:
        print(
            f"{item['status']:6} "
            f"{item['file']:<45} "
            f"{item['words']:>5} words "
            f"{item['domain']}"
        )

        if item["missing_fields"]:
            print("       Missing metadata:", item["missing_fields"])

        if item["noise_flags"]:
            print("       Noise flags:", item["noise_flags"])

        if item["broken_table_flags"]:
            print("       Broken table flags:", item["broken_table_flags"])

        if item["repeated_lines"]:
            print("       Repeated lines:", item["repeated_lines"][:3])

    output_path = BACKEND_ROOT / "app" / "data" / "eval" / "rag_audit_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nSaved audit report:", output_path)


if __name__ == "__main__":
    main()