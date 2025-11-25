"""Prometheus metrics for monitoring."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Request metrics
REQUEST_COUNT = Counter(
    'ai_avangard_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'ai_avangard_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# RAG metrics
RAG_SEARCH_COUNT = Counter(
    'ai_avangard_rag_searches_total',
    'Total number of RAG searches',
    ['search_scope', 'has_results']
)

RAG_SEARCH_SCORE = Histogram(
    'ai_avangard_rag_search_score',
    'RAG search relevance scores',
    ['search_scope'],
    buckets=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

RAG_RESULTS_COUNT = Histogram(
    'ai_avangard_rag_results_count',
    'Number of results returned by RAG search',
    buckets=[0, 1, 2, 3, 4, 5, 10]
)

# OpenAI API metrics
OPENAI_REQUESTS = Counter(
    'ai_avangard_openai_requests_total',
    'Total OpenAI API requests',
    ['model', 'status']
)

OPENAI_LATENCY = Histogram(
    'ai_avangard_openai_latency_seconds',
    'OpenAI API latency in seconds',
    ['model'],
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]
)

OPENAI_TOKENS = Counter(
    'ai_avangard_openai_tokens_total',
    'Total tokens used',
    ['model', 'type']  # type: prompt, completion
)

# Document metrics
DOCUMENTS_INDEXED = Counter(
    'ai_avangard_documents_indexed_total',
    'Total documents indexed',
    ['status']  # success, failed
)

CHUNKS_CREATED = Counter(
    'ai_avangard_chunks_created_total',
    'Total chunks created during indexing'
)

# User metrics
ACTIVE_USERS = Gauge(
    'ai_avangard_active_users',
    'Number of active users (queries in last hour)'
)

QUERIES_TODAY = Gauge(
    'ai_avangard_queries_today',
    'Number of queries today'
)

# Feedback metrics
FEEDBACK_COUNT = Counter(
    'ai_avangard_feedback_total',
    'Total feedback received',
    ['rating']  # positive, negative
)


def get_metrics():
    """Generate Prometheus metrics output."""
    return generate_latest()


def get_content_type():
    """Get Prometheus content type."""
    return CONTENT_TYPE_LATEST
