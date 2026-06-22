from functools import lru_cache

from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from app.services.qdrant_service import QdrantService
from app.services.rag_service import RAGService


@lru_cache
def get_embedding_service():
    return EmbeddingService()


@lru_cache
def get_qdrant_service():
    return QdrantService()


@lru_cache
def get_gemini_service():
    return GeminiService()


@lru_cache
def get_rag_service():
    return RAGService()
