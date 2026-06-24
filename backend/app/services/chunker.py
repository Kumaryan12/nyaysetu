import hashlib
import json
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    metadata: Dict


def split_text_into_chunks(
    text: str,
    chunk_size_words: int = 450,
    overlap_words: int = 75,
) -> List[str]:
    """
    Splits text into overlapping word chunks.
    """

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size_words
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words).strip()

        if chunk_text:
            chunks.append(chunk_text)

        if end >= len(words):
            break

        start = end - overlap_words

    return chunks


def make_chunk_id(
    source_id: str,
    chunk_index: int,
    chunk_text: str,
) -> str:
    """
    Creates a stable unique chunk ID.

    Important:
    The ID includes source_id and chunk_index, not only text.
    This prevents duplicate IDs when two documents contain similar text.
    """

    raw = f"{source_id}::{chunk_index}::{chunk_text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def chunk_documents(
    documents: List,
    chunk_size_words: int = 450,
    overlap_words: int = 75,
) -> List[DocumentChunk]:
    """
    Converts loaded documents into chunks.

    Each chunk receives:
    - unique chunk_id
    - chunk text
    - metadata copied from source document
    """

    all_chunks: List[DocumentChunk] = []

    for document_index, document in enumerate(documents):
        text = document.text
        metadata = dict(document.metadata)

        source_id = (
            metadata.get("source_id")
            or metadata.get("file_name")
            or metadata.get("title")
            or f"document_{document_index}"
        )

        text_chunks = split_text_into_chunks(
            text=text,
            chunk_size_words=chunk_size_words,
            overlap_words=overlap_words,
        )

        for chunk_index, chunk_text in enumerate(text_chunks):
            chunk_id = make_chunk_id(
                source_id=str(source_id),
                chunk_index=chunk_index,
                chunk_text=chunk_text,
            )

            chunk_metadata = dict(metadata)
            chunk_metadata["chunk_index"] = chunk_index
            chunk_metadata["source_id"] = str(source_id)

            all_chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    metadata=chunk_metadata,
                )
            )

    # Safety check: remove duplicate IDs if any still occur.
    seen_ids = set()
    unique_chunks: List[DocumentChunk] = []

    for chunk in all_chunks:
        if chunk.chunk_id in seen_ids:
            print("Skipping duplicate chunk ID:", chunk.chunk_id)
            continue

        seen_ids.add(chunk.chunk_id)
        unique_chunks.append(chunk)

    return unique_chunks


def save_chunks_jsonl(
    chunks: List[DocumentChunk],
    output_path: str,
) -> None:
    """
    Saves chunks to JSONL format.
    """

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            record = {
                "id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": chunk.metadata,
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_chunks_jsonl(input_path: str) -> List[DocumentChunk]:
    """
    Loads chunks from a JSONL file.

    Expected JSONL format:
    {
      "id": "...",
      "text": "...",
      "metadata": {...}
    }
    """

    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {input_file}")

    chunks: List[DocumentChunk] = []

    with input_file.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            chunks.append(
                DocumentChunk(
                    chunk_id=record["id"],
                    text=record["text"],
                    metadata=record.get("metadata", {}),
                )
            )

    return chunks