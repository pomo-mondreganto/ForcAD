#!/usr/bin/env python3

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
from scripts import reset_db, init_db
from scripts import print_tokens


def run():
    reset_db.run()
    init_db.run()

    r = storage.get_redis_storage()
    r.flushall()

    print('New team tokens:')
    print_tokens.run()


if __name__ == '__main__':
    run()
