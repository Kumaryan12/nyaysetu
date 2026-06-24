import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

SOURCE_REGISTRY_DIR = BACKEND_ROOT / "app" / "data" / "source_registry"
OUTPUT_DIR = BACKEND_ROOT / "app" / "data" / "official_docs_raw"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest official webpages into raw NyayaSetu document files."
    )

    parser.add_argument(
        "--registry",
        default="official_sources.json",
        help=(
            "Registry JSON file inside app/data/source_registry/. "
            "Example: labour_sources.json"
        ),
    )

    return parser.parse_args()


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def trim_leading_navigation_noise(lines: List[str]) -> List[str]:
    """
    Removes large navigation blocks before meaningful content starts.

    This is conservative: it only trims if it finds a likely content marker.
    """

    content_markers = [
        "legal aid",
        "free legal services",
        "national legal services authority",
        "about cpgrams",
        "services for citizen",
        "your grievances, our redressal",
        "centralised public grievance",
        "labour",
        "grievance",
        "wages",
        "samadhan",
        "chief labour commissioner",
        "ministry of labour",
        "consumer helpline",
        "file complaint",
        "cyber crime",
        "women",
        "domestic violence",
    ]

    for index, line in enumerate(lines):
        lower = line.lower()

        if any(marker in lower for marker in content_markers):
            start = max(index - 2, 0)
            return lines[start:]

    return lines


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "form"]):
        tag.decompose()

    candidates = []

    for selector in ["main", "article", ".content", "#content", "body"]:
        selected = soup.select_one(selector)
        if selected:
            candidates.append(selected.get_text(separator="\n"))

    raw_text = max(candidates, key=len) if candidates else soup.get_text(separator="\n")

    lines = []
    seen = set()

    boilerplate_exact = {
        "accessibility tools",
        "color contrast",
        "high contrast",
        "normal contrast",
        "highlight links",
        "invert",
        "saturation",
        "text size",
        "font size increase",
        "font size decrease",
        "normal font",
        "text spacing",
        "line height",
        "others",
        "hide images",
        "big cursor",
        "menu toggle",
        "more",
        "home",
        "about",
        "contact us",
        "skip to main content",
        "screen reader access",
        "screen reader",
        "official login",
        "consumer login",
        "previous",
        "next",
        "view all stories",
        "click here",
        "sign in",
        "download",
        "site map",
    }

    boilerplate_contains = [
        "your browser does not support",
        "a -",
        "a +",
        "---select state---",
    ]

    for line in raw_text.splitlines():
        line = clean_text(line)

        if not line:
            continue

        if len(line) <= 2:
            continue

        line_lower = line.lower().strip()

        if line_lower in boilerplate_exact:
            continue

        if any(fragment in line_lower for fragment in boilerplate_contains):
            continue

        if line_lower in seen:
            continue

        seen.add(line_lower)
        lines.append(line)

    lines = trim_leading_navigation_noise(lines)

    return clean_text("\n".join(lines))


def safe_filename(source_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", source_id)


def fetch_source(source: Dict[str, str]) -> str:
    headers = {
        "User-Agent": "NyayaSetuResearchBot/0.1 educational research project"
    }

    response = requests.get(
        source["url"],
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return extract_text_from_html(response.text)


def save_source_text(source: Dict[str, str], text: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_stem = safe_filename(source["id"])
    text_path = OUTPUT_DIR / f"{file_stem}.txt"
    metadata_path = OUTPUT_DIR / f"{file_stem}.metadata.json"

    header = (
        f"Title: {source['title']}\n"
        f"Publisher: {source['publisher']}\n"
        f"Jurisdiction: {source['jurisdiction']}\n"
        f"URL: {source['url']}\n"
        f"Domain: {source['domain']}\n"
        f"Downloaded on: {date.today().isoformat()}\n\n"
        f"{text}\n"
    )

    text_path.write_text(header, encoding="utf-8")

    metadata = {
        "title": source["title"],
        "source_type": source["source_type"],
        "url": source["url"],
        "jurisdiction": source["jurisdiction"],
        "publisher": source["publisher"],
        "domain": source["domain"],
        "last_checked": date.today().isoformat(),
    }

    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_registry(registry_path: Path) -> List[Dict[str, str]]:
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry file not found: {registry_path}")

    with registry_path.open("r", encoding="utf-8") as f:
        sources = json.load(f)

    if not isinstance(sources, list):
        raise ValueError("Registry file must contain a JSON list of sources.")

    required_fields = {
        "id",
        "title",
        "url",
        "domain",
        "publisher",
        "jurisdiction",
        "source_type",
    }

    for index, source in enumerate(sources):
        missing = required_fields - set(source.keys())

        if missing:
            raise ValueError(
                f"Source at index {index} is missing fields: {sorted(missing)}"
            )

    return sources


def main() -> None:
    args = parse_args()
    registry_path = SOURCE_REGISTRY_DIR / args.registry

    print("NyayaSetu official webpage ingestion")
    print("------------------------------------")
    print("Registry:", registry_path)
    print("Output:", OUTPUT_DIR)

    sources = load_registry(registry_path)

    success = 0
    failed = 0

    for source in sources:
        print(f"\nFetching: {source['title']}")
        print(source["url"])

        try:
            text = fetch_source(source)

            if len(text) < 300:
                print("Warning: extracted text is short. Check manually.")

            save_source_text(source, text)

            print("Saved.")
            success += 1

        except Exception as exc:
            print("Failed:", exc)
            failed += 1

    print("\nDone.")
    print("Successful:", success)
    print("Failed:", failed)


if __name__ == "__main__":
    main()