import json
import hashlib
from typing import Any, Optional
import redis.asyncio as aioredis
from app.config import settings

# Initialize async Redis client connection pool
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

def generate_cache_key(tool_name: str, args: dict[str, Any]) -> str:
    """
    Generate a deterministic Redis key based on tool name and hashed argument inputs.
    """
    sorted_args = json.dumps(args, sort_keys=True)
    arg_hash = hashlib.sha256(sorted_args.encode()).hexdigest()[:12]
    return f"cache:tools:{tool_name}:{arg_hash}"

async def get_cached_tool_result(tool_name: str, args: dict[str, Any]) -> Optional[Any]:
    """
    Retrieve cached result from Redis if available.
    """
    try:
        key = generate_cache_key(tool_name, args)
        cached_data = await redis_client.get(key)
        if cached_data:
            print(f"[Redis Cache HIT] Key: {key}")
            return json.loads(cached_data)
        print(f"[Redis Cache MISS] Key: {key}")
    except Exception as e:
        print(f"[Redis Cache Error] Read failed: {e}")
    return None

async def set_cached_tool_result(tool_name: str, args: dict[str, Any], result: Any, ttl_seconds: int = 60) -> None:
    """
    Store tool result in Redis with an explicit Expiration TTL.
    """
    try:
        key = generate_cache_key(tool_name, args)
        await redis_client.set(key, json.dumps(result), ex=ttl_seconds)
        print(f"[Redis Cache WRITE] Key: {key} (TTL: {ttl_seconds}s)")
    except Exception as e:
        print(f"[Redis Cache Error] Write failed: {e}")