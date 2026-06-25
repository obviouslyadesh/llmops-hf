import time

from langfuse import Langfuse

from app.core.config import settings


class LangfuseService:
    def __init__(self):
        self.client = Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )

    def trace_chat(
        self,
        question: str,
        context: str,
        answer: str,
        retrieval_ms: float = 0.0,
        generation_ms: float = 0.0,
        usage: dict | None = None,
    ):
        try:
            trace = self.client.trace(
                name="rag-chat",
                input={"question": question},
                output=answer,
                metadata={
                    "retrieval_ms": round(retrieval_ms, 2),
                    "generation_ms": round(generation_ms, 2),
                    "total_ms": round(retrieval_ms + generation_ms, 2),
                },
            )

            # Retrieval span — how long vector search took
            trace.span(
                name="retrieval",
                input={"question": question},
                output={"context": context},
                metadata={"latency_ms": round(retrieval_ms, 2)},
            )

            # Generation span — Gemini call with token usage
            trace.generation(
                name="gemini",
                model="gemini-2.5-flash",
                input={"question": question, "context": context},
                output=answer,
                usage=usage or {},
                metadata={"latency_ms": round(generation_ms, 2)},
            )

            self.client.flush()

        except Exception as e:
            print(f"Langfuse error: {e}")