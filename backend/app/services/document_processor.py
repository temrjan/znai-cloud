"""Document processing and indexing service using Llama Index with Reranking."""
import logging
import os
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    VectorParams,
)

# from sentence_transformers import CrossEncoder  # Disabled - slow on CPU
from backend.app.config import settings
from backend.app.utils.query_expander import expand_query

logger = logging.getLogger(__name__)


# Chunking parameters by content type
CHUNK_PARAMS: dict[str, dict[str, int]] = {
    'legal': {'chunk_size': 1024, 'chunk_overlap': 128},      # Legal documents need more context
    'technical': {'chunk_size': 768, 'chunk_overlap': 100},   # Technical docs - code blocks
    'cooking': {'chunk_size': 384, 'chunk_overlap': 50},      # Recipes are shorter
    'faq': {'chunk_size': 256, 'chunk_overlap': 32},          # Q&A pairs are small
    'general': {'chunk_size': 512, 'chunk_overlap': 64},      # Default
}

# Reranker model - good balance of quality and speed
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class DocumentProcessor:
    """Process and index documents using Llama Index and Qdrant with Reranking."""

    def __init__(self):
        # Setup OpenAI embedding model
        self.embed_model = OpenAIEmbedding(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
            dimensions=settings.openai_embedding_dimensions
        )

        # Setup OpenAI LLM
        self.llm = OpenAI(
            model=settings.openai_llm_model,
            api_key=settings.openai_api_key,
        )

        # Set global Llama Index settings (default)
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm
        Settings.chunk_size = 512
        Settings.chunk_overlap = 64

        # Setup Qdrant client
        self.qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )

        self.collection_name = "ai_avangard_documents"

        # Initialize reranker (lazy loading)
        self._reranker: Any = None

        self._ensure_collection()

    @property
    def reranker(self) -> Any:
        """Lazy load reranker model to avoid startup delay."""
        if self._reranker is None:
            logger.info(f"Loading reranker model: {RERANKER_MODEL}")
            self._reranker = CrossEncoder(RERANKER_MODEL, max_length=512)
            logger.info("Reranker model loaded successfully")
        return self._reranker

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.qdrant_client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.openai_embedding_dimensions,
                    distance=Distance.COSINE,
                ),
            )

    def _get_chunk_params(self, content_type: str) -> tuple[int, int]:
        """Get chunk size and overlap for content type."""
        params = CHUNK_PARAMS.get(content_type, CHUNK_PARAMS['general'])
        return params['chunk_size'], params['chunk_overlap']

    def _create_splitter(self, content_type: str) -> SentenceSplitter:
        """Create a text splitter based on content type."""
        chunk_size, chunk_overlap = self._get_chunk_params(content_type)
        logger.info(f"Using chunking: type={content_type}, size={chunk_size}, overlap={chunk_overlap}")
        return SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def extract_text(self, file_path: Path, mime_type: str) -> str:
        """Extract text from various file formats."""
        text = ""

        if mime_type == "text/plain" or file_path.suffix in [".txt", ".md"]:
            text = file_path.read_text(encoding="utf-8", errors="ignore")

        elif mime_type == "application/pdf" or file_path.suffix == ".pdf":
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = "\n".join(page.extract_text() for page in reader.pages)
            except Exception as e:
                raise ValueError(f"Failed to extract PDF: {str(e)}")

        else:
            raise ValueError(f"Unsupported file type: {mime_type}")

        return text.strip()

    def detect_content_type(self, text: str, filename: str) -> str:
        """Detect content type using simple heuristics."""
        text_lower = text.lower()[:5000]  # Check first 5000 chars for performance
        filename_lower = filename.lower()

        # Legal keywords (Russian + English)
        legal_keywords = [
            'договор', 'соглашение', 'закон', 'статья', 'пункт', 'постановление',
            'кодекс', 'конституция', 'регламент', 'устав', 'положение',
            'contract', 'agreement', 'law', 'article', 'clause', 'hereby',
            'whereas', 'jurisdiction', 'liability', 'indemnify'
        ]
        legal_count = sum(1 for kw in legal_keywords if kw in text_lower)
        if legal_count >= 3 or any(kw in filename_lower for kw in ['contract', 'legal', 'agreement', 'договор', 'закон']):
            return 'legal'

        # FAQ/Q&A patterns
        faq_patterns = ['вопрос:', 'ответ:', 'q:', 'a:', 'faq', 'чаво', '?', 'question:', 'answer:']
        faq_count = sum(text_lower.count(p) for p in faq_patterns)
        if faq_count >= 5 or 'faq' in filename_lower:
            return 'faq'

        # Technical keywords
        tech_keywords = [
            'api', 'function', 'class', 'def ', 'import ', 'return ',
            'database', 'algorithm', 'implementation', 'method',
            'код', 'программа', 'алгоритм', 'функция', 'переменная',
            '```', 'const ', 'let ', 'var '
        ]
        tech_count = sum(1 for kw in tech_keywords if kw in text_lower)
        if tech_count >= 3 or any(kw in filename_lower for kw in ['tech', 'api', 'code', 'dev', 'doc']):
            return 'technical'

        # Cooking keywords
        cooking_keywords = [
            'рецепт', 'ингредиент', 'приготовление', 'духовка', 'минут',
            'грамм', 'столовая ложка', 'чайная ложка', 'нарезать', 'варить',
            'recipe', 'ingredient', 'cooking', 'bake', 'tablespoon', 'teaspoon'
        ]
        cooking_count = sum(1 for kw in cooking_keywords if kw in text_lower)
        if cooking_count >= 3 or any(kw in filename_lower for kw in ['recipe', 'cooking', 'рецепт']):
            return 'cooking'

        return 'general'

    def index_document(
        self,
        document_id: str,
        user_id: int,
        filename: str,
        file_path: Path,
        mime_type: str,
        organization_id: int | None = None,
        visibility: str = "private",
    ) -> int:
        """
        Process and index document using Llama Index with adaptive chunking.

        Args:
            document_id: Document UUID
            user_id: User ID who uploaded the document
            filename: Original filename
            file_path: Path to the file
            mime_type: MIME type of the file
            organization_id: Organization ID (None for personal documents)
            visibility: 'private' or 'organization'

        Returns number of chunks indexed.
        """
        # Extract text
        text = self.extract_text(file_path, mime_type)

        if not text:
            raise ValueError("No text extracted from document")

        # Detect content type for adaptive chunking
        content_type = self.detect_content_type(text, filename)
        logger.info(f"Document {filename} detected as: {content_type}")

        # Create appropriate text splitter based on content type
        text_splitter = self._create_splitter(content_type)

        # Create Llama Index Document with metadata
        # Normalize filename to NFC to ensure consistent Unicode representation
        normalized_filename = unicodedata.normalize('NFC', filename)
        metadata = {
            "pg_document_id": str(document_id),
            "user_id": user_id,
            "filename": normalized_filename,
            "content_type": content_type,
            "visibility": visibility,
        }

        # Add organization_id to metadata if it's an organization document
        if organization_id is not None:
            metadata["organization_id"] = organization_id

        doc = Document(
            text=text,
            metadata=metadata
        )

        # Create vector store
        vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name,
        )

        # Create storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store
        )

        # Create index with adaptive chunking
        index = VectorStoreIndex.from_documents(
            [doc],
            storage_context=storage_context,
            transformations=[text_splitter],
            show_progress=False
        )

        # Count chunks
        nodes = text_splitter.get_nodes_from_documents([doc])
        chunks_count = len(nodes)

        logger.info(f"Indexed {filename}: {chunks_count} chunks (type: {content_type})")

        return chunks_count

    def delete_document(self, document_id: str, filename: str = None):
        """Delete all chunks for a document from Qdrant.
        
        Uses pg_document_id for new documents, falls back to filename for legacy.
        """
        deleted = False

        # Try deleting by pg_document_id first (new documents)
        try:
            result = self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="pg_document_id",
                                match=MatchValue(value=str(document_id))
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted document {document_id} by pg_document_id from index. Result: {result}")
            deleted = True
        except Exception as e:
            logger.warning(f"Failed to delete by pg_document_id: {e}")

        # Fallback: delete by filename (for legacy documents without pg_document_id)
        if filename:
            # Try both NFC and NFD normalized forms due to Unicode inconsistencies
            for norm_form in ['NFC', 'NFD']:
                try:
                    normalized_filename = unicodedata.normalize(norm_form, filename)
                    result = self.qdrant_client.delete(
                        collection_name=self.collection_name,
                        points_selector=FilterSelector(
                            filter=Filter(
                                must=[
                                    FieldCondition(
                                        key="filename",
                                        match=MatchValue(value=normalized_filename)
                                    )
                                ]
                            )
                        )
                    )
                    logger.info(f"Deleted document by filename '{filename}' ({norm_form}) from index. Result: {result}")
                    deleted = True
                except Exception as e:
                    logger.warning(f"Failed to delete by filename ({norm_form}): {e}")

        if not deleted:
            logger.warning(f"Could not delete document {document_id} from Qdrant")

    def _rerank_results(self, query: str, results: list[dict], top_n: int = 5) -> list[dict]:
        """
        Rerank search results using cross-encoder model.

        Args:
            query: Original search query
            results: List of search results with 'text' field
            top_n: Number of top results to return after reranking

        Returns:
            Reranked and filtered list of results
        """
        if not results:
            return results

        # Prepare query-document pairs for reranking
        pairs = [(query, r["text"]) for r in results]

        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)

        # Add rerank scores to results
        for i, score in enumerate(rerank_scores):
            results[i]["rerank_score"] = float(score)

        # Sort by rerank score (higher is better)
        results.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Return top N results
        return results[:top_n]

    def _execute_search(
        self,
        index: VectorStoreIndex,
        query: str,
        limit: int,
        score_threshold: float,
        filters: MetadataFilters | None
    ) -> list[dict]:
        """Execute a single search query and return results using retriever (no LLM)."""
        # Use retriever directly to avoid LLM calls
        retriever = index.as_retriever(
            similarity_top_k=limit,
            filters=filters
        )

        nodes = retriever.retrieve(query)

        results = []
        for node in nodes:
            score = node.score if hasattr(node, 'score') else 0.0
            if score >= score_threshold:
                results.append({
                    "text": node.text,
                    "filename": node.metadata.get("filename", "Unknown"),
                    "document_id": node.metadata.get("pg_document_id", ""),
                    "content_type": node.metadata.get("content_type", "general"),
                    "score": score,
                })

        return results

    def search(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.35,
        organization_id: int | None = None,
        search_scope: str = "all",
        use_reranking: bool = True,
        rerank_top_n: int = 5,
    ) -> list[dict]:
        """
        Search for relevant chunks using Llama Index with optional reranking.

        Args:
            user_id: User ID for filtering
            query: Search query
            limit: Maximum number of results from initial search
            score_threshold: Minimum similarity score (0.0-1.0), default 0.5
            organization_id: Organization ID (None for personal mode users)
            search_scope: 'all', 'organization', or 'private'
            use_reranking: Whether to apply reranking (default True)
            rerank_top_n: Number of results to return after reranking

        Returns list of matching chunks with metadata.
        """
        # Expand query with synonyms for better recall
        original_query = query
        query = expand_query(query)
        if query != original_query:
            logger.info(f"Query expanded: '{original_query}' -> '{query}'")

        # Create vector store
        vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name,
        )

        # Create index from existing vector store
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
        )

        # For reranking, fetch more initial results (3x the final limit)
        initial_limit = limit * 3 if use_reranking else limit

        if search_scope == "organization":
            # Only organization documents
            if organization_id is None:
                return []
            filters = MetadataFilters(filters=[
                ExactMatchFilter(key="organization_id", value=organization_id),
                ExactMatchFilter(key="visibility", value="organization"),
            ])
            results = self._execute_search(index, query, initial_limit, score_threshold, filters)

        elif search_scope == "private":
            # Only personal documents
            filters = MetadataFilters(filters=[
                ExactMatchFilter(key="user_id", value=user_id),
                ExactMatchFilter(key="visibility", value="private"),
            ])
            results = self._execute_search(index, query, initial_limit, score_threshold, filters)

        else:  # search_scope == "all"
            # Hybrid mode: organization docs + personal docs
            results = []

            # Search organization documents if user is in organization
            if organization_id is not None:
                org_filters = MetadataFilters(filters=[
                    ExactMatchFilter(key="organization_id", value=organization_id),
                    ExactMatchFilter(key="visibility", value="organization"),
                ])
                org_results = self._execute_search(index, query, initial_limit, score_threshold, org_filters)
                results.extend(org_results)

            # Search personal documents
            personal_filters = MetadataFilters(filters=[
                ExactMatchFilter(key="user_id", value=user_id),
                ExactMatchFilter(key="visibility", value="private"),
            ])
            personal_results = self._execute_search(index, query, initial_limit, score_threshold, personal_filters)
            results.extend(personal_results)

            # Remove duplicates by document_id
            seen = set()
            unique_results = []
            for r in results:
                doc_id = r.get("document_id", r["text"][:50])
                if doc_id not in seen:
                    seen.add(doc_id)
                    unique_results.append(r)
            results = unique_results

        # Apply reranking if enabled
        if use_reranking and results:
            logger.info(f"Reranking {len(results)} results for query: {query[:50]}...")
            results = self._rerank_results(query, results, top_n=rerank_top_n)
            logger.info(f"Reranking complete. Top score: {results[0].get('rerank_score', 'N/A') if results else 'N/A'}")
        else:
            # Sort by original score and limit
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:limit]

        return results


# Singleton instance
document_processor = DocumentProcessor()
