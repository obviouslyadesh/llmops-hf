import logging
import time
from collections.abc import Generator

from groq import Groq

from app.core.config import settings
from app.monitoring.metrics import (
    LLM_COMPLETION_TOKENS_TOTAL,
    LLM_COST_USD_TOTAL,
    LLM_DURATION_SECONDS,
    LLM_FAILURES_TOTAL,
    LLM_PROMPT_TOKENS_TOTAL,
    LLM_REQUESTS_TOTAL,
    LLM_TOTAL_TOKENS_TOTAL,
)

logger = logging.getLogger("llmops")

client = Groq(api_key=settings.GROQ_API_KEY)

GROQ_MODEL = "llama-3.1-8b-instant"
PROVIDER = "groq"

# Approximate pricing (USD per million tokens)
PROMPT_PRICE_PER_MILLION = 0.05
COMPLETION_PRICE_PER_MILLION = 0.08

PROMPT_TEMPLATE = """You are a helpful AI assistant.

Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}

Answer:
"""


class GroqService:
    def _estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Estimate request cost in USD."""

        prompt_cost = (prompt_tokens / 1_000_000) * PROMPT_PRICE_PER_MILLION

        completion_cost = (completion_tokens / 1_000_000) * COMPLETION_PRICE_PER_MILLION

        return prompt_cost + completion_cost

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> tuple[str, dict, float]:

        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        LLM_REQUESTS_TOTAL.labels(
            provider=PROVIDER,
            model=GROQ_MODEL,
        ).inc()

        start = time.perf_counter()

        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0,
            )

            duration = time.perf_counter() - start

            LLM_DURATION_SECONDS.labels(
                provider=PROVIDER,
                model=GROQ_MODEL,
            ).observe(duration)

            usage = {}

            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens

                usage = {
                    "input": prompt_tokens,
                    "output": completion_tokens,
                    "total": total_tokens,
                }

                LLM_PROMPT_TOKENS_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(prompt_tokens)

                LLM_COMPLETION_TOKENS_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(completion_tokens)

                LLM_TOTAL_TOKENS_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(total_tokens)

                estimated_cost = self._estimate_cost(
                    prompt_tokens,
                    completion_tokens,
                )

                LLM_COST_USD_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(estimated_cost)

            answer = response.choices[0].message.content or ""

            return (
                answer,
                usage,
                duration * 1000,
            )

        except Exception:
            LLM_FAILURES_TOTAL.labels(
                provider=PROVIDER,
                model=GROQ_MODEL,
            ).inc()

            logger.exception("Groq request failed")

            raise

    def stream_answer(
        self,
        question: str,
        context: str,
    ) -> Generator[str, None, None]:

        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        LLM_REQUESTS_TOTAL.labels(
            provider=PROVIDER,
            model=GROQ_MODEL,
        ).inc()

        start = time.perf_counter()

        try:
            stream = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0,
                stream=True,
            )

            first_token = False
            usage = None

            for chunk in stream:
                # Record latency when first token arrives
                if not first_token:
                    LLM_DURATION_SECONDS.labels(
                        provider=PROVIDER,
                        model=GROQ_MODEL,
                    ).observe(time.perf_counter() - start)

                    first_token = True

                # Save usage from the final chunk (Groq sends it automatically)
                if getattr(chunk, "usage", None):
                    usage = chunk.usage

                # Stream token
                if chunk.choices:
                    text = chunk.choices[0].delta.content

                    if text:
                        yield text

            # Update Prometheus metrics after stream completes
            if usage:
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens

                LLM_PROMPT_TOKENS_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(prompt_tokens)

                LLM_COMPLETION_TOKENS_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(completion_tokens)

                LLM_TOTAL_TOKENS_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(total_tokens)

                estimated_cost = self._estimate_cost(
                    prompt_tokens,
                    completion_tokens,
                )

                LLM_COST_USD_TOTAL.labels(
                    provider=PROVIDER,
                    model=GROQ_MODEL,
                ).inc(estimated_cost)

                logger.info(
                    "Streaming usage | prompt=%d completion=%d total=%d cost=$%.8f",
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    estimated_cost,
                )
            else:
                logger.warning("Groq streaming finished without usage information.")

        except Exception:
            LLM_FAILURES_TOTAL.labels(
                provider=PROVIDER,
                model=GROQ_MODEL,
            ).inc()

            logger.exception("Groq streaming request failed")

            raise
