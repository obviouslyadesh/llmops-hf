from app.core.models import embedding_model


class EmbeddingService:
    """
    Stateless wrapper around the shared embedding model.
    No model is loaded here — it was loaded once in app.core.models.
    """

    def embed_text(self, text: str) -> list[float]:
        return embedding_model.encode(text).tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return embedding_model.encode(texts).tolist()
