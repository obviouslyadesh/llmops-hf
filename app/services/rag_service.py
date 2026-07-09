import json
import logging
import os
import time
from collections.abc import Generator

from app.monitoring.metrics import (
    RAG_CHUNKS_RETRIEVED,
    RAG_GENERATION_DURATION_SECONDS,
    RAG_QUERIES_TOTAL,
    RAG_RERANKER_DURATION_SECONDS,
    RAG_RERANKER_REQUESTS_TOTAL,
    RAG_RETRIEVAL_DURATION_SECONDS,
)
from app.services.embedding_service import EmbeddingService
from app.services.langfuse_service import LangfuseService
from app.services.qdrant_service import QdrantService

logger = logging.getLogger("llmops")


def _get_llm_service():
    """
    Returns the configured LLM service.

    Environment:
        LLM_PROVIDER=groq
        LLM_PROVIDER=gemini
    """

    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "gemini":
        from app.services.gemini_service import GeminiService

        logger.info("Using Gemini LLM")
        return GeminiService()

    from app.services.groq_service import GroqService

    logger.info("Using Groq LLM")
    return GroqService()


class RAGService:
    """
    Complete Retrieval-Augmented Generation pipeline.

    User Question
          ↓
      Embedding
          ↓
      Vector Search (Qdrant)
          ↓
     (Optional Reranker)
          ↓
      Selected Context
          ↓
       LLM Generation
          ↓
      Langfuse Trace
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.llm_service = _get_llm_service()
        self.langfuse_service = LangfuseService()

    def _retrieve(
        self,
        question: str,
        use_reranker: bool = False,
    ) -> tuple[list[str], list[str], float]:
        """
        Retrieve relevant chunks from Qdrant.

        Returns:
            contexts
            sources
            retrieval_ms
        """

        retrieval_start = time.perf_counter()

        query_vector = self.embedding_service.embed_text(question)

        results = self.qdrant_service.search(query_vector)

        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        # Prometheus metric
        RAG_RETRIEVAL_DURATION_SECONDS.observe(retrieval_ms / 1000)

        contexts = [hit.payload["text"] for hit in results]

        sources = [hit.payload["source"] for hit in results]

        # Number of retrieved chunks
        RAG_CHUNKS_RETRIEVED.observe(len(contexts))

        if use_reranker and contexts:
            RAG_RERANKER_REQUESTS_TOTAL.inc()

            rerank_start = time.perf_counter()

            logger.info("Applying cross-encoder reranking")

            from app.services.reranker import rerank

            contexts = rerank(
                query=question,
                chunks=contexts,
                top_k=3,
            )

            RAG_RERANKER_DURATION_SECONDS.observe(time.perf_counter() - rerank_start)

        return contexts, sources, retrieval_ms

    def answer_question(
        self,
        question: str,
        rerank_enabled: bool = False,
    ) -> dict:
        """
        Standard RAG endpoint.
        """

        RAG_QUERIES_TOTAL.inc()

        contexts, sources, retrieval_ms = self._retrieve(
            question=question,
            use_reranker=rerank_enabled,
        )

        context_text = "\n\n".join(contexts)

        generation_start = time.perf_counter()

        answer, usage, generation_ms = self.llm_service.generate_answer(
            question=question,
            context=context_text,
        )

        if generation_ms is None:
            generation_ms = (time.perf_counter() - generation_start) * 1000

        # Prometheus metric
        RAG_GENERATION_DURATION_SECONDS.observe(generation_ms / 1000)

        try:
            self.langfuse_service.trace_chat(
                question=question,
                context=context_text,
                answer=answer,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
                usage=usage,
            )
        except Exception as e:
            logger.warning(f"Langfuse trace failed: {e}")

        return {
            "answer": answer,
            "contexts": contexts,
            "sources": sorted(list(set(sources))),
        }

    def stream_answer(
        self,
        question: str,
        rerank_enabled: bool = False,
    ) -> Generator[str, None, None]:
        """
        Streaming endpoint using Server-Sent Events.
        """

        RAG_QUERIES_TOTAL.inc()

        contexts, sources, retrieval_ms = self._retrieve(
            question=question,
            use_reranker=rerank_enabled,
        )

        context_text = "\n\n".join(contexts)

        yield (f"data: {json.dumps({'sources': sorted(list(set(sources)))})}\n\n")

        answer_parts = []

        generation_start = time.perf_counter()

        for chunk in self.llm_service.stream_answer(
            question=question,
            context=context_text,
        ):
            answer_parts.append(chunk)
            yield f"data: {json.dumps({'token': chunk})}\n\n"

        generation_ms = (time.perf_counter() - generation_start) * 1000

        # Prometheus metric
        RAG_GENERATION_DURATION_SECONDS.observe(generation_ms / 1000)

        final_answer = "".join(answer_parts)

        try:
            self.langfuse_service.trace_chat(
                question=question,
                context=context_text,
                answer=final_answer,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
                usage=None,
            )
        except Exception as e:
            logger.warning(f"Langfuse streaming trace failed: {e}")

        yield "data: [DONE]\n\n"
