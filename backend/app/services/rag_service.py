from typing import List

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
    - convert them into SourceSnippet objects
    """

    def __init__(self):
        self.vector_store = ChromaVectorStore()

    def retrieve_sources(self, query: str, top_k: int = None) -> List[SourceSnippet]:
        results: List[VectorSearchResult] = self.vector_store.search(
            query=query,
            top_k=top_k or settings.rag_top_k,
        )

        sources: List[SourceSnippet] = []

        for result in results:
            if result.score is not None and result.score < settings.rag_min_score:
                continue

            title = result.metadata.get("title", "Unknown Source")
            source_type = result.metadata.get("source_type", "official_document")
            url = result.metadata.get("url", "")

            sources.append(
                SourceSnippet(
                    title=title,
                    source_type=source_type,
                    url=url,
                    text=result.text,
                    score=result.score,
                )
            )

        return sources