from contextlib import contextmanager

import kombu
import redis
import socketio
from psycopg2 import pool, extras

from lib import config
from lib.helpers.singleton import Singleton, T


class DBPool(Singleton[pool.SimpleConnectionPool]):

    @staticmethod
    def create() -> pool.SimpleConnectionPool:
        database_config = config.get_db_config()
        return pool.SimpleConnectionPool(
            minconn=5,
            maxconn=20,
            **database_config.dict(),
        )


class RedisStorage(Singleton[redis.Redis]):

    @staticmethod
    def create() -> redis.Redis:
        redis_config = config.get_redis_config()
        return redis.Redis(decode_responses=True, **redis_config.dict())


class SIOManager(Singleton[socketio.KombuManager]):

    @staticmethod
    def create(*, write_only: bool = False) -> socketio.KombuManager:
        broker_url = config.get_broker_url()
        return socketio.KombuManager(
            url=broker_url,
            write_only=write_only,
            channel='forcad-front',
        )

    @classmethod
    def get(cls, *, write_only: bool) -> T:
        return super().get(write_only=write_only)

    @classmethod
    def write_only(cls) -> socketio.KombuManager:
        return cls.get(write_only=True)

    @classmethod
    def read_write(cls) -> socketio.KombuManager:
        return cls.get(write_only=False)


class BrokerConnection(Singleton[kombu.Connection]):

    @staticmethod
    def create() -> kombu.Connection:
        return kombu.Connection(config.get_broker_url())


@contextmanager
def db_cursor(dict_cursor: bool = False):  # type: ignore
    db_pool = DBPool.get()
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


def redis_pipeline(transaction: bool = True) -> redis.client.Pipeline:
    storage = RedisStorage.get()
    return storage.pipeline(transaction=transaction)
