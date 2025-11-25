"""Redis caching utilities for RAG queries."""
import json
import hashlib
import logging
from typing import Optional, Any
import redis

from backend.app.config import settings

logger = logging.getLogger(__name__)

# Redis client singleton
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password or None,
            db=settings.redis_db,
            decode_responses=True,
        )
    return _redis_client


def make_cache_key(prefix: str, *args) -> str:
    """Generate a cache key from prefix and arguments."""
    key_data = f"{prefix}:" + ":".join(str(a) for a in args)
    # Use MD5 hash for long keys
    if len(key_data) > 200:
        hash_part = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{hash_part}"
    return key_data


class SearchCache:
    """Cache for RAG search results."""
    
    TTL_SECONDS = 3600  # 1 hour cache
    PREFIX = "rag_search"
    
    @classmethod
    def get(cls, user_id: int, query: str, org_id: Optional[int], scope: str) -> Optional[list]:
        """Get cached search results."""
        try:
            client = get_redis_client()
            key = make_cache_key(cls.PREFIX, user_id, query.lower().strip(), org_id or 0, scope)
            cached = client.get(key)
            if cached:
                logger.debug(f"Cache HIT for search: {query[:30]}...")
                return json.loads(cached)
            logger.debug(f"Cache MISS for search: {query[:30]}...")
            return None
        except Exception as e:
            logger.warning(f"Redis cache get error: {e}")
            return None
    
    @classmethod
    def set(cls, user_id: int, query: str, org_id: Optional[int], scope: str, results: list) -> None:
        """Cache search results."""
        try:
            client = get_redis_client()
            key = make_cache_key(cls.PREFIX, user_id, query.lower().strip(), org_id or 0, scope)
            client.setex(key, cls.TTL_SECONDS, json.dumps(results))
            logger.debug(f"Cached search results: {query[:30]}...")
        except Exception as e:
            logger.warning(f"Redis cache set error: {e}")
    
    @classmethod
    def invalidate_user(cls, user_id: int) -> None:
        """Invalidate all cache for a user (when they upload new document)."""
        try:
            client = get_redis_client()
            pattern = f"{cls.PREFIX}:{user_id}:*"
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys for user {user_id}")
        except Exception as e:
            logger.warning(f"Redis cache invalidate error: {e}")
    
    @classmethod
    def invalidate_org(cls, organization_id: int) -> None:
        """Invalidate cache for all users in organization."""
        try:
            client = get_redis_client()
            # Pattern matches any user with this org_id
            pattern = f"{cls.PREFIX}:*:{organization_id}:*"
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys for org {organization_id}")
        except Exception as e:
            logger.warning(f"Redis cache invalidate error: {e}")
