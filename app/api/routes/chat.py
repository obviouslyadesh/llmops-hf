from fastapi import APIRouter
from pydantic import BaseModel

from app.core.logger import logger
from app.services.rag_service import RAGService

router = APIRouter()

# Module-level singleton. RAGService.__init__ is now cheap because
# EmbeddingService no longer loads model weights — the singleton
# in app.core.models does that once.
rag_service = RAGService()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):
    logger.info(f"Question: {request.question}")

    response = rag_service.answer_question(request.question)

    logger.info("Answer generated successfully")

    return response
