"""
AI Job Hunter - Vector Store Tools

LangChain tools for ChromaDB operations — querying similar resumes,
storing embeddings, and retrieving documents.
"""

from __future__ import annotations

from typing import Any

from backend.utils.logger import get_logger
from backend.vectorstore.collections import get_jobs_collection, get_resume_collection

logger = get_logger("agents.tools.vector")


async def store_resume_embedding(
    resume_id: str,
    resume_text: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Store a resume's text embedding in ChromaDB.

    Args:
        resume_id: Unique identifier for the resume.
        resume_text: The full resume text to embed.
        metadata: Optional metadata (user_id, skills, etc.).
    """
    collection = get_resume_collection()
    collection.add_documents(
        ids=[resume_id],
        documents=[resume_text],
        metadatas=[metadata or {}],
    )
    logger.info("Resume embedding stored", resume_id=resume_id)


async def query_similar_resumes(
    query_text: str,
    n_results: int = 5,
) -> list[dict[str, Any]]:
    """Find resumes similar to the given text.

    Args:
        query_text: Text to search for (e.g., a job description).
        n_results: Number of results to return.

    Returns:
        List of dicts with id, document, metadata, and distance.
    """
    collection = get_resume_collection()
    results = collection.query(query_text=query_text, n_results=n_results)

    output = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            output.append({
                "id": doc_id,
                "document": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })

    return output


async def store_job_embedding(
    job_id: str,
    job_text: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Store a job description's text embedding in ChromaDB.

    Args:
        job_id: Unique identifier for the job.
        job_text: The full job description text to embed.
        metadata: Optional metadata (company, title, location, etc.).
    """
    collection = get_jobs_collection()
    collection.add_documents(
        ids=[job_id],
        documents=[job_text],
        metadatas=[metadata or {}],
    )
    logger.info("Job embedding stored", job_id=job_id)


async def query_similar_jobs(
    query_text: str,
    n_results: int = 10,
) -> list[dict[str, Any]]:
    """Find jobs similar to the given text.

    Args:
        query_text: Text to search for (e.g., resume skills summary).
        n_results: Number of results to return.

    Returns:
        List of dicts with id, document, metadata, and distance.
    """
    collection = get_jobs_collection()
    results = collection.query(query_text=query_text, n_results=n_results)

    output = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            output.append({
                "id": doc_id,
                "document": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })

    return output
