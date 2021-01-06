import redis
import socketio
from contextlib import contextmanager
from kombu import Connection
from psycopg2 import pool, extras

import config

_redis_storage = None
_db_pool = None
_sio_wro_manager = None
_sio_manager = None
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


def get_redis_storage() -> redis.StrictRedis:
    global _redis_storage

    if not _redis_storage:
        redis_config = config.get_redis_config()
        redis_config['decode_responses'] = True
        _redis_storage = redis.StrictRedis(
            **redis_config,
        )

    return _redis_storage


def redis_pipeline(transaction: bool = True) -> redis.client.Pipeline:
    storage = get_redis_storage()
    return storage.pipeline(transaction=transaction)


def create_sio_manager(write_only=False) -> socketio.KombuManager:
    broker_url = config.get_broker_url()
    return socketio.KombuManager(
        url=broker_url,
        write_only=write_only,
        channel='forcad-front',
    )


def get_wro_sio_manager() -> socketio.KombuManager:
    global _sio_wro_manager
    if _sio_wro_manager is None:
        _sio_wro_manager = create_sio_manager(write_only=True)
    return _sio_wro_manager


def get_sio_manager() -> socketio.KombuManager:
    global _sio_manager
    if _sio_manager is None:
        _sio_manager = create_sio_manager(write_only=False)
    return _sio_manager


def get_broker_connection() -> Connection:
    global _rmq_connection

    if _rmq_connection is None:
        _rmq_connection = Connection(config.get_broker_url())

    return _rmq_connection
