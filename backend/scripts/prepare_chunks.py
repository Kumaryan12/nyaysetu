import sys
from pathlib import Path

# Allows this script to import from app/ when run from backend/
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

from app.services.chunker import chunk_documents, save_chunks_jsonl
from app.services.document_loader import load_documents_from_directory


OFFICIAL_DOCS_DIR = BACKEND_ROOT / "app" / "data" / "rag_docs"
OUTPUT_CHUNKS_PATH = BACKEND_ROOT / "app" / "data" / "processed" / "chunks.jsonl"


def main() -> None:
    print("NyayaSetu document chunk preparation")
    print("-----------------------------------")
    print(f"Official docs directory: {OFFICIAL_DOCS_DIR}")
    print(f"Output chunks path:      {OUTPUT_CHUNKS_PATH}")

    documents = load_documents_from_directory(str(OFFICIAL_DOCS_DIR))

    print(f"\nDocuments loaded: {len(documents)}")

    if not documents:
        print("\nNo documents found.")
        print("Add .txt, .md, or .pdf files to:")
        print(OFFICIAL_DOCS_DIR)
        return

    chunks = chunk_documents(
        documents=documents,
        chunk_size_words=450,
        overlap_words=75,
    )

    save_chunks_jsonl(
        chunks=chunks,
        output_path=str(OUTPUT_CHUNKS_PATH),
    )

    print(f"Chunks created: {len(chunks)}")
    print(f"Saved to: {OUTPUT_CHUNKS_PATH}")

    print("\nPreview of first chunk:")
    first_chunk = chunks[0]
    print("-----------------------------------")
    print("Chunk ID:", first_chunk.chunk_id)
    print("Title:", first_chunk.metadata.get("title", ""))
    print("Text preview:")
    print(first_chunk.text[:700])


if __name__ == "__main__":
    main()