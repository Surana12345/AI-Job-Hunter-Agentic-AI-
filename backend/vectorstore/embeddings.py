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


    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two normalized vectors."""
        if not vec1 or not vec2:
            return 0.0
        # If normalized, dot product equals cosine similarity
        return max(0.0, min(1.0, sum(a * b for a, b in zip(vec1, vec2))))

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic cosine similarity between two text strings."""
        if not text1.strip() or not text2.strip():
            return 0.0
        v1 = self.embed_text(text1)
        v2 = self.embed_text(text2)
        return self.cosine_similarity(v1, v2)

    def pre_filter_jobs(
        self,
        candidate_summary: str,
        jobs: List[dict],
        threshold: float = 0.65,
    ) -> List[dict]:
        """Module 1 Two-Tier Vector Pre-filtering.

        Pre-filter out jobs below similarity threshold (default 0.65)
        to reduce downstream LLM token costs by over 75%.
        """
        if not candidate_summary or not jobs:
            return jobs

        candidate_vec = self.embed_text(candidate_summary)
        filtered_jobs = []

        for job in jobs:
            # Combine title, description snippet, and skills
            job_text = f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')[:500]}"
            job_vec = self.embed_text(job_text)
            sim = self.cosine_similarity(candidate_vec, job_vec)
            job["vector_similarity"] = round(sim, 4)
            if sim >= threshold:
                job["pre_filter_passed"] = True
                filtered_jobs.append(job)
            else:
                job["pre_filter_passed"] = False

        logger.info(
            "Two-tier vector pre-filtering completed",
            total=len(jobs),
            passed=len(filtered_jobs),
            threshold=threshold,
        )
        # If too restrictive, return top candidates
        if not filtered_jobs and jobs:
            sorted_jobs = sorted(jobs, key=lambda x: x.get("vector_similarity", 0), reverse=True)
            return sorted_jobs[:max(1, len(jobs) // 2)]
        return filtered_jobs


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    """Get a cached embedding model singleton.

    Returns:
        The EmbeddingModel instance.
    """
    return EmbeddingModel()

