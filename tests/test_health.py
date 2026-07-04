from unittest.mock import MagicMock, patch

with (
    patch("sentence_transformers.SentenceTransformer", return_value=MagicMock()),
    patch("qdrant_client.QdrantClient", return_value=MagicMock()),
):
    from fastapi.testclient import TestClient

    from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
