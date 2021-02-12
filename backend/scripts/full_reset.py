#!/usr/bin/env python3

from lib import storage

from scripts import print_tokens
from scripts import reset_db, init_db


def run():
    print('Resetting the database')
    reset_db.run()

    print('Initializing the database')
    init_db.run()

    r = storage.utils.RedisStorage.get()
    r.flushall()

    print('New team tokens:')
    print_tokens.run()


if __name__ == '__main__':
    run()
