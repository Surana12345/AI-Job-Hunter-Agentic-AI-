"""
AI Job Hunter - ChromaDB Client Singleton

Provides a persistent ChromaDB client for vector storage operations.
"""

from __future__ import annotations

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("vectorstore.client")


@lru_cache
def get_chroma_client() -> chromadb.ClientAPI:
    """Get a cached, persistent ChromaDB client.

    The client persists data to disk at the configured path,
    allowing embeddings to survive server restarts.

    Returns:
        A persistent ChromaDB client instance.
    """
    settings = get_settings()

    logger.info("Initializing ChromaDB client", persist_dir=settings.chroma_persist_dir)

    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True,
        ),
    )

    logger.info("ChromaDB client initialized successfully")
    return client
