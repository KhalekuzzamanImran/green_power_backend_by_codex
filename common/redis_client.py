from django.conf import settings
from redis.asyncio import ConnectionPool, Redis
from redis import Redis as SyncRedis

_pool = ConnectionPool.from_url(settings.REDIS_URL)
_client = Redis(connection_pool=_pool)
_sync_client: SyncRedis | None = None


def get_async_redis() -> Redis:
    return _client


def get_redis() -> SyncRedis:
    global _sync_client
    if _sync_client is None:
        _sync_client = SyncRedis.from_url(settings.REDIS_URL, decode_responses=True)
    return _sync_client


async def close_async_redis() -> None:
    await _client.close()
    await _pool.disconnect(inuse_connections=True)
