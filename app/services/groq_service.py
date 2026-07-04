import time
from collections.abc import Generator

from groq import Groq

from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

PROMPT_TEMPLATE = """You are a helpful AI assistant.

Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}

Answer:"""

GROQ_MODEL = "llama-3.1-8b-instant"


class GroqService:
    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> tuple[str, dict, float]:
        """
        Returns (answer_text, usage_dict, generation_ms).
        Same interface as GeminiService.generate_answer.
        """
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        t0 = time.time()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        generation_ms = (time.time() - t0) * 1000

        usage = {}
        if response.usage:
            usage = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens,
            }

        answer = response.choices[0].message.content or ""
        return answer, usage, generation_ms

    def stream_answer(
        self,
        question: str,
        context: str,
    ) -> Generator[str, None, None]:
        """
        Yields text chunks as Groq generates them.
        Same interface as GeminiService.stream_answer.
        """
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            stream=True,
        )

        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                yield text
