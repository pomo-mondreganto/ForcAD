#!/usr/bin/env python3

import os
from pathlib import Path

import pytz
import yaml

from lib import models
from lib import storage

BASE_DIR = Path(__file__).resolve().absolute().parents[1]
CONFIG_DIR = BASE_DIR / 'config'
CONFIG_FILENAME = 'config.yml'

if os.environ.get('TEST'):
    CONFIG_FILENAME = 'test_config.yml'

SCRIPTS_DIR = BASE_DIR / 'scripts'


def init_schema(curs):
    create_tables_path = SCRIPTS_DIR / 'create_tables.sql'
    create_tables_query = create_tables_path.read_text()
    curs.execute(create_tables_query)

    create_functions_path = SCRIPTS_DIR / 'create_functions.sql'
    create_functions_query = create_functions_path.read_text()
    curs.execute(create_functions_query)


def init_teams(config, curs):
    teams = []

    team_defaults = {
        'highlighted': False,
        'active': True,
    }

    for team_conf in config:
        for k, v in team_defaults.items():
            if k not in team_conf:
                team_conf[k] = v

        team_token = models.Team.generate_token()
        team = models.Team(id=None, **team_conf, token=team_token)
        curs.execute(team.get_insert_query(), team.to_dict())
        team.id, = curs.fetchone()
        teams.append(team)

    return teams


def init_tasks(config, global_config, curs):
    task_defaults = {
        'env_path': global_config['env_path'],
        'default_score': global_config['default_score'],
        'get_period': global_config.get('get_period',
                                        global_config['round_time']),
        'checker_type': 'hackerdom',
        'active': True,
    }

    tasks = []

    for task_conf in config:
        for k, v in task_defaults.items():
            if k not in task_conf:
                task_conf[k] = v

        task_conf['checker'] = str(
            Path(
                global_config['checkers_path']
            ).joinpath(
                task_conf['checker'],
            )
        )

        task = models.Task(id=None, **task_conf)
        curs.execute(task.get_insert_query(), task.to_dict())
        task.id, = curs.fetchone()
        tasks.append(task)

    return tasks


def init_global_config(global_config, curs):
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


def init_game_state():
    game_state = storage.game.construct_game_state_from_db(current_round=0)
    with storage.utils.get_redis_storage().pipeline(
            transaction=True) as pipeline:
        pipeline.set('game_state', game_state.to_json())
        pipeline.execute()

    storage.utils.get_wro_sio_manager().emit(
        event='update_scoreboard',
        data={'data': game_state.to_dict()},
        namespace='/game_events',
    )


def run():
    conf_path = CONFIG_DIR / CONFIG_FILENAME
    with conf_path.open(mode='r') as f:
        file_config = yaml.safe_load(f)

    with storage.utils.db_cursor() as (conn, curs):
        init_schema(curs)

        teams = init_teams(file_config['teams'], curs)

        global_defaults = {
            'checkers_path': '/checkers/',
            'env_path': '/checkers/bin/',
            'default_score': 2000.0,
            'game_hardness': 10.0,
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

        tasks = init_tasks(file_config['tasks'], global_config, curs)

        data = [
            (task.id, team.id, task.default_score, -1)
            for team in teams
            for task in tasks
        ]
        curs.executemany(storage.tasks.TEAMTASK_INSERT_QUERY, data)

        init_global_config(global_config, curs)

        conn.commit()

    init_game_state()


if __name__ == '__main__':
    run()
