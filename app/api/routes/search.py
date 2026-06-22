from fastapi import APIRouter
from pydantic import BaseModel

from app.core.logger import logger
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

router = APIRouter()

# Instantiated once at module load — EmbeddingService no longer
# loads a model itself, so this is now a cheap stateless object.
embedding_service = EmbeddingService()
qdrant_service = QdrantService()


class SearchRequest(BaseModel):
    query: str


@router.post("/search")
def search_documents(request: SearchRequest):
    logger.info(f"Search query: {request.query}")

    query_vector = embedding_service.embed_text(request.query)
    results = qdrant_service.search(query_vector)

    logger.info(f"Retrieved {len(results)} chunks")

    return {
        "results": [
            {
                "score": hit.score,
                "text": hit.payload["text"],
                "source": hit.payload["source"],
            }
            for hit in results
        ]
    }
