from unittest.mock import MagicMock, patch

# Mock the embedding model BEFORE app.main is imported.
# Without this, importing app.main triggers SentenceTransformer()
# which tries to download model weights — CI has no cache for this.
with patch("sentence_transformers.SentenceTransformer", return_value=MagicMock()):
    from fastapi.testclient import TestClient

    from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
