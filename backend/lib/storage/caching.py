from redis.client import Pipeline

from lib import models
from lib.storage import utils, game

_SELECT_LAST_STOLEN_TEAM_FLAGS_QUERY = """
SELECT f.id FROM stolenflags sf
JOIN flags f on f.id = sf.flag_id 
WHERE sf.attacker_id = %(attacker_id)s AND f.round >= %(round)s
"""

_SELECT_ALL_LAST_FLAGS_QUERY = "SELECT * from flags WHERE round >= %(round)s"


def cache_teams(pipe: Pipeline) -> None:
    """
    Put "teams" table data from database to cache.

    Just adds commands to pipeline stack, don't forget to execute afterwards.
    """
    with utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(models.Team.get_select_active_query())
        teams = curs.fetchall()

    teams = list(models.Team.from_dict(team) for team in teams)

    pipe.delete('teams')
    if teams:
        pipe.sadd('teams', *[team.to_json() for team in teams])
    for team in teams:
        pipe.set(f'team:token:{team.token}', team.id)


def cache_tasks(pipe: Pipeline) -> None:
    """
    Put active tasks table data from database to cache.

    Just adds commands to pipeline stack don't forget to execute afterwards.
    """
    with utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(models.Task.get_select_active_query())
        tasks = curs.fetchall()

    tasks = list(models.Task.from_dict(task) for task in tasks)
    pipe.delete('tasks')
    if tasks:
        pipe.sadd('tasks', *[task.to_json() for task in tasks])


def cache_last_stolen(team_id: int, current_round: int, pipe: Pipeline) -> None:
    """
    Caches stolen flags from "flag_lifetime" rounds.

    Just adds commands to pipeline stack, don't forget to execute afterwards.

    :param team_id: attacker team id
    :param current_round: current round
    :param pipe: redis connection to add command to
    """
    game_config = game.get_current_global_config()

    with utils.db_cursor() as (_, curs):
        curs.execute(
            _SELECT_LAST_STOLEN_TEAM_FLAGS_QUERY,
            {
                'round': current_round - game_config.flag_lifetime,
                'attacker_id': team_id,
            },
        )
        flags = curs.fetchall()

    pipe.delete(f'team:{team_id}:stolen_flags')
    if flags:
        pipe.sadd(
            f'team:{team_id}:stolen_flags',
            *(flag[0] for flag in flags),
        )


def cache_last_flags(current_round: int, pipe: Pipeline) -> None:
    """
    Cache all generated flags from last "flag_lifetime" rounds.

    Just adds commands to pipeline stack, don't forget to execute afterwards.

    :param current_round: current round
    :param pipe: redis connection to add command to
    """
    game_config = game.get_current_global_config()
    expires = game_config.flag_lifetime * game_config.round_time * 2

    with utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(
            _SELECT_ALL_LAST_FLAGS_QUERY,
            {'round': current_round - game_config.flag_lifetime},
        )
        flags = curs.fetchall()

    flag_models = list(models.Flag.from_dict(data) for data in flags)

    pipe.set('flags:cached', 1)
    for flag in flag_models:
        pipe.set(f'flag:id:{flag.id}', flag.to_json(), ex=expires)
        pipe.set(f'flag:str:{flag.flag}', flag.to_json(), ex=expires)


def cache_global_config(pipe: Pipeline) -> None:
    """Put global config to cache (without round or game_running)."""
    global_config = game.get_db_global_config()
    data = global_config.to_json()
    pipe.set('global_config', data)


def flush_teams_cache():
    with utils.redis_pipeline(transaction=False) as pipe:
        pipe.delete('teams').execute()


def flush_tasks_cache():
    with utils.redis_pipeline(transaction=False) as pipe:
        pipe.delete('tasks').execute()
