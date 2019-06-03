#!/usr/bin/env python3

import os
import sys

import time
import redis
import psycopg2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage

SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')


def run():
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    create_query_path = os.path.join(SCRIPTS_DIR, 'drop_query.sql')
    create_query = open(create_query_path).read()
    try:
        curs.execute(create_query)
    except psycopg2.errors.UndefinedTable:
        pass
    else:
        conn.commit()
    finally:
        curs.close()

    while True:
        try:
            storage.get_redis_storage().flushall()
        except (redis.exceptions.ConnectionError, redis.exceptions.BusyLoadingError):
            print('[*] Redis isn\'t running, waiting...')
            time.sleep(5)
        else:
            break


if __name__ == '__main__':
    run()
