import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

from app.services.document_loader import LoadedDocument


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    chunk_index: int
    metadata: Dict[str, str]


def normalize_text_for_chunking(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def generate_chunk_id(source_identifier: str, chunk_index: int) -> str:
    raw = f"{source_identifier}::{chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def split_words_with_overlap(
    words: List[str],
    chunk_size_words: int,
    overlap_words: int,
) -> List[List[str]]:
    """
    Splits words into overlapping chunks.

    Example:
        chunk_size_words = 450
        overlap_words = 75

    Chunk 1: words 0-449
    Chunk 2: words 375-824
    """

    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be positive.")

    if overlap_words < 0:
        raise ValueError("overlap_words cannot be negative.")

    if overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be smaller than chunk_size_words.")

    chunks: List[List[str]] = []

    start = 0

    while start < len(words):
        end = start + chunk_size_words
        chunk_words = words[start:end]

        if chunk_words:
            chunks.append(chunk_words)

        start = end - overlap_words

    return chunks


def chunk_document(
    document: LoadedDocument,
    chunk_size_words: int = 450,
    overlap_words: int = 75,
) -> List[DocumentChunk]:
    """
    Splits a single loaded document into chunks.
    """

    normalized_text = normalize_text_for_chunking(document.text)

    words = normalized_text.split()

    if not words:
        return []

    source_identifier = (
        document.metadata.get("url")
        or document.metadata.get("file_path")
        or document.metadata.get("title")
        or "unknown_source"
    )

    word_chunks = split_words_with_overlap(
        words=words,
        chunk_size_words=chunk_size_words,
        overlap_words=overlap_words,
    )

    chunks: List[DocumentChunk] = []

    for index, chunk_words in enumerate(word_chunks):
        chunk_text = " ".join(chunk_words).strip()

        chunk_metadata = dict(document.metadata)
        chunk_metadata["chunk_index"] = str(index)
        chunk_metadata["chunk_size_words"] = str(len(chunk_words))

        chunks.append(
            DocumentChunk(
                chunk_id=generate_chunk_id(source_identifier, index),
                text=chunk_text,
                chunk_index=index,
                metadata=chunk_metadata,
            )
        )

    return chunks


def chunk_documents(
    documents: List[LoadedDocument],
    chunk_size_words: int = 450,
    overlap_words: int = 75,
) -> List[DocumentChunk]:
    """
    Splits multiple loaded documents into chunks.
    """

    all_chunks: List[DocumentChunk] = []

    for document in documents:
        chunks = chunk_document(
            document=document,
            chunk_size_words=chunk_size_words,
            overlap_words=overlap_words,
        )

        all_chunks.extend(chunks)

    return all_chunks


def save_chunks_jsonl(chunks: List[DocumentChunk], output_path: str) -> None:
    """
    Saves chunks into a JSONL file.

    JSONL means:
        One JSON object per line.

    This is useful for debugging and later indexing.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            row = asdict(chunk)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_chunks_jsonl(input_path: str) -> List[DocumentChunk]:
    """
    Loads chunks back from JSONL.
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Chunks file not found: {path}")

    chunks: List[DocumentChunk] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            row = json.loads(line)

            chunks.append(
                DocumentChunk(
                    chunk_id=row["chunk_id"],
                    text=row["text"],
                    chunk_index=int(row["chunk_index"]),
                    metadata=row.get("metadata", {}),
                )
            )

    return chunks