import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

import requests
from pypdf import PdfReader


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

SOURCE_REGISTRY_DIR = BACKEND_ROOT / "app" / "data" / "source_registry"
OUTPUT_DIR = BACKEND_ROOT / "app" / "data" / "official_docs_raw"
TMP_PDF_DIR = BACKEND_ROOT / "app" / "data" / "tmp_pdfs"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest official PDFs into NyayaSetu raw document files."
    )
    parser.add_argument(
        "--registry",
        default="labour_sources.json",
        help="Registry JSON file inside app/data/source_registry/",
    )
    return parser.parse_args()


def safe_filename(source_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", source_id)


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_registry(registry_path: Path) -> List[Dict[str, str]]:
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry file not found: {registry_path}")

    with registry_path.open("r", encoding="utf-8") as f:
        sources = json.load(f)

    if not isinstance(sources, list):
        raise ValueError("Registry must contain a JSON list of sources.")

    return sources


def download_pdf(url: str, pdf_path: Path) -> None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept": "application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.indiacode.nic.in/",
    }

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    pdf_path.write_bytes(response.content)


def resolve_pdf_path(source: Dict[str, str]) -> Path:
    local_path = source.get("local_path")

    if local_path:
        pdf_path = BACKEND_ROOT / local_path

        if not pdf_path.exists():
            raise FileNotFoundError(f"Local PDF not found: {pdf_path}")

        return pdf_path

    TMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
    file_stem = safe_filename(source["id"])
    pdf_path = TMP_PDF_DIR / f"{file_stem}.pdf"

    download_pdf(source["url"], pdf_path)
    return pdf_path


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        page_text = clean_text(page_text)

        if page_text:
            pages.append(f"[Page {page_number}]\n{page_text}")

    return clean_text("\n\n".join(pages))


def save_pdf_source(source: Dict[str, str], text: str) -> None:
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


def main() -> None:
    args = parse_args()
    registry_path = SOURCE_REGISTRY_DIR / args.registry

    print("NyayaSetu official PDF ingestion")
    print("--------------------------------")
    print("Registry:", registry_path)
    print("Output:", OUTPUT_DIR)

    sources = load_registry(registry_path)

    pdf_sources = [
        source for source in sources
        if source.get("source_type") == "official_pdf"
    ]

    print("PDF sources found:", len(pdf_sources))

    success = 0
    failed = 0

    for source in pdf_sources:
        print(f"\nProcessing PDF: {source['title']}")

        try:
            pdf_path = resolve_pdf_path(source)
            print("PDF path:", pdf_path)

            text = extract_pdf_text(pdf_path)

            if len(text) < 1000:
                print("Warning: extracted PDF text is short. Check manually.")

            save_pdf_source(source, text)

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