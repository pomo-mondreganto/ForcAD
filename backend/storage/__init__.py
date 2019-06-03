import aioredis
import redis
from psycopg2 import pool

import config
from storage import (
    game,
    tasks,
    flags,
    caching,
    teams,
)

_redis_storage = None
_async_redis_pool = None
_db_pool = None


def get_db_pool():
    global _db_pool

    if not _db_pool:
        database_config = config.get_storage_config()['db']
        _db_pool = pool.SimpleConnectionPool(minconn=1, maxconn=20, **database_config)

    return _db_pool


def get_redis_storage():
    global _redis_storage

    if not _redis_storage:
        redis_config = config.get_storage_config()['redis']
        _redis_storage = redis.StrictRedis(**redis_config)

    return _redis_storage


async def get_async_redis_pool(loop):
    global _async_redis_pool

    if not _async_redis_pool:
        redis_config = config.get_storage_config()['redis']
        address = f'redis://{redis_config["host"]}:{redis_config["port"]}'
        db = redis_config['db']
        _async_redis_pool = await aioredis.create_redis_pool(
            address=address,
            db=db,
            minsize=5,
            maxsize=15,
            loop=loop,
        )
    return _async_redis_pool
