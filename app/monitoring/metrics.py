from prometheus_client import Counter, Gauge, Histogram

# HTTP METRICS #

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint"],
)

HTTP_RESPONSES_TOTAL = Counter(
    "http_responses_total",
    "Total number of HTTP responses",
    ["method", "endpoint", "status"],
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
)

# RAG METRICS #

RAG_QUERIES_TOTAL = Counter(
    "rag_queries_total",
    "Total RAG queries",
)

RAG_RETRIEVAL_DURATION_SECONDS = Histogram(
    "rag_retrieval_duration_seconds",
    "Vector retrieval latency",
)

RAG_GENERATION_DURATION_SECONDS = Histogram(
    "rag_generation_duration_seconds",
    "LLM generation latency",
)

RAG_CHUNKS_RETRIEVED = Histogram(
    "rag_chunks_retrieved",
    "Number of chunks retrieved from Qdrant",
)

RAG_RERANKER_REQUESTS_TOTAL = Counter(
    "rag_reranker_requests_total",
    "Number of requests that used reranking",
)

RAG_RERANKER_DURATION_SECONDS = Histogram(
    "rag_reranker_duration_seconds",
    "Time spent reranking chunks",
)

RAG_EMPTY_RETRIEVALS_TOTAL = Counter(
    "rag_empty_retrievals_total",
    "Number of retrievals returning zero chunks",
)

RAG_CONTEXT_LENGTH = Histogram(
    "rag_context_length",
    "Characters sent to the LLM as context",
)

RAG_SOURCE_DOCUMENTS = Histogram(
    "rag_source_documents",
    "Number of unique source documents",
)


# EMBEDDING METRICS #

EMBEDDING_REQUESTS_TOTAL = Counter(
    "embedding_requests_total",
    "Total embedding requests",
)

EMBEDDING_DURATION_SECONDS = Histogram(
    "embedding_duration_seconds",
    "Embedding generation latency",
)

EMBEDDING_FAILURES_TOTAL = Counter(
    "embedding_failures_total",
    "Failed embedding requests",
)


# QDRANT METRICS #
QDRANT_SEARCH_REQUESTS_TOTAL = Counter(
    "qdrant_search_requests_total",
    "Total Qdrant search requests",
)

QDRANT_SEARCH_DURATION_SECONDS = Histogram(
    "qdrant_search_duration_seconds",
    "Qdrant search latency",
)

QDRANT_INSERT_REQUESTS_TOTAL = Counter(
    "qdrant_insert_requests_total",
    "Total Qdrant insert requests",
)

QDRANT_INSERT_DURATION_SECONDS = Histogram(
    "qdrant_insert_duration_seconds",
    "Qdrant insert latency",
)

QDRANT_POINTS_TOTAL = Gauge(
    "qdrant_points_total",
    "Total vectors stored in Qdrant",
)

# LLM METRICS #

LLM_REQUESTS_TOTAL = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["provider", "model"],
)

LLM_FAILURES_TOTAL = Counter(
    "llm_failures_total",
    "Total failed LLM requests",
    ["provider", "model"],
)

LLM_DURATION_SECONDS = Histogram(
    "llm_duration_seconds",
    "LLM request latency",
    ["provider", "model"],
)

LLM_PROMPT_TOKENS_TOTAL = Counter(
    "llm_prompt_tokens_total",
    "Prompt tokens consumed",
    ["provider", "model"],
)

LLM_COMPLETION_TOKENS_TOTAL = Counter(
    "llm_completion_tokens_total",
    "Completion tokens consumed",
    ["provider", "model"],
)

LLM_TOTAL_TOKENS_TOTAL = Counter(
    "llm_total_tokens_total",
    "Total tokens consumed",
    ["provider", "model"],
)

LLM_COST_USD_TOTAL = Counter(
    "llm_cost_usd_total",
    "Estimated LLM cost in USD",
    ["provider", "model"],
)

# EXPORTS #
__all__ = [
    "CONTENT_TYPE_LATEST",
    "generate_latest",

    # HTTP
    "HTTP_REQUESTS_TOTAL",
    "HTTP_RESPONSES_TOTAL",
    "HTTP_REQUESTS_IN_PROGRESS",
    "HTTP_REQUEST_DURATION_SECONDS",

    # RAG
    "RAG_QUERIES_TOTAL",
    "RAG_RETRIEVAL_DURATION_SECONDS",
    "RAG_GENERATION_DURATION_SECONDS",
    "RAG_CHUNKS_RETRIEVED",
    "RAG_RERANKER_REQUESTS_TOTAL",
    "RAG_RERANKER_DURATION_SECONDS",
    "RAG_EMPTY_RETRIEVALS_TOTAL",
    "RAG_CONTEXT_LENGTH",
    "RAG_SOURCE_DOCUMENTS",

    # Embeddings
    "EMBEDDING_REQUESTS_TOTAL",
    "EMBEDDING_DURATION_SECONDS",
    "EMBEDDING_FAILURES_TOTAL",

    # Qdrant
    "QDRANT_SEARCH_REQUESTS_TOTAL",
    "QDRANT_SEARCH_DURATION_SECONDS",
    "QDRANT_INSERT_REQUESTS_TOTAL",
    "QDRANT_INSERT_DURATION_SECONDS",
    "QDRANT_POINTS_TOTAL",

    # LLM
    "LLM_REQUESTS_TOTAL",
    "LLM_FAILURES_TOTAL",
    "LLM_DURATION_SECONDS",
    "LLM_PROMPT_TOKENS_TOTAL",
    "LLM_COMPLETION_TOKENS_TOTAL",
    "LLM_TOTAL_TOKENS_TOTAL",
    "LLM_COST_USD_TOTAL",
]