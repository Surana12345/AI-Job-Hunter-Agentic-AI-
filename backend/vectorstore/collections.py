"""
AI Job Hunter - ChromaDB Collection Management

Creates and manages ChromaDB collections for resumes and jobs,
with helper methods for adding, querying, and deleting documents.
"""

from __future__ import annotations

from typing import Any, List

from backend.config import get_settings
from backend.utils.logger import get_logger
from backend.vectorstore.client import get_chroma_client
from backend.vectorstore.embeddings import get_embedding_model

logger = get_logger("vectorstore.collections")


class VectorCollection:
    """Manages a single ChromaDB collection with embedding support.

    Provides add, query, get, and delete operations with automatic
    embedding generation via sentence-transformers.
    """

    def __init__(self, collection_name: str) -> None:
        self._client = get_chroma_client()
        self._embedding_model = get_embedding_model()
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._name = collection_name

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[dict[str, Any]] | None = None,
    ) -> None:
        """Add documents to the collection with auto-generated embeddings.

        Args:
            ids: Unique identifiers for each document.
            documents: Text content of each document.
            metadatas: Optional metadata dicts for each document.
        """
        embeddings = self._embedding_model.embed_texts(documents)

        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info(
            "Documents added to collection",
            collection=self._name,
            count=len(ids),
        )

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict:
        """Query the collection for similar documents.

        Args:
            query_text: The text to search for.
            n_results: Number of results to return.
            where: Optional metadata filter.

        Returns:
            Dict with keys: ids, documents, metadatas, distances.
        """
        query_embedding = self._embedding_model.embed_text(query_text)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        return results

    def get_by_id(self, doc_id: str) -> dict | None:
        """Retrieve a specific document by its ID.

        Args:
            doc_id: The document ID.

        Returns:
            Dict with document data, or None if not found.
        """
        result = self._collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"],
        )

        if not result["ids"]:
            return None

        return {
            "id": result["ids"][0],
            "document": result["documents"][0],
            "metadata": result["metadatas"][0] if result["metadatas"] else {},
        }

    def delete_by_id(self, doc_id: str) -> None:
        """Delete a document from the collection.

        Args:
            doc_id: The document ID to delete.
        """
        self._collection.delete(ids=[doc_id])
        logger.info("Document deleted", collection=self._name, doc_id=doc_id)

    def count(self) -> int:
        """Get the total number of documents in the collection.

        Returns:
            Document count.
        """
        return self._collection.count()

    def clear(self) -> None:
        """Delete all documents from the collection."""
        client = get_chroma_client()
        client.delete_collection(self._name)
        self._collection = client.get_or_create_collection(
            name=self._name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning("Collection cleared", collection=self._name)


def get_resume_collection() -> VectorCollection:
    """Get the resumes vector collection.

    Returns:
        VectorCollection for resume embeddings.
    """
    settings = get_settings()
    return VectorCollection(settings.chroma_collection_resumes)


def get_jobs_collection() -> VectorCollection:
    """Get the jobs vector collection.

    Returns:
        VectorCollection for job description embeddings.
    """
    settings = get_settings()
    return VectorCollection(settings.chroma_collection_jobs)
