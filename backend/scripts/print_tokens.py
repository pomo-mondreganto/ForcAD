#!/usr/bin/env python3

from lib import storage

_SELECT_TEAMS_NAME_TOKEN_QUERY = "SELECT name, token from Teams"


def run():
    with storage.utils.db_cursor() as (_, curs):
        curs.execute(_SELECT_TEAMS_NAME_TOKEN_QUERY)
        result = curs.fetchall()

    print('\n'.join(f"{name}:{token}" for name, token in result))


if __name__ == '__main__':
    run()
