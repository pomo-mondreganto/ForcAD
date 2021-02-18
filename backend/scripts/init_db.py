#!/usr/bin/env python3

import os
from pathlib import Path

import pytz
import yaml

from lib import models
from lib import storage

BACKEND_BASE = Path(__file__).resolve().absolute().parents[1]
SCRIPTS_DIR = BACKEND_BASE / 'scripts'
CONFIG_PATH = os.getenv('CONFIG_PATH')


def init_schema(curs):
    create_tables_path = SCRIPTS_DIR / 'create_tables.sql'
    create_tables_query = create_tables_path.read_text()
    curs.execute(create_tables_query)

    create_functions_path = SCRIPTS_DIR / 'create_functions.sql'
    create_functions_query = create_functions_path.read_text()
    curs.execute(create_functions_query)


def init_teams(config, curs):
    teams = []

    for team_conf in config:
        team_token = models.Team.generate_token()
        team = models.Team(id=None, **team_conf, token=team_token)
        team.insert(curs)
        teams.append(team)

    return teams


def init_tasks(config, game_config, curs):
    task_defaults = {
        'env_path': game_config['env_path'],
        'default_score': game_config['default_score'],
        'get_period': game_config.get('get_period', game_config['round_time']),
        'checker_type': 'hackerdom',
    }

    tasks = []

    for task_conf in config:
        for k, v in task_defaults.items():
            if k not in task_conf:
                task_conf[k] = v

        task_conf['checker'] = os.path.join(
            game_config['checkers_path'],
            task_conf['checker'],
        )

        task = models.Task(id=None, **task_conf)
        task.insert(curs)
        tasks.append(task)

    return tasks


def init_game_config(game_config, curs):
    game_config.pop('env_path', None)
    game_config.pop('default_score', None)
    game_config.pop('checkers_path', None)
    game_config.pop('get_period', None)

    tz = pytz.timezone(game_config['timezone'])
    game_config['start_time'] = tz.localize(game_config['start_time'])

    game_config['real_round'] = 0
    game_config['game_running'] = False

    # noinspection PyArgumentList
    game_config['mode'] = models.GameMode(game_config['mode'])

    game_config = models.GameConfig(id=None, **game_config)
    game_config.insert(curs)


def run():
    with open(CONFIG_PATH, 'r') as f:
        file_config = yaml.safe_load(f)

    with storage.utils.db_cursor() as (conn, curs):
        print('Initializing schema')
        init_schema(curs)

        print('Initializing teams')
        teams = init_teams(file_config['teams'], curs)

        game_defaults = {
            'checkers_path': '/checkers/',
            'env_path': '/checkers/bin/',
            'default_score': 2000.0,
            'game_hardness': 10.0,
            'inflation': True,
            'flag_lifetime': 5,
            'round_time': 60,
            'timezone': 'UTC',
            'mode': 'classic',
        }

        game_config = file_config['game']
        for k, v in game_defaults.items():
            if k not in game_config:
                game_defaults[k] = v

        print('Initializing tasks')
        tasks = init_tasks(file_config['tasks'], game_config, curs)

        data = [
            {
                'task_id': task.id,
                'team_id': team.id,
                'score': task.default_score,
                'status': -1,
            }
            for team in teams
            for task in tasks
        ]
        curs.executemany(storage.tasks.TEAMTASK_INSERT_QUERY, data)

        print('Initializing game config')
        init_game_config(game_config, curs)

        conn.commit()

    print('Initializing game state')
    storage.game.update_game_state(for_round=0)


if __name__ == '__main__':
    run()
