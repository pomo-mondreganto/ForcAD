from contextlib import contextmanager

import aioredis
import redis
import socketio
from psycopg2 import pool, extras

import config
from storage import (
    game,
    tasks,
    flags,
    caching,
    teams,
)

_redis_storage = None
_async_redis_storage = None
_db_pool = None
_async_sio_manager = None
_sio_wro_manager = None


def get_db_pool():
    global _db_pool

    if not _db_pool:
        database_config = config.get_db_config()
        _db_pool = pool.SimpleConnectionPool(minconn=5, maxconn=20, **database_config)

    return _db_pool


@contextmanager
def db_cursor(dict_cursor=False):
    db_pool = get_db_pool()
    conn = db_pool.getconn()
    if dict_cursor:
        curs = conn.cursor(cursor_factory=extras.RealDictCursor)
    else:
        curs = conn.cursor()
    try:
        yield conn, curs
    finally:
        curs.close()
        db_pool.putconn(conn)


def get_redis_storage():
    global _redis_storage

    if not _redis_storage:
        redis_config = config.get_redis_config()
        _redis_storage = redis.StrictRedis(**redis_config, decode_responses=True)

    return _redis_storage


async def _connect_async_redis(loop):
    redis_config = config.get_redis_config()
    address = f'redis://{redis_config["host"]}:{redis_config["port"]}'
    db = redis_config['db']
    return await aioredis.create_redis(
        address=address,
        db=db,
        password=redis_config.get('password', None),
        loop=loop,
        encoding='utf-8',
    )


async def get_async_redis_storage(loop, always_create_new=False):
    if always_create_new:
        return await _connect_async_redis(loop)

    global _async_redis_storage

    if not _async_redis_storage:
        _async_redis_storage = await _connect_async_redis(loop)

    return _async_redis_storage


def get_async_sio_manager():
    global _async_sio_manager

    if _async_sio_manager is None:
        broker_url = config.get_broker_url()
        _async_sio_manager = socketio.AsyncAioPikaManager(
            url=broker_url,
            write_only=False,
            channel='forcad-front',
        )

    return _async_sio_manager


def get_wro_sio_manager():
    global _sio_wro_manager

    if _sio_wro_manager is None:
        broker_url = config.get_broker_url()
        _sio_wro_manager = socketio.KombuManager(
            url=broker_url,
            write_only=True,
            channel='forcad-front',
        )

    return _sio_wro_manager
