import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import config

from helpers import models


def run():
    query = '''
    CREATE TABLE IF NOT EXISTS Teams(
        id SERIAL PRIMARY KEY,
        name varchar(255) not null default '',
        ip inet
    )'''

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    curs.execute(query)

    teams_config = config.get_teams_config()
    teams = []

    for team_conf in teams_config:
        team = models.Team(id=None, **team_conf)
        query = 'INSERT INTO Teams (name, ip) VALUES (%s, %s) RETURNING id'
        curs.execute(query, (team.name, team.ip))
        team.id, = curs.fetchone()
        teams.append(team)

    query = '''
    CREATE TABLE IF NOT EXISTS Flags(
        id SERIAL PRIMARY KEY,
        flag varchar(32) not null default '',
        team_id INTEGER NOT NULL,
        task_id INTEGER NOT NULL,
        round INTEGER NOT NULL,
        flag_data varchar(255) NOT NULL
    )'''

    curs.execute(query)

    query = '''
    CREATE TABLE IF NOT EXISTS StolenFlags(
        id SERIAL PRIMARY KEY,
        flag_id INTEGER NOT NULL,
        attacker_id INTEGER NOT NULL
    )'''

    curs.execute(query)

    query = '''
    CREATE TABLE IF NOT EXISTS Tasks(
        id SERIAL PRIMARY KEY,
        name varchar(255),
        checker varchar(1024),
        env_path varchar(1024),
        gets INTEGER,
        puts INTEGER,
        places INTEGER,
        checker_timeout INTEGER
    )'''

    curs.execute(query)

    tasks_config = config.get_game_config()['tasks']
    tasks = []

    for task_conf in tasks_config:
        task = models.Task(id=None, **task_conf)
        query = (
            "INSERT INTO Tasks (name, checker, gets, puts, places, checker_timeout, env_path) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"
        )
        curs.execute(
            query,
            (
                task.name,
                task.checker,
                task.gets,
                task.puts,
                task.places,
                task.checker_timeout,
                task.env_path,
            )
        )
        task.id, = curs.fetchone()
        tasks.append(task)

    query = '''
    CREATE TABLE IF NOT EXISTS TeamTasks(
        id SERIAL PRIMARY KEY,
        task_id INTEGER,
        team_id INTEGER,
        status INTEGER,
        message varchar(1024) NOT NULL DEFAULT ''
    )'''

    curs.execute(query)

    for team in teams:
        for task in tasks:
            query = "INSERT INTO TeamTasks (task_id, team_id) VALUES (%s, %s)"
            curs.execute(query, (task.id, team.id))

    conn.commit()

    storage.get_db_pool().putconn(conn)


if __name__ == '__main__':
    run()
