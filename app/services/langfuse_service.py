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
    ):
        try:
            trace = self.client.trace(
                name="rag-chat",
                input={"question": question},
                output=answer,
            )

            trace.span(
                name="retrieval",
                input={"question": question},
                output={"context": context},
            )

            trace.generation(
                name="gemini",
                model="gemini-2.5-flash",
                input={
                    "question": question,
                    "context": context,
                },
                output=answer,
            )

            self.client.flush()

        except Exception as e:
            print(f"Langfuse error: {e}")
