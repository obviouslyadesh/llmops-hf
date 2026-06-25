import time
from collections.abc import Generator

from google import genai

from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

PROMPT_TEMPLATE = """You are a helpful AI assistant.

Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}

Answer:"""


class GeminiService:

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> tuple[str, dict, float]:
        """
        Returns (answer_text, usage_dict, generation_ms).
        """
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        t0 = time.time()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        generation_ms = (time.time() - t0) * 1000

        # Extract token usage if available
        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = {
                "input": getattr(response.usage_metadata, "prompt_token_count", 0),
                "output": getattr(response.usage_metadata, "candidates_token_count", 0),
                "total": getattr(response.usage_metadata, "total_token_count", 0),
            }

        return response.text, usage, generation_ms

    def stream_answer(
        self,
        question: str,
        context: str,
    ) -> Generator[str, None, None]:
        """
        Yields text chunks as Gemini generates them.
        """
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt,
        ):
            if chunk.text:
                yield chunk.text