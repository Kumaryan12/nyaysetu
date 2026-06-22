import sys
from pathlib import Path

# Allows this script to import from app/ when run from backend/
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

from app.services.chunker import load_chunks_jsonl
from app.services.vector_store import ChromaVectorStore


CHUNKS_PATH = BACKEND_ROOT / "app" / "data" / "processed" / "chunks.jsonl"


def main() -> None:
    print("NyayaSetu vector index builder")
    print("------------------------------")
    print(f"Chunks path: {CHUNKS_PATH}")

    if not CHUNKS_PATH.exists():
        print("\nchunks.jsonl not found.")
        print("Run this first:")
        print("python scripts/prepare_chunks.py")
        return

    chunks = load_chunks_jsonl(str(CHUNKS_PATH))

    print(f"\nChunks loaded: {len(chunks)}")

    if not chunks:
        print("No chunks found. Add official documents and rebuild chunks.")
        return

    vector_store = ChromaVectorStore()

    print("\nResetting Chroma collection...")
    vector_store.reset_collection()

    print("Adding chunks to vector database...")
    vector_store.add_chunks(chunks)

    print("\nVector index built successfully.")
    print(f"Chunks in vector DB: {vector_store.count()}")


if __name__ == "__main__":
    main()