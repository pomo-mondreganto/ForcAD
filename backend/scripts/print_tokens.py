#!/usr/bin/env python3

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage

_SELECT_TEAMS_NAME_TOKEN_QUERY = "SELECT name, token from teams"


def run():
    with storage.db_cursor() as (conn, curs):
        curs.execute(_SELECT_TEAMS_NAME_TOKEN_QUERY)
        result = curs.fetchall()

    print('\n'.join("{name}:{token}".format(name=name, token=token) for name, token in result))


if __name__ == '__main__':
    run()
