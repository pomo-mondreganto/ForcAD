import json

from psycopg2 import extras

import config
import helpers.models
import storage
from helpers import models

_SELECT_ALL_TEAMS_QUERY = "SELECT * FROM teams"

_SELECT_ALL_TASKS_QUERY = "SELECT * FROM tasks"

_SELECT_LAST_STOLEN_TEAM_FLAGS_QUERY = """
WITH flag_ids AS (
    SELECT id FROM flags WHERE  round >= %s
)
SELECT flag_id FROM stolenflags 
WHERE flag_id IN (SELECT id from flag_ids) AND attacker_id = %s
"""

_SELECT_LAST_TEAM_FLAGS_QUERY = "SELECT id from flags WHERE round >= %s AND team_id = %s"

_SELECT_ALL_LAST_FLAGS_QUERY = "SELECT * from flags WHERE round >= %s"

_SELECT_TEAMTASKS_BY_ROUND_QUERY = "SELECT * from teamtasks WHERE round = %s"


def cache_teams():
    """Put "teams" table data from database to cache"""
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor(cursor_factory=extras.DictCursor)
    curs.execute(_SELECT_ALL_TEAMS_QUERY)

    teams = curs.fetchall()
    curs.close()
    storage.get_db_pool().putconn(conn)

    teams = list(models.Team.from_dict(team) for team in teams)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete('teams', 'teams:cached')
        for team in teams:
            pipeline.sadd('teams', team.to_json())
            pipeline.set(f'team:token:{team.token}', team.id)
        pipeline.set('teams:cached', 1)
        pipeline.execute()


def cache_tasks():
    """Put "tasks" table data from database to cache"""
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor(cursor_factory=extras.DictCursor)
    curs.execute(_SELECT_ALL_TASKS_QUERY)

    tasks = curs.fetchall()
    curs.close()
    storage.get_db_pool().putconn(conn)

    tasks = list(models.Task.from_dict(task) for task in tasks)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete('tasks', 'tasks:cached')
        for task in tasks:
            pipeline.sadd('tasks', task.to_json())
        pipeline.set('tasks:cached', 1)
        pipeline.execute()


def cache_last_stolen(team_id: int, round: int):
    """Put stolen flags for attacker team from last "flag_lifetime" rounds to cache

        :param team_id: attacker team id
        :param round: current round
    """
    game_config = config.get_game_config()
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    curs.execute(_SELECT_LAST_STOLEN_TEAM_FLAGS_QUERY, (round - game_config['flag_lifetime'], team_id))

    flags = curs.fetchall()
    curs.close()
    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete(f'team:{team_id}:cached_stolen', f'team:{team_id}:stolen_flags')
        for flag_id, in flags:
            pipeline.sadd(f'team:{team_id}:stolen_flags', flag_id)
        pipeline.set(f'team:{team_id}:cached_stolen', 1)
        pipeline.execute()


def cache_last_owned(team_id: int, round: int):
    """Put owned flags for team from last "flag_lifetime" rounds to cache

        :param team_id: flag owner team id
        :param round: current round
    """
    game_config = config.get_game_config()

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    curs.execute(_SELECT_LAST_TEAM_FLAGS_QUERY, (round - game_config['flag_lifetime'], team_id))

    flags = curs.fetchall()
    curs.close()
    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete(f'team:{team_id}:owned_flags', f'team:{team_id}:cached_owned')
        for flag_id, in flags:
            pipeline.sadd(f'team:{team_id}:owned_flags', flag_id)
        pipeline.set(f'team:{team_id}:cached_owned', 1)
        pipeline.execute()


def cache_last_flags(round: int):
    """Put all generated flags from last "flag_lifetime" rounds to cache

            :param round: current round
    """
    game_config = config.get_game_config()
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor(cursor_factory=extras.DictCursor)

    curs.execute(_SELECT_ALL_LAST_FLAGS_QUERY, (round - game_config['flag_lifetime'],))

    flags = curs.fetchall()
    curs.close()
    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete('flags:cached')
        flag_models = []
        for flag_dict in flags:
            flag = helpers.models.Flag.from_dict(flag_dict)
            flag_models.append(flag)
            pipeline.delete(f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}')

        for flag in flag_models:
            pipeline.set(f'flag:id:{flag.id}', flag.to_json())
            pipeline.set(f'flag:str:{flag.flag}', flag.to_json())
            pipeline.sadd(f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}', flag.id)

        pipeline.set(f'flags:cached', 1)
        pipeline.execute()


def cache_teamtasks(round: int):
    """Put "teamtasks" table data for the specified round from database to cache
        :param round: round to cache

        This function caches full game state for specified round
    """
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor(cursor_factory=extras.RealDictCursor)

    curs.execute(_SELECT_TEAMTASKS_BY_ROUND_QUERY, (round,))

    results = curs.fetchall()
    curs.close()
    storage.get_db_pool().putconn(conn)

    data = json.dumps(results)
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.set(f'teamtasks:{round}', data)
        pipeline.set(f'teamtasks:{round}:cached', 1)
        pipeline.execute()
