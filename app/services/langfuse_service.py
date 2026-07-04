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
            print("TRACE_CHAT CALLED")

            with self.client.start_as_current_observation(name="rag-chat") as trace:
                trace.update(
                    input={"question": question},
                    output=answer,
                    metadata={
                        "retrieval_ms": round(retrieval_ms, 2),
                        "generation_ms": round(generation_ms, 2),
                        "total_ms": round(
                            retrieval_ms + generation_ms,
                            2,
                        ),
                    },
                )

            self.client.flush()

            print("LANGFUSE FLUSH COMPLETE")

        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"LANGFUSE ERROR: {e}")
