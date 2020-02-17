#!/usr/bin/env python3

import os
import secrets

import pytz
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import config

from helplib import models

SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# noinspection 
_CONFIG_INITIALIZATION_QUERY = '''INSERT INTO globalconfig ({columns}) VALUES ({values}) RETURNING id'''

_TEAM_INSERT_QUERY = 'INSERT INTO Teams (name, ip, token) VALUES (%s, %s, %s) RETURNING id'

_TASK_INSERT_QUERY = '''
INSERT INTO Tasks 
(name, checker, gets, puts, places, checker_timeout, env_path, checker_returns_flag_id, gevent_optimized, get_period) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
'''

_TEAMTASK_INSERT_QUERY = "INSERT INTO TeamTasks (task_id, team_id, round, score, status) VALUES (%s, %s, %s, %s, %s)"

_SET_TIMEZONE_QUERY = "SET TIME ZONE %s"


def run():
    with storage.db_cursor() as (conn, curs):
        file_config = config.AppConfig.get_main_config()

        create_query_path = os.path.join(SCRIPTS_DIR, 'create_query.sql')
        create_query = open(create_query_path).read()
        curs.execute(create_query)

        teams_config = file_config['teams']
        teams = []

        for team_conf in teams_config:
            team_token = secrets.token_hex(8)
            team = models.Team(id=None, **team_conf, token=team_token)
            curs.execute(_TEAM_INSERT_QUERY, (team.name, team.ip, team_token))
            team.id, = curs.fetchone()
            teams.append(team)

        tasks_config = file_config['tasks']
        tasks = []

        global_defaults = {
            'checkers_path': '/checkers/',
            'env_path': '/checkers/bin/',
            'default_score': 2000.0,
            'game_hardness': 3000.0,
            'inflation': True,
            'flag_lifetime': 5,
            'round_time': 60,
            'timezone': 'UTC',
        }

        global_config = file_config['global']
        for k, v in global_defaults.items():
            if k not in global_config:
                global_defaults[k] = v

        task_defaults = {
            'env_path': global_config['env_path'],
            'default_score': global_config['default_score'],
            'get_period': global_config.get('get_period', global_config['round_time']),
            'checker_returns_flag_id': True,
            'gevent_optimized': False,
        }

        for task_conf in tasks_config:
            for k, v in task_defaults.items():
                if k not in task_conf:
                    task_conf[k] = v

            task_conf['checker'] = os.path.join(global_config['checkers_path'], task_conf['checker'])

            task = models.Task(id=None, **task_conf)
            curs.execute(
                _TASK_INSERT_QUERY,
                (
                    task.name,
                    task.checker,
                    task.gets,
                    task.puts,
                    task.places,
                    task.checker_timeout,
                    task.env_path,
                    task.checker_returns_flag_id,
                    task.gevent_optimized,
                    task.get_period,
                )
            )
            task.id, = curs.fetchone()
            tasks.append(task)

        data = [
            (task.id, team.id, 0, task.default_score, -1)
            for team in teams
            for task in tasks
        ]

        curs.executemany(_TEAMTASK_INSERT_QUERY, data)

        global_config.pop('env_path', None)
        global_config.pop('default_score', None)
        global_config.pop('checkers_path', None)
        global_config.pop('get_period', None)

        tz = pytz.timezone(global_config['timezone'])
        global_config['start_time'] = tz.localize(global_config['start_time'])

        keys = global_config.keys()
        columns = ','.join(keys)
        values = ','.join(f'%({key})s' for key in keys)
        curs.execute(
            _CONFIG_INITIALIZATION_QUERY.format(columns=columns, values=values),
            global_config,
        )

        conn.commit()

    storage.caching.cache_teamtasks(round=0)
    game_state = storage.game.construct_game_state(round=0)
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.set('game_state', game_state.to_json())
        pipeline.publish('scoreboard', game_state.to_json())
        pipeline.execute()


if __name__ == '__main__':
    run()
