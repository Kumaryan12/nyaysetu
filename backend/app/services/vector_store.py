from pathlib import Path
from typing import Dict, List, Optional

import chromadb

from app.config import settings
from app.services.chunker import DocumentChunk
from app.services.embedding_service import EmbeddingService


class VectorSearchResult:

    def __init__(
        self,
        chunk_id: str,
        text: str,
        metadata: Dict[str, str],
        distance: Optional[float],
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.metadata = metadata
        self.distance = distance

        if distance is None:
            self.score = None
        else:
            # For cosine distance in Chroma, lower distance is better.
            # A rough relevance score can be represented as 1 - distance.
            self.score = 1.0 - float(distance)


class ChromaVectorStore:

    def __init__(self):
        db_path = Path(settings.chroma_db_path)
        db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(db_path))

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        self.embedding_service = EmbeddingService()

    def reset_collection(self) -> None:

        try:
            self.client.delete_collection(settings.chroma_collection_name)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: List[DocumentChunk], batch_size: int = 32) -> None:

        if not chunks:
            return

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]

            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.text for chunk in batch]

            metadatas = []
            for chunk in batch:
                clean_metadata = {}

                for key, value in chunk.metadata.items():
                    if value is None:
                        clean_metadata[key] = ""
                    else:
                        clean_metadata[key] = str(value)

                metadatas.append(clean_metadata)

            embeddings = self.embedding_service.embed_documents(documents)

            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )

    def search(self, query: str, top_k: int = None) -> List[VectorSearchResult]:

        top_k = top_k or settings.rag_top_k

        query_embedding = self.embedding_service.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        output: List[VectorSearchResult] = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, text, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            output.append(
                VectorSearchResult(
                    chunk_id=chunk_id,
                    text=text,
                    metadata=metadata or {},
                    distance=distance,
                )
            )

        return output

    def count(self) -> int:

        return self.collection.count()