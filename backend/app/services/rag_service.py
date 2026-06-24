from typing import List, Optional

from app.config import settings
from app.models.schemas import SourceSnippet
from app.services.vector_store import ChromaVectorStore, VectorSearchResult


class RAGService:
    """
    High-level RAG retrieval service.

    Responsibility:
    - take user query
    - retrieve relevant official chunks
    - filter weak results
    - preserve source metadata
    - convert retrieved chunks into SourceSnippet objects
    """

    def __init__(self):
        self.vector_store = ChromaVectorStore()

    def retrieve_sources(self, query: str, top_k: Optional[int] = None) -> List[SourceSnippet]:
        results: List[VectorSearchResult] = self.vector_store.search(
            query=query,
            top_k=top_k or settings.rag_top_k,
        )

        sources: List[SourceSnippet] = []

        for result in results:
            if result.score is not None and result.score < settings.rag_min_score:
                continue

            metadata = result.metadata or {}

            title = metadata.get("title", "Unknown Source")
            source_type = metadata.get("source_type", "official_document")
            url = metadata.get("url", "")
            domain = metadata.get("domain")
            publisher = metadata.get("publisher")
            jurisdiction = metadata.get("jurisdiction")

            sources.append(
                SourceSnippet(
                    title=title,
                    source_type=source_type,
                    url=url,
                    domain=domain,
                    publisher=publisher,
                    jurisdiction=jurisdiction,
                    text=result.text,
                    score=result.score,
                )
            )

        return sources