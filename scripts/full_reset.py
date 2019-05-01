import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import config
from scripts import reset_db, init_db


def run():
    try:
        os.remove(os.path.join(config.BASE_DIR, 'volumes/shared/round'))
    except FileNotFoundError:
        pass

    reset_db.run()
    init_db.run()

    r = storage.get_redis_storage()
    r.flushall()


if __name__ == '__main__':
    run()
