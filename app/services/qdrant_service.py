import time

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings
from app.core.logger import logger
from app.monitoring.metrics import (
    QDRANT_INSERT_DURATION_SECONDS,
    QDRANT_INSERT_REQUESTS_TOTAL,
    QDRANT_POINTS_TOTAL,
    QDRANT_SEARCH_DURATION_SECONDS,
    QDRANT_SEARCH_REQUESTS_TOTAL,
)


class QdrantService:
    COLLECTION_NAME = "documents"

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )

        self._wait_for_qdrant()
        self._create_collection()

    def _wait_for_qdrant(
        self,
        retries: int = 10,
        delay: float = 2.0,
    ):
        """
        Wait until Qdrant becomes available.
        """

        for attempt in range(retries):
            try:
                self.client.get_collections()
                logger.info("Qdrant is ready")
                return

            except Exception:
                logger.warning(
                    f"Qdrant not ready "
                    f"({attempt + 1}/{retries}), "
                    f"retrying in {delay}s..."
                )

                time.sleep(delay)

        raise RuntimeError(
            f"Qdrant unavailable at "
            f"{settings.QDRANT_URL}"
        )

    def _create_collection(self):
        collections = self.client.get_collections()

        names = [
            collection.name
            for collection in collections.collections
        ]

        if self.COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

    def insert_chunks(self, points):
        """
        Insert vectors into Qdrant.
        """

        QDRANT_INSERT_REQUESTS_TOTAL.inc()

        start = time.perf_counter()

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

        QDRANT_INSERT_DURATION_SECONDS.observe(
            time.perf_counter() - start
        )

        try:
            collection = self.client.get_collection(
                self.COLLECTION_NAME
            )

            QDRANT_POINTS_TOTAL.set(
                collection.points_count
            )

        except Exception:
            logger.warning(
                "Unable to update Qdrant vector count metric."
            )

    def search(
        self,
        vector,
        limit: int = 5,
    ):
        """
        Search similar vectors.
        """

        QDRANT_SEARCH_REQUESTS_TOTAL.inc()

        start = time.perf_counter()

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=limit,
        )

        QDRANT_SEARCH_DURATION_SECONDS.observe(
            time.perf_counter() - start
        )

        return results.points