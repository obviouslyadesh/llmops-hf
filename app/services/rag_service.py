from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from app.services.langfuse_service import LangfuseService
from app.services.qdrant_service import QdrantService


class RAGService:
    """
    Orchestrates the full RAG pipeline.
    EmbeddingService is cheap to instantiate now — it holds no model weights.
    The actual model lives in app.core.models and is shared process-wide.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.gemini_service = GeminiService()
        self.langfuse_service = LangfuseService()

    def answer_question(self, question: str) -> dict:
        query_vector = self.embedding_service.embed_text(question)
        results = self.qdrant_service.search(query_vector)

        contexts = []
        sources = []

        for hit in results:
            contexts.append(hit.payload["text"])
            sources.append(hit.payload["source"])

        context_text = "\n\n".join(contexts)

        answer = self.gemini_service.generate_answer(
            question,
            context_text,
        )

        self.langfuse_service.trace_chat(
            question=question,
            context=context_text,
            answer=answer,
        )

        return {
            "answer": answer,
            "sources": list(set(sources)),
        }
