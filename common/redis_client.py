from django.conf import settings
from redis.asyncio import ConnectionPool, Redis

_pool = ConnectionPool.from_url(settings.REDIS_URL)
_client = Redis(connection_pool=_pool)


def get_async_redis() -> Redis:
    return _client


async def close_async_redis() -> None:
    await _client.close()
    await _pool.disconnect(inuse_connections=True)
