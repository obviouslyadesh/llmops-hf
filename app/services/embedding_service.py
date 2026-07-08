import logging
import time

from app.core.models import embedding_model
from app.monitoring.metrics import (
    EMBEDDING_DURATION_SECONDS,
    EMBEDDING_FAILURES_TOTAL,
    EMBEDDING_REQUESTS_TOTAL,
)

logger = logging.getLogger("llmops")


class EmbeddingService:
    """
    Stateless wrapper around the shared embedding model.

    The embedding model is loaded once in app.core.models.
    This service only performs inference and records Prometheus metrics.
    """

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        EMBEDDING_REQUESTS_TOTAL.inc()

        start = time.perf_counter()

        try:
            embedding = embedding_model.encode(
                text,
                normalize_embeddings=True,
            )

            EMBEDDING_DURATION_SECONDS.observe(
                time.perf_counter() - start
            )

            return embedding.tolist()

        except Exception:
            EMBEDDING_FAILURES_TOTAL.inc()
            logger.exception("Embedding generation failed")
            raise

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        EMBEDDING_REQUESTS_TOTAL.inc()

        start = time.perf_counter()

        try:
            embeddings = embedding_model.encode(
                texts,
                normalize_embeddings=True,
            )

            EMBEDDING_DURATION_SECONDS.observe(
                time.perf_counter() - start
            )

            return embeddings.tolist()

        except Exception:
            EMBEDDING_FAILURES_TOTAL.inc()
            logger.exception("Batch embedding generation failed")
            raise