from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query: str, chunks: list[str], top_k: int = 3) -> list[str]:
    """
    Rerank chunks by relevance to query using a cross-encoder.
    Returns top_k chunks sorted by descending relevance score.
    """
    if not chunks:
        return chunks

    pairs = [(query, chunk) for chunk in chunks]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in ranked[:top_k]]
