import sys
from pathlib import Path

# Allows this script to import from app/ when run from backend/
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

from app.services.vector_store import ChromaVectorStore


def main() -> None:
    print("NyayaSetu retrieval test")
    print("-----------------------")

    query = input("\nEnter a test query: ").strip()

    if not query:
        print("Empty query. Exiting.")
        return

    vector_store = ChromaVectorStore()

    print("\nSearching...")
    results = vector_store.search(query=query, top_k=5)

    if not results:
        print("No results found.")
        return

    print(f"\nTop {len(results)} results:")

    for index, result in enumerate(results, start=1):
        print("\n" + "=" * 80)
        print(f"Result {index}")
        print("-" * 80)
        print("Title:", result.metadata.get("title", "Unknown"))
        print("Source type:", result.metadata.get("source_type", ""))
        print("URL:", result.metadata.get("url", ""))
        print("Distance:", result.distance)
        print("Score:", result.score)
        print("\nText preview:")
        print(result.text[:1000])


if __name__ == "__main__":
    main()