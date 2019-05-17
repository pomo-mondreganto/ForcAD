import os
import secrets
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import config

from helpers import models

SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')


def run():
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    create_query_path = os.path.join(SCRIPTS_DIR, 'create_query.sql')
    create_query = open(create_query_path, 'r').read()
    curs.execute(create_query)

    query = 'INSERT INTO globalconfig (real_round, game_running) VALUES (%s, %s)'
    curs.execute(query, (0, 0))

    teams_config = config.get_teams_config()
    teams = []

    for team_conf in teams_config:
        team_token = secrets.token_hex(8)
        team = models.Team(id=None, **team_conf, token=team_token)
        query = 'INSERT INTO Teams (name, ip, token) VALUES (%s, %s, %s) RETURNING id'
        curs.execute(query, (team.name, team.ip, team_token))
        team.id, = curs.fetchone()
        teams.append(team)

    tasks_config = config.get_tasks_config()
    tasks = []

    game_config = config.get_game_config()
    global_env_path = game_config['env_path']
    checkers_path = game_config['checkers_path']
    global_default_score = game_config['default_score']

    for task_conf in tasks_config:
        if 'env_path' not in task_conf:
            task_conf['env_path'] = global_env_path

        if 'default_score' not in task_conf:
            task_conf['default_score'] = global_default_score

        task_conf['checker'] = os.path.join(checkers_path, task_conf['checker'])

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

    for team in teams:
        for task in tasks:
            query = "INSERT INTO TeamTasks (task_id, team_id, round, score, status) VALUES (%s, %s, %s, %s, %s)"
            curs.execute(query, (task.id, team.id, 0, task.default_score, -1))

    conn.commit()
    curs.close()
    storage.get_db_pool().putconn(conn)


if __name__ == '__main__':
    run()
