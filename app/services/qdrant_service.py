from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from app.core.config import settings


class QdrantService:
    COLLECTION_NAME = "documents"

    def __init__(self):

        self.client = QdrantClient(url=settings.QDRANT_URL)

        self._create_collection()

    def _create_collection(self):

        collections = self.client.get_collections()

        names = [collection.name for collection in collections.collections]

        if self.COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def insert_chunks(self, points):
        self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)

    def search(self, vector, limit=5):
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME, query=vector, limit=limit
        )

        return results.points
