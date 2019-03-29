import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import psycopg2


def run():
    def _run(_query):
        conn = storage.get_db_pool().getconn()
        curs = conn.cursor()
        try:
            curs.execute(_query)
        except psycopg2.ProgrammingError:
            pass
        else:
            conn.commit()
        finally:
            storage.get_db_pool().putconn(conn)

    query = '''DROP TABLE teams'''
    _run(query)

    query = '''DROP TABLE flags'''
    _run(query)

    query = '''DROP TABLE stolenflags'''
    _run(query)

    query = '''DROP TABLE tasks'''
    _run(query)

    query = '''DROP TABLE teamtasks'''
    _run(query)

    storage.get_redis_storage().flushall()


if __name__ == '__main__':
    run()
