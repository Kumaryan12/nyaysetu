import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass
class LoadedDocument:
    
    text: str
    metadata: Dict[str, str]


def clean_extracted_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_sidecar_metadata(file_path: Path) -> Dict[str, str]:

    metadata_path = file_path.with_suffix(".metadata.json")

    if not metadata_path.exists():
        return {}

    with metadata_path.open("r", encoding="utf-8") as f:
        raw_metadata = json.load(f)

    metadata = {}

    for key, value in raw_metadata.items():
        if value is None:
            metadata[key] = ""
        else:
            metadata[key] = str(value)

    return metadata


def read_txt_or_md(file_path: Path) -> str:

    return file_path.read_text(encoding="utf-8", errors="ignore")


def read_pdf(file_path: Path) -> str:
    

    reader = PdfReader(str(file_path))
    pages_text: List[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages_text.append(
                "\n\n"
                + f"[Page {page_number}]"
                + "\n"
                + page_text
            )

    return "\n".join(pages_text)


def build_default_metadata(file_path: Path) -> Dict[str, str]:

    return {
        "title": file_path.stem.replace("_", " ").replace("-", " ").title(),
        "file_name": file_path.name,
        "file_path": str(file_path),
        "source_type": "official_document",
        "url": "",
        "jurisdiction": "India",
        "last_checked": "",
    }


def load_document(file_path: Path) -> Optional[LoadedDocument]:

    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        return None

    if suffix in {".txt", ".md"}:
        raw_text = read_txt_or_md(file_path)
    elif suffix == ".pdf":
        raw_text = read_pdf(file_path)
    else:
        return None

    cleaned_text = clean_extracted_text(raw_text)

    if not cleaned_text:
        return None

    metadata = build_default_metadata(file_path)
    metadata.update(load_sidecar_metadata(file_path))

    return LoadedDocument(
        text=cleaned_text,
        metadata=metadata,
    )


def load_documents_from_directory(directory: str) -> List[LoadedDocument]:
    root = Path(directory)

    if not root.exists():
        raise FileNotFoundError(f"Document directory not found: {root}")

    documents: List[LoadedDocument] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        loaded = load_document(file_path)

        if loaded is not None:
            documents.append(loaded)

    return documents