from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.core.logger import logger
from app.services.rag_service import RAGService

router = APIRouter()

rag_service = RAGService()


class ChatRequest(BaseModel):
    question: str
    rerank: bool = False


@router.post("/chat")
def chat(request: ChatRequest):
    """
    Standard chat endpoint.

    Returns:
    {
        "answer": "...",
        "contexts": [...],
        "sources": [...]
    }

    rerank=False -> baseline retrieval
    rerank=True  -> retrieval + cross-encoder reranking
    """
    logger.info(f"Question: {request.question} | rerank={request.rerank}")

    try:
        response = rag_service.answer_question(
            question=request.question,
            rerank_enabled=request.rerank,
        )

        logger.info("Answer generated successfully")

        return response

    except Exception as e:
        logger.exception(f"Chat error: {e}")

        return JSONResponse(
            status_code=503,
            content={"detail": "Service temporarily unavailable. Please try again."},
        )


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint.

    Streams tokens via Server-Sent Events (SSE).

    Supports optional reranking.
    """

    logger.info(f"Stream question: {request.question} | rerank={request.rerank}")

    return StreamingResponse(
        rag_service.stream_answer(
            question=request.question,
            rerank_enabled=request.rerank,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
