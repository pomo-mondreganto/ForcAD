#!/usr/bin/env python3

from lib import storage

from scripts import print_tokens
from scripts import reset_db, init_db


def run():
    reset_db.run()
    init_db.run()

    r = storage.utils.get_redis_storage()
    r.flushall()

    print('New team tokens:')
    print_tokens.run()


if __name__ == '__main__':
    run()
