import time
from collections.abc import Generator

from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from app.services.langfuse_service import LangfuseService
from app.services.qdrant_service import QdrantService


class RAGService:
    """
    Orchestrates the full RAG pipeline.
    EmbeddingService is cheap to instantiate — model lives in app.core.models.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.gemini_service = GeminiService()
        self.langfuse_service = LangfuseService()

    def _retrieve(self, question: str) -> tuple[list[str], list[str], float]:
        """
        Embed question, search Qdrant.
        Returns (contexts, sources, retrieval_ms).
        """
        t0 = time.time()
        query_vector = self.embedding_service.embed_text(question)
        results = self.qdrant_service.search(query_vector)
        retrieval_ms = (time.time() - t0) * 1000

        contexts = [hit.payload["text"] for hit in results]
        sources = [hit.payload["source"] for hit in results]

        return contexts, sources, retrieval_ms

    def answer_question(self, question: str) -> dict:
        """
        Full RAG pipeline — returns complete answer with sources.
        Traces to Langfuse with per-step latency and token usage.
        """
        contexts, sources, retrieval_ms = self._retrieve(question)
        context_text = "\n\n".join(contexts)

        answer, usage, generation_ms = self.gemini_service.generate_answer(
            question,
            context_text,
        )

        self.langfuse_service.trace_chat(
            question=question,
            context=context_text,
            answer=answer,
            retrieval_ms=retrieval_ms,
            generation_ms=generation_ms,
            usage=usage,
        )

        return {
            "answer": answer,
            "sources": list(set(sources)),
        }

    def stream_answer(self, question: str) -> Generator[str, None, None]:
        """
        Streaming RAG pipeline — yields tokens as Gemini generates them.
        Retrieval is done upfront (blocking), then generation streams.
        Note: Langfuse tracing is skipped for streaming (no final answer to trace).
        """
        contexts, sources, _ = self._retrieve(question)
        context_text = "\n\n".join(contexts)

        # Yield sources first as a JSON header so the frontend knows the sources
        import json
        yield f"data: {json.dumps({'sources': list(set(sources))})}\n\n"

        # Stream answer tokens
        for chunk in self.gemini_service.stream_answer(question, context_text):
            yield f"data: {json.dumps({'token': chunk})}\n\n"

        # Signal stream end
        yield "data: [DONE]\n\n"