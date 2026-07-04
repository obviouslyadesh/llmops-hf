from functools import lru_cache

from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from app.services.qdrant_service import QdrantService
from app.services.rag_service import RAGService, _get_llm_service


@lru_cache
def get_embedding_service():
    return EmbeddingService()


@lru_cache
def get_qdrant_service():
    return QdrantService()


@lru_cache
def get_gemini_service():
    """Kept for backward compatibility — use get_llm_service() for new code."""
    return GeminiService()


@lru_cache
def get_llm_service():
    """Returns Groq or Gemini depending on LLM_PROVIDER env var."""
    return _get_llm_service()


@lru_cache
def get_rag_service():
    return RAGService()
