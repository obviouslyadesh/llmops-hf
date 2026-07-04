import time

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings
from app.core.logger import logger


class QdrantService:
    COLLECTION_NAME = "documents"

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )
        self._wait_for_qdrant()
        self._create_collection()

    def _wait_for_qdrant(self, retries: int = 10, delay: float = 2.0):
        """Wait for Qdrant to be ready before proceeding."""
        for attempt in range(retries):
            try:
                self.client.get_collections()
                logger.info("Qdrant is ready")
                return
            except Exception:
                logger.warning(
                    f"Qdrant not ready, attempt {attempt + 1}/{retries}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
        raise RuntimeError(
            f"Qdrant unavailable at {settings.QDRANT_URL} after {retries} attempts"
        )

    def _create_collection(self):
        collections = self.client.get_collections()
        names = [c.name for c in collections.collections]

        if self.COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

    def insert_chunks(self, points):
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

    def search(self, vector, limit=5):
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=limit,
        )
        return results.points
