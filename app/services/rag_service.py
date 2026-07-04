import json
import logging
import os
import time
from collections.abc import Generator

from app.services.embedding_service import EmbeddingService
from app.services.langfuse_service import LangfuseService
from app.services.qdrant_service import QdrantService

logger = logging.getLogger("llmops")


def _get_llm_service():
    """
    Returns the configured LLM service.

    Environment:
        LLM_PROVIDER=groq      (default)
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
    Complete RAG pipeline.

    Flow

    User Question
          ↓
      Embedding
          ↓
       Qdrant Search
          ↓
      (Optional Reranker)
          ↓
        Selected Contexts
          ↓
         LLM (Groq/Gemini)
          ↓
          Answer
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

        start = time.time()

        query_vector = self.embedding_service.embed_text(question)

        results = self.qdrant_service.search(query_vector)

        retrieval_ms = (time.time() - start) * 1000

        contexts = [hit.payload["text"] for hit in results]
        sources = [hit.payload["source"] for hit in results]

        if use_reranker and contexts:
            logger.info("Applying cross-encoder reranking")

            from app.services.reranker import rerank

            contexts = rerank(
                query=question,
                chunks=contexts,
                top_k=3,
            )

        return contexts, sources, retrieval_ms

    def answer_question(
        self,
        question: str,
        rerank_enabled: bool = False,
    ) -> dict:
        """
        Standard (non-streaming) RAG endpoint.

        Returns:
            answer
            contexts
            sources
        """

        contexts, sources, retrieval_ms = self._retrieve(
            question=question,
            use_reranker=rerank_enabled,
        )

        context_text = "\n\n".join(contexts)

        generation_start = time.time()

        answer, usage, generation_ms = self.llm_service.generate_answer(
            question=question,
            context=context_text,
        )

        if generation_ms is None:
            generation_ms = (time.time() - generation_start) * 1000

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
        Streaming endpoint using Server Sent Events.
        """

        contexts, sources, retrieval_ms = self._retrieve(
            question=question,
            use_reranker=rerank_enabled,
        )

        context_text = "\n\n".join(contexts)

        yield (f"data: {json.dumps({'sources': sorted(list(set(sources)))})}\n\n")

        answer_parts = []

        generation_start = time.time()

        for chunk in self.llm_service.stream_answer(
            question=question,
            context=context_text,
        ):
            answer_parts.append(chunk)

            yield f"data: {json.dumps({'token': chunk})}\n\n"

        generation_ms = (time.time() - generation_start) * 1000

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
