#!/usr/bin/env python3

import sys

from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import storage

_SELECT_TEAMS_NAME_TOKEN_QUERY = "SELECT name, token from teams"


def run():
    with storage.db_cursor() as (_, curs):
        curs.execute(_SELECT_TEAMS_NAME_TOKEN_QUERY)
        result = curs.fetchall()

    print('\n'.join(f"{name}:{token}" for name, token in result))


if __name__ == '__main__':
    run()
