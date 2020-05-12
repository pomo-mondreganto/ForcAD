#!/usr/bin/env python3

import sys
from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

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
