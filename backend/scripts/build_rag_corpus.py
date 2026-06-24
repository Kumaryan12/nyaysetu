import shutil
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]

OFFICIAL_CLEAN_DIR = BACKEND_ROOT / "app" / "data" / "official_docs_clean"
MANUAL_DOCS_DIR = BACKEND_ROOT / "app" / "data" / "manual_docs"
RAG_DOCS_DIR = BACKEND_ROOT / "app" / "data" / "rag_docs"


def clear_rag_docs() -> None:
    RAG_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    for path in RAG_DOCS_DIR.glob("*"):
        if path.is_file():
            path.unlink()


def copy_docs_from(source_dir: Path, source_label: str) -> int:
    if not source_dir.exists():
        print(f"Skipping missing directory: {source_dir}")
        return 0

    copied = 0

    for path in sorted(source_dir.glob("*")):
        if not path.is_file():
            continue

        if path.suffix not in {".txt", ".md", ".json"}:
            continue

        destination = RAG_DOCS_DIR / path.name
        shutil.copy2(path, destination)
        copied += 1

    print(f"Copied {copied} files from {source_label}: {source_dir}")
    return copied


def main() -> None:
    print("NyayaSetu RAG corpus builder")
    print("----------------------------")
    print("Official clean dir:", OFFICIAL_CLEAN_DIR)
    print("Manual docs dir:    ", MANUAL_DOCS_DIR)
    print("RAG docs dir:       ", RAG_DOCS_DIR)

    clear_rag_docs()

    official_count = copy_docs_from(
        source_dir=OFFICIAL_CLEAN_DIR,
        source_label="official cleaned docs",
    )

    manual_count = copy_docs_from(
        source_dir=MANUAL_DOCS_DIR,
        source_label="manual curated docs",
    )

    txt_count = len(list(RAG_DOCS_DIR.glob("*.txt")))
    metadata_count = len(list(RAG_DOCS_DIR.glob("*.metadata.json")))

    print("\nDone.")
    print("Official files copied:", official_count)
    print("Manual files copied:  ", manual_count)
    print("Final .txt docs:      ", txt_count)
    print("Final metadata files: ", metadata_count)

    if txt_count == 0:
        print("\nWARNING: No text documents found in final RAG corpus.")


if __name__ == "__main__":
    main()