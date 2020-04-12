import time
from typing import Optional

import storage
from helplib import models
from helplib.cache import cache_helper, async_cache_helper
from storage import caching

_CURRENT_REAL_ROUND_QUERY = 'SELECT real_round FROM globalconfig WHERE id=1'

_UPDATE_REAL_ROUND_QUERY = 'UPDATE globalconfig SET real_round = %s WHERE id=1'

_SET_GAME_RUNNING_QUERY = 'UPDATE globalconfig SET game_running = %s WHERE id=1'

_GET_GAME_RUNNING_QUERY = 'SELECT game_running FROM globalconfig WHERE id=1'

_GET_GLOBAL_CONFIG_QUERY = 'SELECT * FROM globalconfig WHERE id=1'


def get_round_start(round: int) -> int:
    """Get start time for round as unix timestamp"""
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        start_time, = pipeline.get(f'round:{round}:start_time').execute()
    try:
        start_time = int(start_time)
    except (ValueError, TypeError):
        start_time = 0
    return start_time


def set_round_start(round: int):
    """Set start time for round as str"""
    cur_time = int(time.time())
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        pipeline.set(f'round:{round}:start_time', cur_time).execute()


def get_real_round() -> int:
    """Get real round of system (for flag submitting),
    returns -1 if round not in cache
    """
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        round, = pipeline.get('real_round').execute()

    try:
        round = int(round)
    except (ValueError, TypeError):
        return -1
    return round


def get_real_round_from_db() -> int:
    """Get real round from database
        Fully persistent to use with game management"""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_CURRENT_REAL_ROUND_QUERY)
        round, = curs.fetchone()

    return round


def update_real_round_in_db(new_round: int):
    """Update real round stored in DB"""

    with storage.db_cursor() as (conn, curs):
        curs.execute(_UPDATE_REAL_ROUND_QUERY, (new_round,))
        conn.commit()


def set_game_running(new_value: bool):
    """Update game_running value in db"""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_SET_GAME_RUNNING_QUERY, (new_value,))
        conn.commit()


def get_game_running() -> bool:
    """Update game_running value in db"""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_GET_GAME_RUNNING_QUERY)
        game_running, = curs.fetchone()

    return game_running


def get_db_global_config() -> models.GlobalConfig:
    """Get global config from database as it is"""
    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_GET_GLOBAL_CONFIG_QUERY)
        result = curs.fetchone()

    return models.GlobalConfig.from_dict(result)


def get_current_global_config() -> models.GlobalConfig:
    """Get global config from cache is cached, otherwise cache it"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cache_helper(
            pipeline=pipeline,
            cache_key='global_config:cached',
            cache_func=storage.caching.cache_global_config,
            cache_args=(pipeline,),
        )

        result, = pipeline.get('global_config').execute()
        global_config = models.GlobalConfig.from_json(result)

    return global_config


async def global_config_async_getter(redis_aio, pipe):
    """Async version of get_current_global_config"""
    await async_cache_helper(
        redis_aio=redis_aio,
        cache_key='global_config:cached',
        cache_func=caching.cache_global_config,
    )
    pipe.get('global_config')


def construct_game_state_from_db(round: int) -> Optional[models.GameState]:
    """Get game state for specified round with teamtasks from db"""
    teamtasks = storage.tasks.get_teamtasks_from_db()
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)

    round_start = get_round_start(round)
    state = models.GameState(round_start=round_start, round=round, team_tasks=teamtasks)
    return state


def construct_latest_game_state(round: int) -> Optional[models.GameState]:
    """Get game state from latest teamtasks from redis stream"""
    teamtasks = storage.tasks.get_last_teamtasks()
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)

    round_start = get_round_start(round)
    state = models.GameState(round_start=round_start, round=round, team_tasks=teamtasks)
    return state


def game_state_getter(pipe):
    """Get game state for current round (asynchronous version)"""
    pipe.get('game_state')


async def get_attack_data(loop) -> str:
    """Get public flag ids for task that provide them"""
    redis_pool = await storage.get_async_redis_storage(loop)
    attack_data = await redis_pool.get('attack_data')
    return attack_data
