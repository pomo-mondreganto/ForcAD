import redis
from psycopg2 import pool

import config
from storage import flags, teams, tasks

_redis_storage = None
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
