"""
db.check.py
This script will check whether the postgres container is up and running. It'll
connect to the database with the credentials provided in the environment
variables.
"""

import os
import sys

import psycopg2


def database_check():
    dbname = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOST']
    port = os.environ['POSTGRES_PORT']

    print("HOST: {host}:{port}, DB: {dbname}, USER: {user}".format(
        dbname=dbname,
        user=user,
        host=host,
        port=port))

    # noinspection PyBroadException
    try:
        psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port)
    except:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    database_check()
