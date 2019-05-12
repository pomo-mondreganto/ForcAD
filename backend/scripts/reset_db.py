import os
import sys

import psycopg2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage

SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')


def run():
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    create_query_path = os.path.join(SCRIPTS_DIR, 'drop_query.sql')
    create_query = open(create_query_path, 'r').read()
    try:
        curs.execute(create_query)
    except psycopg2.errors.UndefinedTable:
        pass
    else:
        conn.commit()
    finally:
        curs.close()

    storage.get_redis_storage().flushall()


if __name__ == '__main__':
    run()
