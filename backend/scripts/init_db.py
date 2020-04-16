#!/usr/bin/env python3

import os

import pytz
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import yaml

from helplib import models

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CONFIG_FILENAME = 'config.yml'

if os.environ.get('TEST'):
    CONFIG_FILENAME = 'test_config.yml'

SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')


def run():
    conf_path = os.path.join(CONFIG_DIR, CONFIG_FILENAME)
    with open(conf_path) as f:
        file_config = yaml.load(f, Loader=yaml.FullLoader)

    with storage.db_cursor() as (conn, curs):
        create_tables_path = os.path.join(SCRIPTS_DIR, 'create_tables.sql')
        with open(create_tables_path) as f:
            create_tables_query = f.read()
        curs.execute(create_tables_query)

        create_functions_path = os.path.join(
            SCRIPTS_DIR,
            'create_functions.sql',
        )
        with open(create_functions_path) as f:
            create_functions_query = f.read()
        curs.execute(create_functions_query)

        teams_config = file_config['teams']
        teams = []

        team_defaults = {
            'highlighted': False,
            'active': True,
        }

        for team_conf in teams_config:
            for k, v in team_defaults.items():
                if k not in team_conf:
                    team_conf[k] = v

            team_token = models.Team.generate_token()
            team = models.Team(id=None, **team_conf, token=team_token)
            curs.execute(team.get_insert_query(), team.to_dict())
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
            'game_mode': 'classic',
        }

        global_config = file_config['global']
        for k, v in global_defaults.items():
            if k not in global_config:
                global_defaults[k] = v

        task_defaults = {
            'env_path': global_config['env_path'],
            'default_score': global_config['default_score'],
            'get_period': global_config.get('get_period',
                                            global_config['round_time']),
            'checker_type': 'hackerdom',
            'active': True,
        }

        for task_conf in tasks_config:
            for k, v in task_defaults.items():
                if k not in task_conf:
                    task_conf[k] = v

            task_conf['checker'] = os.path.join(global_config['checkers_path'],
                                                task_conf['checker'])

            task = models.Task(id=None, **task_conf)
            curs.execute(task.get_insert_query(), task.to_dict())
            task.id, = curs.fetchone()
            tasks.append(task)

        data = [
            (task.id, team.id, task.default_score, -1)
            for team in teams
            for task in tasks
        ]

        curs.executemany(storage.tasks.TEAMTASK_INSERT_QUERY, data)

        global_config.pop('env_path', None)
        global_config.pop('default_score', None)
        global_config.pop('checkers_path', None)
        global_config.pop('get_period', None)

        tz = pytz.timezone(global_config['timezone'])
        global_config['start_time'] = tz.localize(global_config['start_time'])

        global_config['real_round'] = 0
        global_config['game_running'] = False

        global_config = models.GlobalConfig(id=None, **global_config)
        curs.execute(global_config.get_insert_query(), global_config.to_dict())

        conn.commit()

    game_state = storage.game.construct_game_state_from_db(round=0)
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.set('game_state', game_state.to_json())
        pipeline.execute()

    storage.get_wro_sio_manager().emit(
        event='update_scoreboard',
        data={'data': game_state.to_dict()},
        namespace='/game_events',
    )


if __name__ == '__main__':
    run()
