import json

import helplib
import storage
from helplib import models

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

_SELECT_TEAMTASKS_BY_ROUND_QUERY = "SELECT * from teamtasks WHERE round = %s ORDER BY id"
_SELECT_TEAMTASKS_FOR_TEAM_WITH_ROUND_QUERY = "SELECT * from teamtasks WHERE team_id = %s AND round <= %s ORDER BY id"


def cache_teams(pipeline):
    """Put "teams" table data from database to cache

    Just adds commands to pipeline stack, don't forget to execute afterwards
    """
    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_SELECT_ALL_TEAMS_QUERY)
        teams = curs.fetchall()

    teams = list(models.Team.from_dict(team) for team in teams)

    pipeline.delete('teams', 'teams:cached')
    if teams:
        pipeline.sadd('teams', *[team.to_json() for team in teams])
    for team in teams:
        pipeline.set(f'team:token:{team.token}', team.id)
    pipeline.set('teams:cached', 1)


async def cache_teams_async(redis):
    """Async version of cache_teams"""
    return cache_teams(redis)


def cache_tasks(pipeline):
    """Put "tasks" table data from database to cache

    Just adds commands to pipeline stack, don't forget to execute afterwards
    """
    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_SELECT_ALL_TASKS_QUERY)
        tasks = curs.fetchall()

    tasks = list(models.Task.from_dict(task) for task in tasks)
    pipeline.delete('tasks', 'tasks:cached')
    if tasks:
        pipeline.sadd('tasks', *[task.to_json() for task in tasks])
    pipeline.set('tasks:cached', 1)


async def cache_tasks_async(redis):
    """Async version of cache_tasks"""
    return cache_tasks(redis)


def cache_last_stolen(team_id: int, round: int, pipeline):
    """Put stolen flags for attacker team from last "flag_lifetime" rounds to cache

        :param team_id: attacker team id
        :param round: current round
        :param pipeline: redis connection to add command to
    Just adds commands to pipeline stack, don't forget to execute afterwards
    """
    game_config = storage.game.get_current_global_config()

    with storage.db_cursor() as (conn, curs):
        curs.execute(_SELECT_LAST_STOLEN_TEAM_FLAGS_QUERY, (round - game_config.flag_lifetime, team_id))
        flags = curs.fetchall()

    pipeline.delete(f'team:{team_id}:cached:stolen', f'team:{team_id}:stolen_flags')
    if flags:
        pipeline.sadd(f'team:{team_id}:stolen_flags', *[flag_id for flag_id, in flags])
    pipeline.set(f'team:{team_id}:cached:stolen', 1)


def cache_last_owned(team_id: int, round: int, pipeline):
    """Put owned flags for team from last "flag_lifetime" rounds to cache

        :param team_id: flag owner team id
        :param round: current round
        :param pipeline: redis connection to add command to

    Just adds commands to pipeline stack, don't forget to execute afterwards
    """
    game_config = storage.game.get_current_global_config()

    with storage.db_cursor() as (conn, curs):
        curs.execute(_SELECT_LAST_TEAM_FLAGS_QUERY, (round - game_config.flag_lifetime, team_id))
        flags = curs.fetchall()

    pipeline.delete(f'team:{team_id}:cached:owned', f'team:{team_id}:owned_flags')
    if flags:
        pipeline.sadd(f'team:{team_id}:owned_flags', *[flag_id for flag_id, in flags])
    pipeline.set(f'team:{team_id}:cached:owned', 1)


def cache_last_flags(round: int, pipeline):
    """Put all generated flags from last "flag_lifetime" rounds to cache

        :param round: current round
        :param pipeline: redis connection to add command to

    Just adds commands to pipeline stack, don't forget to execute afterwards
    """
    game_config = storage.game.get_current_global_config()

    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_SELECT_ALL_LAST_FLAGS_QUERY, (round - game_config.flag_lifetime,))
        flags = curs.fetchall()

    pipeline.delete('flags:cached')
    flag_models = []
    for flag_dict in flags:
        flag = helplib.models.Flag.from_dict(flag_dict)
        flag_models.append(flag)

    if flag_models:
        pipeline.delete(*[f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}' for flag in flag_models])

    for flag in flag_models:
        pipeline.set(f'flag:id:{flag.id}', flag.to_json())
        pipeline.set(f'flag:str:{flag.flag}', flag.to_json())
        pipeline.sadd(f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}', flag.id)

    pipeline.set('flags:cached', 1)


def cache_teamtasks(round: int):
    """Put "teamtasks" table data for the specified round from database to cache"""
    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_SELECT_TEAMTASKS_BY_ROUND_QUERY, (round,))
        results = curs.fetchall()

    data = json.dumps(results)
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.set(f'teamtasks:{round}', data)
        pipeline.set(f'teamtasks:{round}:cached', 1)
        pipeline.execute()


def cache_teamtasks_for_team(team_id: int, current_round: int, pipeline):
    """Put "teamtasks" for specified team table data for the specified round from database to cache

        :param team_id: team id
        :param current_round: round to cache
        :param pipeline: redis connection to add command to
    """
    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(
            _SELECT_TEAMTASKS_FOR_TEAM_WITH_ROUND_QUERY,
            (
                team_id,
                current_round,
            )
        )
        results = curs.fetchall()

    data = json.dumps(results)
    pipeline.set(f'teamtasks:team:{team_id}:round:{current_round}', data)
    pipeline.set(f'teamtasks:team:{team_id}:round:{current_round}:cached', 1)


def cache_global_config(pipeline):
    """Put global config to cache (without round or game_running)"""
    global_config = storage.game.get_db_global_config()
    data = global_config.to_json()
    pipeline.set('global_config', data)
    pipeline.set('global_config:cached', data)
