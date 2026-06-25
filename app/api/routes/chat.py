from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.core.logger import logger
from app.services.rag_service import RAGService

router = APIRouter()

rag_service = RAGService()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):
    """Standard chat — returns complete answer at once."""
    logger.info(f"Question: {request.question}")

    try:
        response = rag_service.answer_question(request.question)
        logger.info("Answer generated successfully")
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(
            status_code=503,
            content={"detail": "Service temporarily unavailable. Please try again."},
        )


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    """
    Streaming chat — returns tokens via Server-Sent Events.
    Frontend consumes this with EventSource or fetch + ReadableStream.
    """
    logger.info(f"Stream question: {request.question}")

    return StreamingResponse(
        rag_service.stream_answer(request.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disables nginx buffering on HF Spaces
        },
    )