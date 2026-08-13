"""
AI Job Hunter - Embedding Model Wrapper

Provides a unified interface to the sentence-transformers embedding model
for use with ChromaDB and LangChain.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("vectorstore.embeddings")


class EmbeddingModel:
    """Wrapper around sentence-transformers for generating text embeddings.

    Uses the model specified in settings (default: all-MiniLM-L6-v2).
    Lazy-loads the model on first use to avoid slow import at startup.
    """

    def __init__(self) -> None:
        self._model = None
        self._model_name = get_settings().embedding_model

    def _load_model(self) -> None:
        """Lazy-load the sentence-transformers model."""
        if self._model is None:
            logger.info("Loading embedding model", model=self._model_name)
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded successfully")

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding vector for a single text string.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        self._load_model()
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        self._load_model()
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """Get the embedding dimension size.

        Returns:
            The dimension of the embedding vectors (e.g., 384 for MiniLM).
        """
        self._load_model()
        return self._model.get_sentence_embedding_dimension()


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    """Get a cached embedding model singleton.

    Returns:
        The EmbeddingModel instance.
    """
    return EmbeddingModel()
