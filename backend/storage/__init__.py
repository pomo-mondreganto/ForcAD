from contextlib import contextmanager, asynccontextmanager

import aiopg
import aioredis
import redis
import socketio
from kombu import Connection
from psycopg2 import pool, extras, _ext

import config
from storage import (
    caching,
    flags,
    game,
    tasks,
    teams,
)

__all__ = ['caching', 'flags', 'game', 'tasks', 'teams']

_redis_storage = None
_async_redis_storage = None
_db_pool = None
_async_db_pool = None
_async_sio_manager = None
_sio_wro_manager = None
_rmq_connection = None


def get_db_pool() -> pool.SimpleConnectionPool:
    global _db_pool

    if not _db_pool:
        database_config = config.get_db_config()
        _db_pool = pool.SimpleConnectionPool(
            minconn=5,
            maxconn=20,
            **database_config,
        )

    return _db_pool


async def get_async_db_pool() -> aiopg.pool.Pool:
    global _async_db_pool

    if not _async_db_pool:
        database_config = config.get_db_config()
        dsn = _ext.make_dsn(**database_config)
        _async_db_pool = await aiopg.create_pool(dsn)

    return _async_db_pool


@contextmanager
def db_cursor(dict_cursor: bool = False):  # type: ignore
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


@asynccontextmanager
async def async_db_cursor(dict_cursor: bool = False):  # type: ignore
    db_pool = await get_async_db_pool()
    conn = await db_pool.acquire()

    if dict_cursor:
        curs = await conn.cursor(cursor_factory=extras.RealDictCursor)
    else:
        curs = await conn.cursor()

    try:
        yield conn, curs
    finally:
        curs.close()
        await db_pool.release(conn)


def get_redis_storage() -> redis.StrictRedis:
    global _redis_storage

    if not _redis_storage:
        redis_config = config.get_redis_config()
        redis_config['decode_responses'] = True
        _redis_storage = redis.StrictRedis(
            **redis_config,
        )

    return _redis_storage


async def get_async_redis_storage() -> aioredis.Redis:
    global _async_redis_storage

    if not _async_redis_storage:
        redis_config = config.get_redis_config()
        address = f'redis://{redis_config["host"]}:{redis_config["port"]}'
        db = redis_config['db']
        _async_redis_storage = await aioredis.create_redis_pool(
            address=address,
            db=db,
            password=redis_config.get('password', None),
            encoding='utf-8',
        )

    return _async_redis_storage


def get_async_sio_manager() -> socketio.AsyncAioPikaManager:
    global _async_sio_manager

    if _async_sio_manager is None:
        broker_url = config.get_broker_url()
        _async_sio_manager = socketio.AsyncAioPikaManager(
            url=broker_url,
            write_only=False,
            channel='forcad-front',
        )

    return _async_sio_manager


def get_wro_sio_manager() -> socketio.KombuManager:
    global _sio_wro_manager

    if _sio_wro_manager is None:
        broker_url = config.get_broker_url()
        _sio_wro_manager = socketio.KombuManager(
            url=broker_url,
            write_only=True,
            channel='forcad-front',
        )

    return _sio_wro_manager


def get_broker_connection() -> Connection:
    global _rmq_connection

    if _rmq_connection is None:
        _rmq_connection = Connection(config.get_broker_url())

    return _rmq_connection
