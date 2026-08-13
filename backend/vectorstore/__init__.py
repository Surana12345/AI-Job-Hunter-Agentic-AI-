"""
AI Job Hunter - VectorStore Package

ChromaDB vector store for resume and job description embeddings.
"""

from backend.vectorstore.client import get_chroma_client
from backend.vectorstore.embeddings import EmbeddingModel, get_embedding_model
from backend.vectorstore.collections import (
    VectorCollection,
    get_jobs_collection,
    get_resume_collection,
)

__all__ = [
    "get_chroma_client",
    "EmbeddingModel",
    "get_embedding_model",
    "VectorCollection",
    "get_jobs_collection",
    "get_resume_collection",
]
