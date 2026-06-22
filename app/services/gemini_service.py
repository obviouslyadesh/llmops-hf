from google import genai

from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:

        prompt = f"""You are a helpful AI assistant.

Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}

Answer:"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text
