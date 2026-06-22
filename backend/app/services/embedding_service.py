from typing import List

from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingService:

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model_name
        self.model = SentenceTransformer(self.model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:

        if not texts:
            return []

        prepared_texts = [
            "passage: " + text.strip()
            for text in texts
        ]

        embeddings = self.model.encode(
            prepared_texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        prepared_query = "query: " + query.strip()

        embedding = self.model.encode(
            prepared_query,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embedding.tolist()