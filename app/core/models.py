from sentence_transformers import SentenceTransformer

# Loaded ONCE when the module is first imported.
# Every service that imports this gets the same object — no duplication.
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
